# 🏆 WC26 AI Command Center

App de predicción de partidos de la Copa del Mundo 2026 usando el modelo de Poisson.

## 📁 Estructura del proyecto

```
wc26_app/
├── app.py                          # App principal de Streamlit
├── predicciones_fase_grupos.csv    # Predicciones pre-calculadas
├── Fase_grupos.txt                 # Datos originales del torneo
├── requirements.txt                # Dependencias Python
└── README.md                       # Este archivo
```

## 🚀 Deploy gratis en Streamlit Community Cloud

### Paso 1 — Sube el proyecto a GitHub
1. Crea un repositorio nuevo en [github.com](https://github.com) (puede ser público o privado)
2. Sube todos los archivos de esta carpeta al repositorio

```bash
git init
git add .
git commit -m "WC26 AI Command Center"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### Paso 2 — Deploy en Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en **"New app"**
4. Selecciona tu repositorio y la rama `main`
5. En "Main file path" escribe: `app.py`
6. Haz clic en **"Deploy!"**

¡Listo! En ~2 minutos tu app estará disponible en una URL pública gratuita.

---

## 🧮 Modelo de Poisson

La lambda se construye con:

```
λ_A = (OV_A/100)^α × (100/DV_B)^β × (MV_A/MV_ref)^γ × FA_A × k
```

| Parámetro | Valor default | Descripción |
|-----------|--------------|-------------|
| α | 0.6 | Peso del Valor Ofensivo |
| β | 0.3 | Peso del Valor Defensivo rival |
| γ | 0.1 | Peso del Valor de Mercado |
| k | 1.5 | Constante de escala de goles |

Los parámetros son ajustables en tiempo real desde la barra lateral de la app.

## 📊 Funcionalidades

- **Dashboard**: KPIs globales, favoritos del torneo, distribución de resultados
- **Predictor de Partido**: fixture oficial + partido personalizado, matriz de marcadores, radar de atributos
- **Análisis de Equipos**: estadísticas por equipo, lambda promedio, historial de partidos
- **Tabla de Predicciones**: tabla completa filtrable con descarga CSV
