"""Página de inicio de la aplicación multipágina de estadística agrícola."""

import streamlit as st

from src.eda import cargar_metadatos

st.set_page_config(
    page_title="Estadística Aplicada — Ingeniería Agrícola",
    page_icon="🌱",
    layout="wide",
)

st.title("Estadística Aplicada con Python y R — Ingeniería Agrícola, Unisucre")
st.write(
    "Explora datos de parcelas y clima mediante herramientas estadísticas "
    "reproducibles, con variables y unidades propias de la producción agrícola."
)

metadatos = cargar_metadatos()
with st.container(border=True):
    st.subheader("Identificación del proyecto")
    columnas = st.columns(5)
    campos = [
        ("Nombre", metadatos["nombre"]),
        ("Código", metadatos["codigo"]),
        ("Cultivo", metadatos["cultivo"]),
        ("Municipio", metadatos["municipio"]),
        ("Huella", metadatos["huella"]),
    ]
    for columna, (etiqueta, valor) in zip(columnas, campos):
        columna.metric(etiqueta, valor)

st.header("Páginas de la aplicación")
st.markdown(
    """
- **Datos:** consulta la tabla de parcelas, el tipo de cada variable y los
  valores faltantes; también puedes descargar el archivo CSV.
- **EDA:** filtra por tipo de suelo y riego para estudiar distribuciones,
  categorías, relaciones entre variables y una muestra de diez parcelas.
- **Regresión:** próximamente incluirá análisis de correlación, modelos lineales
  y diagnóstico de residuos.
- **Series de tiempo:** próximamente explorará componentes, descomposición,
  promedios móviles y pronóstico de la precipitación mensual.
"""
)
