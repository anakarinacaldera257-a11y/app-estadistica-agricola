"""Descripción y descarga de la tabla de parcelas."""

import pandas as pd
import streamlit as st

from src.eda import cargar_datos, valores_faltantes

st.set_page_config(page_title="Datos de parcelas", page_icon="📋", layout="wide")
st.title("Datos de parcelas")
st.write(
    "Cada fila corresponde a una parcela. Las variables cuantitativas incluyen "
    "mediciones y dosis; suelo, riego e identificador son variables cualitativas."
)

# 1. Cargar los registros y mostrar su contenido tal como se encuentra en el CSV.
parcelas = cargar_datos("parcelas.csv")
st.subheader("Tabla de parcelas")
st.dataframe(parcelas, width="stretch")

# 2. Resumir las dimensiones para conocer cuántas observaciones y variables hay.
filas, columnas = parcelas.shape
st.write(f"**Número de filas:** {filas} · **Número de columnas:** {columnas}")

# 3. Clasificar cada columna según su tipo de dato almacenado.
tipos = pd.DataFrame(
    {
        "variable": parcelas.columns,
        "tipo": [
            "Cuantitativa" if pd.api.types.is_numeric_dtype(parcelas[columna]) else "Cualitativa"
            for columna in parcelas.columns
        ],
        "tipo de dato": [str(parcelas[columna].dtype) for columna in parcelas.columns],
    }
)
st.subheader("Tipo de cada variable")
st.dataframe(tipos, hide_index=True, width="stretch")

# 4. Revisar faltantes y ofrecer el mismo archivo para descarga.
st.subheader("Valores faltantes")
st.dataframe(valores_faltantes(parcelas), width="stretch")

st.download_button(
    label="Descargar parcelas.csv",
    data=parcelas.to_csv(index=False).encode("utf-8"),
    file_name="parcelas.csv",
    mime="text/csv",
)
