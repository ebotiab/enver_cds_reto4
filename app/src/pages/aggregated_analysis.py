import plotly.express as px
import streamlit as st
import pandas as pd
import datetime

from src.constants import data_small_path, districts_names, districts_name2id, weekdays, month_names, options_materials
from src.pages.utils import aggregate_df, filter_by_colvalue, filter_by_dates

def show_aggregation(df, variables, operation, cols_distribution=[], tr={}, kwargs={}):
    # cols_distribution can be list of cols dims, if not specif, same length for all cols
    cols_distribution = st.columns(cols_distribution if bool(cols_distribution) else len(variables))
    for col, var_name in zip(cols_distribution, variables):
        grouped_df = aggregate_df(df, var_name, "PESO", operation)
        grouped_df[var_name] = grouped_df[var_name].apply(lambda x: tr[var_name][x]) if (var_name in tr) else grouped_df[var_name]
        fig = px.bar(grouped_df, x=var_name, y='PESO', **kwargs)        
        fig.update_layout(yaxis_title=None)
        if var_name == "Day Anual":
            fig.update_xaxes(dtick="M1",tickformat="%b")
        col.plotly_chart(fig, use_container_width=True)

def app():
    st.title('Análisis agregado respecto la generación de residuos')
    df = pd.read_feather(data_small_path)
    
    # display global configurations
    c1, c2, c3, c4 = st.columns([0.3,0.15,0.2,0.35])
    operation = c1.radio("Selecciona operación para agregar datos", ["Mean", "Sum", "Std dev", "Count"])
    # display global years and months Seleccionaors and set them as bounds in the posterior dates Seleccionaors
    filter_by_dates(df, [c2,c3,c4,c4], level="year_month", filter=False, store_dates=True)
    
    # display aggregations
    st.subheader("Agregado según localización")
    col1, empty, col2 = st.columns([0.25, 0.05, 0.7])
    empty.empty()
    classif_names = ["ALL", ]+list(options_materials.keys())
    df_loc = filter_by_colvalue(df, "Clasificacion", col1, "Selecciona Material", classif_names, options_materials)
    df_loc = filter_by_dates(df_loc, col2, use_stored=True)
    districts_id2name = {v: k for k, v in districts_name2id.items()}
    show_aggregation(df_loc, ["Distrito", "Lote"], operation, [0.65, 0.35], {"Distrito":districts_id2name})
    
    st.subheader("Aggregated por composición de residuos")
    col1, empty, col2 = st.columns([0.25, 0.05, 0.7])
    empty.empty()
    df_mat = filter_by_colvalue(df, "Distrito", col1, "Selecciona District", options=[
                                "ALL", ]+districts_names, transpose=districts_name2id, key="loc1")
    df_mat = filter_by_dates(df_mat, col2, use_stored=True, key="dates2")
    show_aggregation(df_mat, ["Clasificacion", ], operation)
    
    st.subheader("Aggregated por tiempo")
    cols = st.columns(2)
    df_time = filter_by_colvalue(df, "Distrito", cols[0], "Selecciona Distrito", options=[
                                 "ALL", ]+districts_names, transpose=districts_name2id, key="loc2")
    df_time = filter_by_colvalue(df_time, "Clasificacion", cols[1], "Selecciona Material", classif_names, options_materials, key="mat2")
    df_time = filter_by_dates(df_time, st, use_stored=True, key="dates3")
    df_time["date"] =  pd.to_datetime(df_time[['Year', 'Month', 'Day']])
    df_time_serie = aggregate_df(df_time, "date", "PESO", operation=operation)
    st.plotly_chart(px.line(df_time_serie, x="date", y="PESO"), use_container_width=True)
    # remove differences in leap years
    df_time["Day Anual"] = df_time["date"].dt.dayofyear
    df_time.drop(df_time[(df_time["Year"] == 2020) & (df_time["Day Anual"] == 60)].index, inplace=True)
    df_time.loc[(df["Year"] == 2020) & (df_time["Day Anual"] > 60), "Day Anual"] -= 1
    #st.markdown("\**In this plot the differences in 2020 caused by February 29, have been removed*")
    tr_days = {"Day Anual": {d: datetime.datetime(2017, 1, 1) + datetime.timedelta(d-1) for d in range(0, 366)}}
    show_aggregation(df_time, ["Day Anual", ], operation, tr=tr_days, kwargs={"hover_data": {
                     "Day Anual": "|%B %d"}, "title": "In this plot the differences in 2020 caused by February 29th have been removed"})
    df_time["Weekday"] = pd.to_datetime(df_time[['Year', 'Month', 'Day']]).dt.day_name()
    show_aggregation(df_time, ["Weekday", "Day"], operation, [0.4, 0.6], kwargs={"category_orders": weekdays})
    df_time["Months"] = df_time["Month"].apply(lambda x: month_names[x-1])
    show_aggregation(df_time, ["Months", "Year"], operation, [0.55, 0.45], kwargs={"category_orders": {"Months": month_names}})
