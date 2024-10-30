# Importar las librerías necesarias
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Lectura del archivo de datos
data_path = 'datos/Anexo4.Covid-19_CE_15-03-23.xlsx'
df = pd.read_excel(data_path, sheet_name='COVID-19')
#print("Resumen estadístico df:\n", df.describe())
# Filtrar los datos para el análisis de 2020 y 2021
df['FECHA DEFUNCIÓN'] = pd.to_datetime(df['FECHA DEFUNCIÓN'], errors='coerce')
df_2021 = df[(df['FECHA DEFUNCIÓN'].dt.year == 2021) & (df['COVID-19'] == 'CONFIRMADO')]
df_2020_2021 = df[(df['FECHA DEFUNCIÓN'].dt.year.isin([2020, 2021])) & (df['COVID-19'] == 'CONFIRMADO')]
#print("Resumen estadístico df 2021:\n", df_2021.describe())
# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Layout de la aplicación en cuadrícula
app.layout = html.Div([
    html.H1("Dashboard COVID-19 - Análisis de Muertes", style={'text-align': 'center'}),
    html.H3("Por: Juan Carlos Vega Rueda, Maestría IA", style={'text-align': 'center'}),
    # Contenedor en cuadrícula
    html.Div([
        # Mapa de defunciones por departamento
        html.Div([
            html.H3("Mapa de Muertes por COVID-19 Confirmadas por Departamento (2021)"),
            dcc.Graph(id="mapa_muertes_departamento", style={'height': '400px'}),
        ], style={'grid-area': 'mapa', 'padding': '10px', 'border': '1px solid #ccc'}),

        # Gráfico de barras horizontal para las 5 ciudades con mayor índice de muertes
        html.Div([
            html.H3("Top 5 Ciudades con Mayor Índice de Muertes Confirmadas (2021)"),
            dcc.Graph(id="grafico_barras", style={'height': '400px'}),
        ], style={'grid-area': 'barras', 'padding': '10px', 'border': '1px solid #ccc'}),

        # Gráfico circular de casos confirmados, sospechosos y descartados
        html.Div([
            html.H3("Distribución de Casos de COVID-19 por Tipo (2021)"),
            dcc.Graph(id="grafico_circular", style={'height': '400px'}),
        ], style={'grid-area': 'circular', 'padding': '10px', 'border': '1px solid #ccc'}),

        # Gráfico de línea de muertes por mes (2020 y 2021)
        html.Div([
            html.H3("Muertes Confirmadas por COVID-19 por Mes (2020 - 2021)"),
            dcc.Graph(id="grafico_linea", style={'height': '400px'}),
        ], style={'grid-area': 'linea', 'padding': '10px', 'border': '1px solid #ccc'}),

        # Gráfico de histograma de edades quinquenales (2020)
        html.Div([
            html.H3("Distribución de Muertes Confirmadas por Edad (2020)"),
            dcc.Graph(id="grafico_histograma", style={'height': '400px'}),
        ], style={'grid-area': 'histograma', 'padding': '10px', 'border': '1px solid #ccc'}),
    ], style={
        'display': 'grid',
        'grid-template-areas': """
            'mapa barras circular'
            'linea linea histograma'
        """,
        'grid-gap': '10px',
        'padding': '20px',
        'grid-template-columns': '1fr 1fr 1fr'
    })
])


# Función para actualizar el mapa
@app.callback(
    Output("mapa_muertes_departamento", "figure"),
    Input("mapa_muertes_departamento", "id")
)
def actualizar_mapa(id):
    df_map = df_2021.groupby("DEPARTAMENTO").size().reset_index(name='muertes')
    fig = px.choropleth(
        df_map,
        geojson="https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json",  # GeoJSON para departamentos de Colombia
        locations="DEPARTAMENTO",
        featureidkey="properties.NOMBRE_DPT",
        color="muertes",
        hover_name="DEPARTAMENTO",
        color_continuous_scale="Viridis",
        title="Total de Muertes Confirmadas por Departamento en Colombia (2021)"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    return fig

# Función para actualizar el gráfico de barras
@app.callback(
    Output("grafico_barras", "figure"),
    Input("grafico_barras", "id")
)
def actualizar_grafico_barras(id):
    df_top5 = df[(df['FECHA DEFUNCIÓN'].dt.year == 2021) & (df['COVID-19'] == 'CONFIRMADO')].groupby("MUNICIPIO").size().nlargest(5).reset_index(name='muertes')
    fig = px.bar(df_top5, x='muertes', y='MUNICIPIO', orientation='h', title="Top 5 Ciudades con Mayor Número de Muertes")
    return fig

# Función para actualizar el gráfico circular
@app.callback(
    Output("grafico_circular", "figure"),
    Input("grafico_circular", "id")
)
def actualizar_grafico_circular(id):
    df_2021 = df[(df['FECHA DEFUNCIÓN'].dt.year == 2021)]
    df_tipo = df_2021['COVID-19'].value_counts().reset_index()
    df_tipo.columns = ['Tipo', 'Casos']
    fig = px.pie(df_tipo, names='Tipo', values='Casos', title="Distribución de Casos de COVID-19 por Tipo")
    return fig

# Función para actualizar el gráfico de línea
@app.callback(
    Output("grafico_linea", "figure"),
    Input("grafico_linea", "id")
)
def actualizar_grafico_linea(id):
    df_linea = df_2020_2021.groupby(df_2020_2021['FECHA DEFUNCIÓN'].dt.to_period("M")).size().reset_index(name='muertes')
    df_linea['FECHA DEFUNCIÓN'] = df_linea['FECHA DEFUNCIÓN'].dt.to_timestamp()
    fig = px.line(df_linea, x='FECHA DEFUNCIÓN', y='muertes', title="Muertes Confirmadas por Mes")
    return fig

# Función para actualizar el histograma de edades
@app.callback(
    Output("grafico_histograma", "figure"),
    Input("grafico_histograma", "id")
)
def actualizar_grafico_histograma(id):
    df_2020 = df[(df['FECHA DEFUNCIÓN'].dt.year == 2020) & (df['COVID-19'] == 'CONFIRMADO')]
    df_2020['Edad Rango'] = pd.cut(pd.to_numeric(df_2020['EDAD FALLECIDO'].str.extract(r'(\d+)', expand=False), errors='coerce'),
                                   bins=[0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 79, 84, 89, 100],
                                   labels=["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", 
                                           "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", 
                                           "75-79", "80-84", "85-89", "90+"])
    fig = px.histogram(df_2020, x='Edad Rango', title="Distribución de Muertes Confirmadas por Edad")
    fig.update_xaxes(categoryorder='array', categoryarray=["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", 
                                                           "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", 
                                                           "60-64", "65-69", "70-74", "75-79", "80-84", "85-89", "90+"])
    return fig

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)

# Elaborado por: Juan Vega, Maestría IA