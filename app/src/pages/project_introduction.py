import streamlit as st
import requests
import pandas as pd
from geojson import dump

from src.constants import intro, path_load, data_path, small_cols, data_small_path, district_cols, data_districts_path, geojson_load, geojson_path

def app():
    st.markdown(intro)
    
    @st.cache(allow_output_mutation=True)
    def load_data():
        df = pd.read_csv("https://residuosbucket.s3.amazonaws.com/residuos.csv")
        df.to_feather(data_path)
        # save small df
        df_small = df[small_cols]
        df_small.to_feather(data_small_path)
        # save districts df
        df_districts = df[["Year", "Month", "Day", "Distrito",]+district_cols]
        df_districts.to_feather(data_districts_path)
        # save geojson to display districts map
        geojson = requests.get(geojson_load).json()
        with open(geojson_path, 'w') as f:
            dump(geojson, f)
            
        return df

    # Create a text element and let the reader know the data is loading.
    data_load_state = st.text('Cargando datos...')
    # Load processed data into a dataframe.
    df = load_data()

    # Notify the reader that the data was successfully loaded.
    data_load_state.text('Cargando datos...¡Hecho!')

    if st.checkbox('Mostrar los datos utilizados en el análisis'):
        st.subheader('Datos utilizados')
        st.write(df.head())
