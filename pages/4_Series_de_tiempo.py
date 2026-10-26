"""Vista previa de las series mensuales de precipitación."""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.eda import cargar_datos

st.set_page_config(page_title="Series de tiempo", page_icon="🌧️", layout="wide")
st.title("Series de tiempo")
st.info("Esta página está en construcción.")
st.write("En las próximas versiones se trabajarán los siguientes temas:")
st.markdown(
    """
- Componentes de una serie temporal
- Descomposición
- Promedios móviles
- Pronóstico
"""
)

# La vista previa convierte las fechas de texto a fechas para ordenar el eje temporal.
clima = cargar_datos("clima_mensual.csv")
clima["fecha"] = pd.to_datetime(clima["fecha"])
figura, eje = plt.subplots(figsize=(10, 4))
eje.plot(clima["fecha"], clima["precipitacion_mm"], color="#2878b5")
eje.set(
    title="Precipitación mensual (2015–2025)",
    xlabel="Fecha",
    ylabel="Precipitación (mm)",
)
figura.autofmt_xdate()
figura.tight_layout()
st.pyplot(figura)
plt.close(figura)
