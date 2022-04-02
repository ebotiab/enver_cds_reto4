import numpy as np
import streamlit as st

path_load = "https://residuosbucket.s3.amazonaws.com/residuos.csv"
data_path = "data/processed/data.feather"
data_small_path = "data/processed/data_small.feather"
data_districts_path = "data/processed/districts.feather"
geojson_load = "https://residuosbucket.s3.amazonaws.com/madrid-districts.geojson"
geojson_path = "data/external/madrid-districts.geojson"
title = 'CDS Reto 4: Contenedores inteligentes y rutas de basuras'

# SIDEBAR ==============================================================
sidebar_text = '''
Este proyecto ha sido realizado por el equipo ENVER

April, 2022
'''

# HOME =========================================================================
intro = '''
Puesto que no disponemos de datos de la ciudad de Anthem, hemos decidido desarrollar esta página web utilizando datos públicos de la ciudad de Madrid
'''


# DATA =========================================================================

districts_names = ["Centro", "Arganzuela", "Retiro", "Salamanca", "Chamartin", "Tetuan", "Chamberi", "Fuencarral-El Pardo", "Moncloa-Aravaca", "Latina",
                   "Carabanchel", "Usera", "Puente de Vallecas", "Moratalaz", "Ciudad Lineal", "Hortaleza", "Villaverde", "Villa de Vallecas", "Vicalvaro", "San Blas", "Barajas"]

districts_name2id = {
    "Centro": 1,
    "Arganzuela": 2,
    "Retiro": 3,
    "Salamanca": 4,
    "Chamartin": 5,
    "Tetuan": 6,
    "Chamberi": 7,
    "Fuencarral-El Pardo": 8,
    "Moncloa-Aravaca": 9,
    "Latina": 10,
    "Carabanchel": 11,
    "Usera": 12,
    "Puente de Vallecas": 13,
    "Moratalaz": 14,
    "Ciudad Lineal": 15,
    "Hortaleza": 16,
    "Villaverde": 17,
    "Villa de Vallecas": 18,
    "Vicalvaro": 19,
    "San Blas": 20,
    "Barajas": 21
}

weekdays = {"Weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
month_names = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

options_materials = {"RESTO": 'RESTO', "ORGÁNICO": "ORGANICA", "ENVASES": "ENVASES", "VIDRIO": "VIDRIO",
                     "gran volumen": "GRAN VOLUMEN", "clínicos": "CLINICOS", "metales": "METALES", "animales muertos": "ANIMALES MUERTOS"}

small_cols = ["Distrito", "PESO", "Lote", "Clasificacion", "Year", "Month", "Day"]

district_cols = ["PESO", "Hombres(%)", "Personas_nacionalidad_española(%)", "Tasa_absoluta_paro(%)", "Sedentarismo(%)", "Superficie(Ha.)", "Densidad(hab./Ha.)", "Poblacion", "Edad_media_poblacion", "Numero_hogares", "Habitantes_hogar_medio", "Renta_neta_media_anual_hogares",
                 "Rent_Bruta_Per_Cápita", "Paro_registrado", "Poblacion_etapa_educativa", "Satisfaccion_calidad_vida(%)", "Recogida_residuos_kg/habitante/dia", "Centros_deportivos_municipales", "Centros_servicios_sociales", "Centros_cultura", "Numero_escuelas"]

map_defaults = [(0, "#00F"), (1, "#F00"), (0, "#000")]

operations_dict = {"Mean": np.mean, "Sum": np.sum,
                   "Std dev": np.std, "Count": np.size}

weekday = {"Monday": 0, "Tuesday": 1, "Wednesday": 2,
           "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
num_to_weekday = {value: key for (key, value) in weekday.items()}
districts = list(districts_name2id.keys())

possible_days_dummies = ['Weekday_Monday', 'Weekday_Saturday', 'Weekday_Sunday', 'Weekday_Thursday',
                         'Weekday_Tuesday', 'Weekday_Wednesday', 'Poblacion',
                         'hour_sec_Madrugada', 'hour_sec_Mañana', 'hour_sec_Noche',
                         'hour_sec_Tarde', 'Month_1', 'Month_2', 'Month_3', 'Month_4', 'Month_5',
                         'Month_6', 'Month_7', 'Month_8', 'Month_9', 'Month_10', 'Month_11',
                         'Month_12']
id_to_week = {value: key for (key, value) in weekday.items()}

rmse_dis = {1: 5.4421, 2: 5.3173, 3: 5.4023, 4: 7.5929, 5: 7.3623, 6: 4.8072, 7: 7.5491,
            8: 9.5537, 9: 5.9614, 10: 5.0935, 11: 5.9582, 12: 3.7371, 13: 4.9622,
            14: 4.866, 15: 4.7522, 16: 7.3733, 17: 4.2288, 18: 4.1643, 19: 4.9699, 20: 6.7314, 21: 5.487}

sel_data_defaults = [("container", st), ('mssg', "Seleccione la operación para agregar los datos"), ("options", operations_dict.keys()), ("key", None)]

holiday_dates = [('new_year', '01-01'), ('epifania', '01-06'), ('labor_day', '05-01'), ('assumption_day', '08-15'), ('national_holiday','10-12'), 
                 ('all_saints_day', '11-01'),('constitution', '12-06'), ('inmaculada', '12-08'), ('christmas', '12-25')]

#DATA ANALYSIS ================================================================
references = '''
---
## References and Credit

'''

# Reproducibility ==================================================================
reproducibility_text = '''
In order to reproduce the Analysis we made on this dashboard you can follow the steps below:
1.
'''
