"""Carga y resumen exploratorio de los datos de parcelas agrícolas."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).resolve().parents[1] / "datos"


@st.cache_data
def cargar_datos(nombre_csv: str) -> pd.DataFrame:
    """Carga un archivo CSV de la carpeta datos y almacena el resultado en caché."""
    ruta = DATA_DIR / nombre_csv
    return pd.read_csv(ruta)


def cargar_metadatos() -> dict:
    """Lee y devuelve los metadatos de identificación del proyecto."""
    ruta = DATA_DIR / "metadatos.json"
    with ruta.open(encoding="utf-8") as archivo:
        return json.load(archivo)


def resumen_numerico(serie: pd.Series) -> dict:
    """Calcula estadísticas descriptivas, incluyendo desviación muestral y CV %."""
    valores = pd.to_numeric(serie, errors="coerce").dropna()
    if valores.empty:
        return {
            "n": 0,
            "media": np.nan,
            "mediana": np.nan,
            "desviación estándar muestral": np.nan,
            "CV (%)": np.nan,
            "mínimo": np.nan,
            "Q1": np.nan,
            "Q3": np.nan,
            "máximo": np.nan,
            "RIC": np.nan,
            "asimetría": np.nan,
        }

    q1 = valores.quantile(0.25)
    q3 = valores.quantile(0.75)
    media = valores.mean()
    desviacion = valores.std(ddof=1)

    return {
        "n": int(valores.count()),
        "media": media,
        "mediana": valores.median(),
        "desviación estándar muestral": desviacion,
        "CV (%)": desviacion / media * 100 if media != 0 else np.nan,
        "mínimo": valores.min(),
        "Q1": q1,
        "Q3": q3,
        "máximo": valores.max(),
        "RIC": q3 - q1,
        "asimetría": valores.skew(),
    }


def valores_faltantes(df: pd.DataFrame) -> pd.DataFrame:
    """Resume los valores faltantes por variable, en cantidad y porcentaje."""
    faltantes = df.isna().sum()
    return pd.DataFrame(
        {
            "valores faltantes": faltantes,
            "porcentaje faltante (%)": faltantes.div(len(df)).mul(100)
            if len(df)
            else 0.0,
        }
    )


def atipicos_iqr(serie: pd.Series) -> dict:
    """Calcula las vallas de Tukey (1.5·RIC) y los valores fuera de ellas."""
    valores = pd.to_numeric(serie, errors="coerce").dropna()
    if valores.empty:
        return {
            "Q1": np.nan,
            "Q3": np.nan,
            "RIC": np.nan,
            "valla_inferior": np.nan,
            "valla_superior": np.nan,
            "valores_atipicos": valores,
        }

    q1 = valores.quantile(0.25)
    q3 = valores.quantile(0.75)
    ric = q3 - q1
    valla_inferior = q1 - 1.5 * ric
    valla_superior = q3 + 1.5 * ric

    return {
        "Q1": q1,
        "Q3": q3,
        "RIC": ric,
        "valla_inferior": valla_inferior,
        "valla_superior": valla_superior,
        "valores_atipicos": valores[
            (valores < valla_inferior) | (valores > valla_superior)
        ],
    }
