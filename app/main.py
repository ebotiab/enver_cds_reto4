import os
import streamlit as st
import numpy as np
from PIL import  Image

# Custom imports 
from src.multipage import MultiPage
# import your pages here
from src.pages import project_introduction, aggregated_analysis, district_analysis, prophet_forecasting

from src.constants import title, sidebar_text

# Configuration page
st.set_page_config(page_title='enver_reto4cds',
                   page_icon='app/images/wall-e.png',
                   layout="wide")

# Sidebar uppside
st.sidebar.image(np.array(Image.open('app/images/wall-e.png')),
                 use_column_width=True)
st.sidebar.header(title)

# Create an instance of the app
app = MultiPage()

# Title of the main page
display = np.array(Image.open('app/images/logo.png'))
col1, col2 = st.columns([2, 9])
col1.image(display, use_column_width=True)
col2.title('CDS Reto 4: Contenedores inteligentes y rutas de basuras')

# Add all your application here
app.add_page("Introducción al proyecto", project_introduction.app)
app.add_page("Análisis agregado residuos", aggregated_analysis.app)
app.add_page("Análisis por disitritos", district_analysis.app)
app.add_page("Predicción generación residuos", prophet_forecasting.app)

# The main app
app.run()

# Sidebar downside
st.sidebar.markdown('Streamlit Dashboard')
st.sidebar.markdown(sidebar_text)
