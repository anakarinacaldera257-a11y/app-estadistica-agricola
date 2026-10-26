"""Análisis exploratorio univariado, cualitativo y bivariado."""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src.eda import atipicos_iqr, cargar_datos, resumen_numerico

st.set_page_config(page_title="Análisis exploratorio", page_icon="📊", layout="wide")
st.title("Análisis exploratorio de datos (EDA)")

# 1. Cargar las parcelas y preparar controles para filtrar los análisis.
parcelas = cargar_datos("parcelas.csv")
with st.sidebar:
    st.header("Filtros")
    opciones_suelo = ["Todos", *sorted(parcelas["suelo"].dropna().unique())]
    opciones_riego = ["Todos", *sorted(parcelas["riego"].dropna().unique())]
    suelo_elegido = st.selectbox("Tipo de suelo", opciones_suelo)
    riego_elegido = st.selectbox("Tipo de riego", opciones_riego)

filtradas = parcelas.copy()
if suelo_elegido != "Todos":
    filtradas = filtradas[filtradas["suelo"] == suelo_elegido]
if riego_elegido != "Todos":
    filtradas = filtradas[filtradas["riego"] == riego_elegido]

if filtradas.empty:
    st.info("La combinación de filtros seleccionada no contiene parcelas.")
    st.stop()

unidades = {
    "dosis_N": "Dosis de nitrógeno (kg/ha)",
    "lamina_riego": "Lámina de riego (mm)",
    "materia_organica": "Materia orgánica (%)",
    "ph": "pH del suelo (adimensional)",
    "rendimiento": "Rendimiento (t/ha)",
}
numericas = filtradas.select_dtypes(include="number").columns.tolist()

# 2. Describir la forma, dispersión y observaciones extremas de una variable.
st.header("a) Análisis univariado")
variable = st.selectbox(
    "Variable cuantitativa",
    numericas,
    format_func=lambda nombre: unidades.get(nombre, nombre),
)
serie = filtradas[variable].dropna()
st.dataframe(
    pd.DataFrame([resumen_numerico(serie)], index=[unidades.get(variable, variable)]),
    width="stretch",
)

if serie.empty:
    st.info("No hay observaciones disponibles para esta variable y estos filtros.")
else:
    izquierda, derecha = st.columns(2)
    with izquierda:
        figura, eje = plt.subplots()
        sns.histplot(x=serie, kde=True, stat="density", ax=eje, color="#2b8a3e")
        eje.set(title="Histograma y curva de densidad", xlabel=unidades.get(variable, variable), ylabel="Densidad")
        st.pyplot(figura)
        plt.close(figura)
    with derecha:
        figura, eje = plt.subplots()
        sns.boxplot(y=serie, ax=eje, color="#8fd19e")
        eje.set(title="Diagrama de caja", ylabel=unidades.get(variable, variable))
        st.pyplot(figura)
        plt.close(figura)

resultado_atipicos = atipicos_iqr(filtradas[variable])
parcelas_atipicas = filtradas.loc[resultado_atipicos["valores_atipicos"].index]
st.subheader("Parcelas fuera de las vallas de Tukey")
st.write(
    f"Valla inferior: {resultado_atipicos['valla_inferior']:.3f} · "
    f"Valla superior: {resultado_atipicos['valla_superior']:.3f}"
)
if parcelas_atipicas.empty:
    st.write("No se identificaron parcelas atípicas con el criterio de 1.5·RIC.")
else:
    st.dataframe(
        parcelas_atipicas[["parcela", variable]].rename(
            columns={variable: unidades.get(variable, variable)}
        ),
        hide_index=True,
        width="stretch",
    )

# 3. Comparar las frecuencias de las categorías de suelo y riego.
st.header("b) Análisis cualitativo")
for variable_categorica in ["suelo", "riego"]:
    conteo = filtradas[variable_categorica].fillna("Sin dato").value_counts(dropna=False)
    frecuencias = pd.DataFrame(
        {
            "categoría": conteo.index,
            "frecuencia absoluta": conteo.values,
            "frecuencia relativa (%)": conteo.values / conteo.sum() * 100,
        }
    )
    st.subheader(f"Frecuencias de {variable_categorica}")
    st.dataframe(frecuencias, hide_index=True, width="stretch")
    figura, eje = plt.subplots()
    sns.countplot(
        x=filtradas[variable_categorica].fillna("Sin dato"),
        order=conteo.index,
        ax=eje,
        color="#4c956c",
    )
    eje.set(
        title=f"Parcelas por {variable_categorica}",
        xlabel="Tipo de suelo" if variable_categorica == "suelo" else "Tipo de riego",
        ylabel="Número de parcelas",
    )
    st.pyplot(figura)
    plt.close(figura)

# 4. Explorar diferencias entre grupos y asociaciones entre mediciones.
st.header("c) Análisis bivariado")
izquierda, derecha = st.columns(2)
with izquierda:
    figura, eje = plt.subplots()
    sns.boxplot(data=filtradas, x="suelo", y="rendimiento", ax=eje, color="#8fd19e")
    eje.set(title="Rendimiento por tipo de suelo", xlabel="Tipo de suelo", ylabel="Rendimiento (t/ha)")
    st.pyplot(figura)
    plt.close(figura)
with derecha:
    figura, eje = plt.subplots()
    sns.boxplot(data=filtradas, x="riego", y="rendimiento", ax=eje, color="#8fd19e")
    eje.set(title="Rendimiento por tipo de riego", xlabel="Tipo de riego", ylabel="Rendimiento (t/ha)")
    st.pyplot(figura)
    plt.close(figura)

variables_x = [nombre for nombre in numericas if nombre != "rendimiento"]
if variables_x:
    variable_x = st.selectbox(
        "Variable X para comparar con el rendimiento",
        variables_x,
        format_func=lambda nombre: unidades.get(nombre, nombre),
    )
    figura, eje = plt.subplots()
    sns.scatterplot(
        data=filtradas,
        x=variable_x,
        y="rendimiento",
        hue="riego",
        ax=eje,
        palette="Set1",
    )
    eje.set(
        title=f"{unidades.get(variable_x, variable_x)} y rendimiento por riego",
        xlabel=unidades.get(variable_x, variable_x),
        ylabel="Rendimiento (t/ha)",
    )
    st.pyplot(figura)
    plt.close(figura)

matriz_correlacion = filtradas[numericas].corr(method="pearson")
etiquetas = [unidades.get(nombre, nombre) for nombre in matriz_correlacion.columns]
figura, eje = plt.subplots(figsize=(8, 6))
sns.heatmap(
    matriz_correlacion,
    annot=True,
    cmap="vlag",
    center=0,
    xticklabels=etiquetas,
    yticklabels=etiquetas,
    ax=eje,
)
eje.set(title="Correlación de Pearson entre variables cuantitativas")
plt.setp(eje.get_xticklabels(), rotation=35, ha="right")
st.pyplot(figura)
plt.close(figura)

# 5. Contrastar los cálculos con la muestra seleccionada para el ejercicio manual.
st.header("d) Muestra de 10 parcelas (verificación del cálculo a mano)")
muestra = cargar_datos("muestra10.csv")
st.dataframe(muestra, hide_index=True, width="stretch")
resumen_muestra = resumen_numerico(muestra["rendimiento"])
st.subheader("Resumen numérico del rendimiento")
st.dataframe(
    pd.DataFrame([resumen_muestra], index=["Rendimiento (t/ha)"]),
    width="stretch",
)

atipicos_muestra = atipicos_iqr(muestra["rendimiento"])
st.subheader("Vallas de Tukey y valores atípicos")
st.dataframe(
    pd.DataFrame(
        [
            {
                "Q1": atipicos_muestra["Q1"],
                "Q3": atipicos_muestra["Q3"],
                "RIC": atipicos_muestra["RIC"],
                "valla inferior": atipicos_muestra["valla_inferior"],
                "valla superior": atipicos_muestra["valla_superior"],
            }
        ]
    ),
    hide_index=True,
    width="stretch",
)
indices_atipicos = atipicos_muestra["valores_atipicos"].index
st.write(
    "Parcelas atípicas: "
    + (
        ", ".join(muestra.loc[indices_atipicos, "parcela"].astype(str))
        if len(indices_atipicos)
        else "ninguna"
    )
)
st.subheader("Rendimiento medio por riego en la muestra (t/ha)")
st.dataframe(
    muestra.groupby("riego", as_index=False)["rendimiento"]
    .mean()
    .rename(columns={"rendimiento": "rendimiento medio (t/ha)"}),
    hide_index=True,
    width="stretch",
)
