"""
generar_datos.py
Genera los datos PERSONALIZADOS de tu app a partir de tu código estudiantil.
Asignatura: Estadística Aplicada con Python y R · Ingeniería Agrícola · Unisucre
NO modifiques nada, excepto las dos líneas marcadas con  <--
"""
import hashlib   # para calcular la "huella" única de tus datos
import json      # para guardar los metadatos
from pathlib import Path

import numpy as np
import pandas as pd

# ------------------------------------------------------------------
# 0. Tus datos de identificación (ÚNICAS líneas que modificas)
# ------------------------------------------------------------------
codigo = "1100015448"            # <-- tu código estudiantil completo, entre comillas
nombre = "Ana Karina Caldera Mejia"       # <-- tus nombres y apellidos

semilla = int(codigo) % 2**32            # la semilla depende de tu código
rng = np.random.default_rng(semilla)     # generador de números aleatorios
Path("datos").mkdir(exist_ok=True)       # carpeta donde se guardan los CSV

# ------------------------------------------------------------------
# 1. Escenario asignado: cultivo y municipio
# ------------------------------------------------------------------
cultivos = {  # cultivo: (rendimiento base en t/ha, escala de variación)
    "Maíz": (4.5, 1.0), "Arroz": (5.5, 0.9), "Yuca": (18.0, 3.5),
    "Ñame": (14.0, 3.0), "Ajonjolí": (0.9, 0.2), "Plátano": (12.0, 2.5),
    "Frijol": (1.4, 0.3), "Sorgo": (3.8, 0.8)}
cultivo = list(cultivos)[semilla % len(cultivos)]
base, esc = cultivos[cultivo]
municipio = ["Sincelejo", "Corozal", "Sampués", "Los Palmitos",
             "San Marcos", "Majagual", "Tolú", "Ovejas"][(semilla // 8) % 8]

# ------------------------------------------------------------------
# 2. parcelas.csv: una fila por parcela (para EDA y, luego, regresión)
# ------------------------------------------------------------------
n = 80 + semilla % 41                                   # entre 80 y 120 parcelas
suelo = rng.choice(["Franco", "Arcilloso", "Arenoso"], n, p=[0.45, 0.35, 0.20])
riego = rng.choice(["Sí", "No"], n, p=[0.4, 0.6])
dosis_N = rng.uniform(0, 180, n).round(0)               # kg/ha de nitrógeno
lamina = np.where(riego == "Sí", rng.uniform(250, 600, n),
                  rng.uniform(100, 350, n)).round(0)    # mm de agua recibida
mo = rng.normal(2.5, 0.8, n).clip(0.5, 5.0).round(2)    # materia orgánica (%)
ph = rng.normal(6.2, 0.5, n).clip(4.8, 7.8).round(2)    # pH del suelo
efecto_suelo = {"Franco": 0.25, "Arcilloso": 0.0, "Arenoso": -0.30}
rend = (base
        + esc * (0.9 * dosis_N / 180 + 0.8 * (lamina - 100) / 500 + 0.20 * (mo - 2.5))
        - esc * 0.6 * (ph - 6.3) ** 2
        + esc * np.vectorize(efecto_suelo.get)(suelo)
        + rng.normal(0, 0.45 * esc, n))
rend = np.clip(rend, 0.2 * base, None)
atipicos = rng.choice(n, 2, replace=False)               # 2 parcelas atípicas
rend[atipicos[0]] *= 1.9                                  # una muy alta
rend[atipicos[1]] *= 0.35                                 # una muy baja (plaga)
mo_con_faltantes = mo.astype(float)
mo_con_faltantes[rng.choice(n, 3 + semilla % 4, replace=False)] = np.nan  # datos faltantes

parcelas = pd.DataFrame({
    "parcela": [f"P{i:03d}" for i in range(1, n + 1)],
    "suelo": suelo, "riego": riego,
    "dosis_N": dosis_N, "lamina_riego": lamina,
    "materia_organica": mo_con_faltantes, "ph": ph,
    "rendimiento": rend.round(2)})
parcelas.to_csv("datos/parcelas.csv", index=False)

# ------------------------------------------------------------------
# 3. clima_mensual.csv: serie mensual 2015-2025 (para series de tiempo al final)
# ------------------------------------------------------------------
fechas = pd.date_range("2015-01-01", "2025-12-01", freq="MS")
mes = fechas.month.values
t = np.arange(len(fechas))
# régimen bimodal del Caribe: lluvias en abril-mayo y septiembre-noviembre
patron = np.array([15, 20, 45, 110, 160, 110, 90, 120, 160, 190, 130, 45])
precip = (patron[mes - 1] * rng.uniform(0.85, 1.15)
          * rng.lognormal(0, 0.30, len(t))).round(1)
temp = (27.5 + 0.012 * t + 0.9 * np.cos(2 * np.pi * (mes - 3) / 12)
        + rng.normal(0, 0.35, len(t))).round(2)
pd.DataFrame({"fecha": fechas.strftime("%Y-%m-%d"),
              "precipitacion_mm": precip,
              "temperatura_c": temp}).to_csv("datos/clima_mensual.csv", index=False)

# ------------------------------------------------------------------
# 4. muestra10.csv: 10 parcelas para el cálculo A MANO (Lápiz y Algoritmo)
# ------------------------------------------------------------------
sin_atipicos = parcelas.drop(index=atipicos)
muestra10 = sin_atipicos.sample(9, random_state=semilla % 10_000)
muestra10 = pd.concat([muestra10, parcelas.loc[[atipicos[0]]]])  # incluye 1 atípico
muestra10 = muestra10[["parcela", "suelo", "riego", "rendimiento"]].sort_values("parcela")
muestra10.to_csv("datos/muestra10.csv", index=False)

# ------------------------------------------------------------------
# 5. Huella y metadatos
# ------------------------------------------------------------------
huella = hashlib.md5(f"{codigo}|{n}|{parcelas['rendimiento'].sum():.2f}".encode()
                     ).hexdigest()[:8].upper()
meta = {"codigo": codigo, "nombre": nombre, "cultivo": cultivo,
        "municipio": municipio, "n_parcelas": int(n), "huella": huella}
Path("datos/metadatos.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                                        encoding="utf-8")

print(f"Estudiante: {nombre} | Código: {codigo} | Huella: {huella}")
print(f"Cultivo: {cultivo} | Municipio: {municipio} | Parcelas: {n}")
print("\nMuestra de 10 parcelas para tu cálculo a mano:")
print(muestra10.to_string(index=False))