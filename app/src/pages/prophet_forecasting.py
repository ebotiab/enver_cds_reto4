import streamlit as st
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
import datetime as dt

from src.constants import data_small_path, districts_names, options_materials, districts_name2id, holiday_dates
from src.pages.utils import filter_by_colvalue, aggregate_df

def app():
    st.title('Predicción de la generación de residuos')
    df = pd.read_feather(data_small_path)
    col1, col2, col3, empty, col4 = st.columns([0.25,0.25,0.25,0.03,0.22])
    empty.empty()
    # select range of the prediction
    date_chosen = col1.date_input("Seleccione la fecha de finalización en la predicción", dt.date(2022, 12, 31), dt.date(2022, 1, 1), dt.date(2024, 12, 31))
    range_pred = (date_chosen - dt.date(2021, 12, 31)).days
    # filter by district
    df = filter_by_colvalue(df, "Distrito", col2, "Selecciona distrito", options=["ALL", ]+districts_names, transpose=districts_name2id)
    # filter by classification
    classif_names = ["ALL", ]+list(options_materials.keys())
    df = filter_by_colvalue(df, "Clasificacion", col3, "Selecciona material", classif_names, options_materials)
    # create prophet df
    selection_data = {"container":col4, "mssg":"Selecciona operación", "options": ["Mean", "Sum", "Std dev"]}
    df = aggregate_df(df, ["Year", "Month", "Day"], ["PESO",], selection_data=selection_data)
    df = df.sort_values(["Year", "Month", "Day"])
    df_prophet = pd.DataFrame({"y": df["PESO"]})
    df_prophet["ds"] = pd.to_datetime(df[['Year', 'Month', 'Day']])
    # create holidays df
    holidays_df = pd.DataFrame({
        'holiday': 'holy_week',
        'ds': pd.to_datetime(['2017-04-14', '2018-03-30', '2019-04-19', '2020-04-10', '2021-04-02']),
        'lower_window': 0,
        'upper_window': 2,
    })
    for hol_name, hol_date in holiday_dates:
        hol = pd.DataFrame({
            'holiday': hol_name,
            'ds': pd.to_datetime([f'{year}-{hol_date}' for year in range(2017, date_chosen.year+1)]),
            'lower_window': 0,
            'upper_window': 1,
        })
        holidays_df = pd.concat([holidays_df, hol])
    holidays_df = holidays_df[holidays_df["ds"] < pd.to_datetime(date_chosen)]
    # compute and display prophet analysis
    m = Prophet(holidays=holidays_df)
    m.fit(df_prophet)
    future = m.make_future_dataframe(periods=range_pred)
    forecast = m.predict(future)
    st.plotly_chart(plot_plotly(m, forecast),use_container_width=True)
    st.markdown("Pronóstico desglosado en tendencia, estacionalidad semanal y estacionalidad anual:")
    st.plotly_chart(plot_components_plotly(m, forecast), use_container_width=True)
