import dash
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc  # Importar dbc
import numpy as np
import os

# Load the dataset with the cleaned structure
df_bolivia_30_women = pd.read_csv('Mujeres STEM Bolivia  ofi(1).csv')
df_bolivia_30_women.columns = df_bolivia_30_women.columns.str.strip()
df_bolivia_30_women = df_bolivia_30_women[['Nombre', 'Campo STEM', 'Institución', 'Destacado', 
                                           'Contacto (página personal, otros)', 'Latitud', 'Longitud']]
# Clean trailing spaces from Campo STEM values, drop NaN or empty rows
df_bolivia_30_women['Campo STEM'] = df_bolivia_30_women['Campo STEM'].str.strip()
df_bolivia_30_women = df_bolivia_30_women.dropna(subset=['Campo STEM'])

# Get unique non-null options for the dropdown
unique_stem_options = df_bolivia_30_women['Campo STEM'].unique()

# Mapa de colores únicos para cada mujer usando Plotly Express
colors = px.colors.qualitative.Prism
df_bolivia_30_women['Color'] = [colors[i % len(colors)] for i in range(len(df_bolivia_30_women))]

# Adjust lat/long to avoid overlap
def ajustar_lat_long(df, zoom):
    seen = {}
    factor = 0.01 if zoom <= 5 else 0.001
    for i, row in df.iterrows():
        key = (row['Latitud'], row.get('Longitud', 0))
        if key in seen:
            seen[key] += 1
            df.at[i, 'Latitud'] += np.random.uniform(-factor, factor) * seen[key]
            df.at[i, 'Longitud'] += np.random.uniform(-factor, factor) * seen[key]
        else:
            seen[key] = 0
    return df

# City coordinates for centering the map
city_coordinates = {
    'La Paz': {"lat": -16.5000, "lon": -68.1500, "zoom": 12},
    'Cochabamba': {"lat": -17.3895, "lon": -66.1568, "zoom": 12},
    'Santa Cruz': {"lat": -17.7833, "lon": -63.1823, "zoom": 12},
    'Todos': {"lat": -17.0, "lon": -65.0, "zoom": 5}
}

# Initialize Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Mujeres STEM Bolivia"
server = app.server

# Layout of the app
app.layout = html.Div(style={'backgroundColor': '#f7f9fc', 'padding': '20px'}, children=[
    # Botón "Volver al Inicio" en la parte superior
    html.Div([
        dbc.Button(
            html.Span("🏠 Volver al Inicio", style={"margin-left": "5px"}),
            href="https://stem-bolivia.onrender.com",  # URL de la página principal (app2.py)
            color="primary",
            className="mt-2"
        )
    ], style={"text-align": "left", "margin-bottom": "20px"}),

    # Encabezado principal
    html.H1("¡Sean bienvenidos al Portal Mujeres STEM de Bolivia!", style={'text-align': 'center', 'color': '#333'}),
    html.P("Este espacio podrás encontrar a mujeres bolivianas que se desenvuelven profesionalmente y lideran en las áreas de ciencia, tecnología, ingeniería y matemáticas (STEM).", 
           style={'text-align': 'center', 'color': '#555', 'margin-bottom': '30px'}),

    # Filtros
    html.Div([
        html.Label('Filtrar por Campo STEM:', style={'font-weight': 'bold', 'color': '#333'}),
        dcc.Dropdown(
            id='filtro_stem',
            options=[{'label': i, 'value': i} for i in unique_stem_options] + [{'label': 'Todos los campos', 'value': 'Todos los campos'}],
            value='Todos los campos'
        )
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),

    dcc.Graph(id='mapa_interactivo', style={'height': '700px'}),

    # Formulario y llamado a la acción
    html.Div([
        html.P("¿Eres y/o conoces a una mujer boliviana trabajando en áreas STEM? Te invitamos a completar este breve formulario para ser incluida en nuestro portal si así lo deseas. ¡Construyamos juntas una red que inspire y fortalezca la presencia femenina en STEM!",
               style={'text-align': 'center', 'margin-top': '30px'}),
        html.Div([
            html.A("Completa el formulario aquí", 
                   href="https://docs.google.com/forms/d/e/1FAIpQLSfwBN3aT7V-P-qWVlNRC5VXuay5sBZTE2tCq7OUhFO7rnzXKw/viewform?usp=sf_link", 
                   target="_blank", 
                   style={'text-align': 'center', 'display': 'block', 'margin-top': '10px', 'color': '#007bff', 'font-weight': 'bold'})
        ], style={"text-align": "center"})
    ]),

    # Nota informativa al final
    html.Div(
        children=[
            html.P(
                "Nota: Esta es una versión beta preliminar de la plataforma. "
                "Se están realizando ajustes y mejoras continuamente. "
                "Si encuentras algún problema o tienes sugerencias, no dudes en compartirlas.",
                style={
                    'color': '#555', 
                    'font-style': 'italic', 
                    'font-size': '14px', 
                    'text-align': 'center',
                    'border-top': '1px solid #ccc',
                    'padding-top': '10px',
                    'margin-top': '20px'
                }
            )
        ]
    )
])

# Callback to update the map with filters
@app.callback(
    Output('mapa_interactivo', 'figure'),
    [Input('filtro_stem', 'value')]
)
def update_map(filtro_stem):
    dff = df_bolivia_30_women.copy()
    if filtro_stem != 'Todos los campos':
        dff = dff[dff['Campo STEM'] == filtro_stem]

    dff = ajustar_lat_long(dff, zoom=5)

    fig = go.Figure(go.Scattermapbox(
        lat=dff['Latitud'],
        lon=dff['Longitud'],
        mode='markers',
        marker=dict(size=18, color=dff['Color'], opacity=0.85),
        text=dff['Nombre'],
        hoverinfo='text'
    ))

    fig.update_layout(
        mapbox=dict(style="carto-positron", zoom=5, center={"lat": -17.0, "lon": -65.0}),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=9090)
