import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import StripePattern, CirclePattern
from streamlit_folium import folium_static
import geopandas as gpd

from src.pages.utils import aggregate_df, filter_by_dates
from src.constants import data_districts_path, district_cols, districts_names, geojson_path, map_defaults

def app():
    st.subheader("Configurationes Mapa")
    df = pd.read_feather(data_districts_path)
    st.markdown("A continuación, puede especificar qué variables desea que procese el mapa. Recuerda al escribirlos que todos **comienzan con mayúscula** y el resto en minúsculas (excepto *'PESO'*). Si el nombre no está bien especificado, generará un error.")
    chosen_cols = st_tags(
        label='Variables de distrito para mostrar en el mapa (la primera determinará los colores de relleno del mapa):',
        text='Presiona enter para añadir más',
        value=district_cols[:4],
        suggestions=district_cols,
        maxtags=len(district_cols),
        key='dist_cols')
    highlit_cols = st_tags(
        label='District Vars para segregar el mapa (permite un máximo de 3 variables):',
        text='Presiona enter para añadir más',
        value=["Rent_Bruta_Per_Cápita", "Densidad(hab./Ha.)"],
        suggestions=district_cols,
        maxtags=3,
        key='seg_cols')
    config_container = st.container()
    # filter map by range of dates
    filter_level = "day" if chosen_cols[0] == "PESO" else "year"
    col1, col2, *cols_dates = st.columns([0.3, 0.2, 0.4]) if filter_level=="day" else st.columns([0.25,0.25,0.15,0.35])
    df_filtered = filter_by_dates(df, cols_dates, level=filter_level)
    # create aggregated df with selected operation
    agg_df = aggregate_df(df_filtered, "Distrito", district_cols, selection_data = {"container": col1, "options": ["Mean", "Std dev"]})
    # add map configurations for the variables to seggregate if any
    config_segcols = {c: {} for c in highlit_cols}
    if len(highlit_cols)>0:
        c1, c2, c3, c4 = config_container.columns([0.4, 0.2, 0.2, 0.2])
        c1.markdown("<h6 style='text-align: center;'>District variables to seggregate</h1>", unsafe_allow_html=True)
        c2.markdown("**Figura tipos**")
        c3.markdown("**Color tipos**")
        c4.markdown("**Valor para segregar**")
        c1.write("");c4.write("")
        for c, mdef in zip(highlit_cols, map_defaults):
            c1.write(""); c3.write(""); #black spaces
            c1.markdown(f"<h6 style='text-align: center;'>{c}</h1>", unsafe_allow_html=True)
            config_segcols[c]["fig"] = c2.radio('', ["Lines", "Circles"], mdef[0], key="rad_"+c)
            config_segcols[c]["col"] = c3.color_picker('', mdef[1], key="col_"+c)
            config_segcols[c]["val"] = c4.slider(
                '', float(agg_df[c].min()), float(agg_df[c].max()), float(agg_df[c].mean()), key="val_"+c)
            c1.write(" ");c1.write(" ");c1.write(" ")
    fill_colors = col2.radio("Seleccione un conjunto de colores de relleno", options = ["YlGn", "YlGnBu", "BuPu"])
    # filter df by columns chosen and columns to segregate
    total = chosen_cols # creating an oredered set from the two lists
    [total.append(c) for c in highlit_cols if c not in chosen_cols]
    agg_df = agg_df[["Distrito"]+total]
    # display map with the prepared df and configurations
    st.subheader("Madrid Mapa de Distritos")
    m = create_map(agg_df, highlit_cols, config_segcols, fill_colors)
    folium_static(m,  width=1100, height=750)
    
    st.subheader("Análisis de variables por distrito")
    c1, empty, c2, c3, c4 = st.columns([0.35, 0.1, 0.15,0.2,0.2])
    empty.empty()  # let some margin between c1 and c2
    col_name = c1.selectbox("Selecciona variable", district_cols)
    c1.write(" ") #blank space
    show_boxplot = c1.checkbox("Mostrar diagrama de caja con datos agregados")
    # filter df by selected years
    df = filter_by_dates(df, [c2, c3], level="year")
    # create aggregated df with selected operation
    df = aggregate_df(df, "Distrito", district_cols, selection_data={"container": c4, "key":"operation_distvars"})
    col_name = "size" if st.session_state["operation_distvars"] == "Count" else col_name
    # convert district ids to district names
    df["Distrito"] = df["Distrito"].apply(lambda x: districts_names[x-1])
    # bar plot to observe agg data about a selected district variable
    if show_boxplot:
        c1, c2 = st.columns(2)
        fig = px.bar(df, x="Distrito", y=col_name)
        c1.plotly_chart(fig, use_container_width=True, title="Comparación distritos")
        # box plot of the selected district variable
        fig = px.box(df, y=col_name, points="all")
        c2.plotly_chart(fig, use_container_width=True)
    else:
        fig = px.bar(df, x="Distrito", y=col_name)
        st.plotly_chart(fig, use_container_width=True, title="District comparison")
    # display data if desired
    exp = st.expander("Mostrar datos para observar los valores de las variables para cada distrito")
    exp.write(df)
    # display boxplots comparing variance for each district variable
    if st.session_state["operation_distvars"] != "Count":
        df_norm = {}
        for c in district_cols:  # standarize all variables to allow the comparison
            df_norm[c] = (df[c] - df[c].mean())/df[c].std(ddof=0)
        districts_concat = pd.DataFrame(pd.concat([df_norm[c] for c in district_cols]), columns=["value"])
        districts_concat["var"] = [i for c in district_cols for i in [c]*len(df["Distrito"].unique())]
        fig = px.box(districts_concat, x="var", y="value", title="Comparación de variables de distrito estandarizadas")
        st.plotly_chart(fig, use_container_width=True)
        

def create_map(df_map, seg_cols, config_segcols, fill_colors):
    # references: https://towardsdatascience.com/how-to-step-up-your-folium-choropleth-map-skills-17cf6de7c6fe
    geoJSON_df = gpd.read_file(geojson_path)  # create map df
    geoJSON_df = geoJSON_df[["cartodb_id", "name", "geometry"]]
    # rename column from name to Distrito in the geoJSON_df to merge the two dfs.
    geoJSON_df = geoJSON_df.rename(columns={"cartodb_id": "Distrito"})
    # merge sample data df and geoJSON df
    df = geoJSON_df.merge(df_map, on="Distrito")
    df = df.drop(seg_cols, axis=1)
    field_cols = ["name", ]+list(df.columns[3:])

    # set up choropleth map
    m = folium.Map(location=[40.47, -3.7], zoom_start=10.5)
    folium.Choropleth(
        geo_data=df.iloc[:, :4],
        name=field_cols[1],
        data=df.iloc[:, :4],
        columns=["Distrito", field_cols[1]],
        key_on="feature.properties.Distrito",
        fill_color=fill_colors,
        fill_opacity=1,
        line_opacity=0.2,
        legend_name=field_cols[1],
        smooth_factor=0,
        Highlight=True,
        line_color="#0000",
        show=True,
        overlay=True,
        nan_fill_color="White"
    ).add_to(m)
    
    # Add hover functionality.
    def style_function(x): return {'fillColor': '#ffffff',
                                    'color': '#000000',
                                    'fillOpacity': 0.1,
                                    'weight': 0.1}

    def highlight_function(x): return {'fillColor': '#000000',
                                        'color': '#000000',
                                        'fillOpacity': 0.50,
                                        'weight': 0.1}
    NIL = folium.features.GeoJson(
        data=df,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=field_cols,
            aliases=field_cols,
            style=(
                "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )
    m.add_child(NIL)
    m.keep_in_front(NIL)
    def cross_hatching_helper(config_segcols, c, add_90):
        segreg_distids = list(df[df_map[c] >= config_segcols[c]["val"]]["Distrito"])
        gdf_segreg = df[df['Distrito'].isin(segreg_distids)]
        add_90 = not add_90 if config_segcols[c]["fig"] == "Lines" else add_90
        return gdf_segreg, config_segcols[c]["col"], 45+90*add_90, add_90
    add_90 = True
    seg_cols = list(config_segcols.keys())
    if len(seg_cols) > 0:
        gdf_segreg, col0, angle0, add_90 = cross_hatching_helper(config_segcols, seg_cols[0], add_90)
        # cross-hatching to display the seggregated district
        if config_segcols[seg_cols[0]]["fig"] == "Lines":  # add pattern
            sp0 = StripePattern(angle=angle0, color=col0,
                                space_color=col0, opacity=1).add_to(m)
        else:
            sp0 = CirclePattern(width=20, height=20, radius=4, weight=2.0,
                                color=col0, fill_color=col0, opacity=1, fill_opacity=1)
        folium.features.GeoJson(name=seg_cols[0]+">="+str(round(config_segcols[seg_cols[0]]["val"], 2)),
                                data=gdf_segreg, style_function=lambda x: {'fillPattern': sp0}, show=True).add_to(m)
    if len(seg_cols) > 1:
        gdf_segreg, col1, angle1, add_90 = cross_hatching_helper(config_segcols, seg_cols[1], add_90)
        if config_segcols[seg_cols[1]]["fig"] == "Lines":  # add pattern
            sp1 = StripePattern(angle=angle1, color=col1, space_color=col1, opacity=1).add_to(m)
        else:
            sp1 = CirclePattern(width=20, height=20, radius=4, weight=2.0,
                                color=col1, fill_color=col1, opacity=1, fill_opacity=1)
        folium.features.GeoJson(name=seg_cols[1]+">="+str(round(config_segcols[seg_cols[1]]["val"], 2)),
                                data=gdf_segreg, style_function=lambda x: {'fillPattern': sp1}, show=True).add_to(m)
    if len(seg_cols) > 2:
        gdf_segreg, col2, angle2, add_90 = cross_hatching_helper(config_segcols, seg_cols[2], add_90)
        if config_segcols[seg_cols[2]]["fig"] == "Lines":  # add pattern
            sp2 = StripePattern(angle=angle2, color=col2,
                                space_color=col2, opacity=1).add_to(m)
        else:
            sp2 = CirclePattern(width=20, height=20, radius=4, weight=2.0,
                                color=col2, fill_color=col2, opacity=1, fill_opacity=1)
        folium.features.GeoJson(name=seg_cols[2]+">="+str(round(config_segcols[seg_cols[2]]["val"], 2)),
                                data=gdf_segreg, style_function=lambda x: {'fillPattern': sp2}, show=True).add_to(m)
    # add dark and light mode.
    folium.TileLayer('cartodbdark_matter', name="dark mode",
                    control=True).add_to(m)
    folium.TileLayer('cartodbpositron', name="light mode",
                    control=True).add_to(m)
    # add a layer controller
    folium.LayerControl(collapsed=False).add_to(m)
    return m
        
