
  import dash
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
import os

# Load the dataset with the cleaned structure
df_bolivia_30_women = pd.read_csv('/Users/romi_1/Downloads/Mujeres STEM Bolivia  ofi(1) (1).csv')
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
    'Tarija': {"lat": -21.5333, "lon": -64.7333, "zoom": 12},
    'Sucre': {"lat": -19.0333, "lon": -65.2627, "zoom": 12},
    'Oruro': {"lat": -17.9667, "lon": -67.1064, "zoom": 12},
    'Potosi': {"lat": -19.5833, "lon": -65.7500, "zoom": 12},
    'Beni': {"lat": -14.8333, "lon": -64.9000, "zoom": 12},
    'Pando': {"lat": -11.0264, "lon": -68.7692, "zoom": 12},
    'Todos': {"lat": -17.0, "lon": -65.0, "zoom": 5}
}

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Mujeres STEM Bolivia"
server = app.server

# Layout of the app
app.layout = html.Div(style={'backgroundColor': '#f7f9fc', 'padding': '20px'}, children=[
    # Botón "Volver al Inicio" en la parte superior
    html.Div([
        html.A("🏠 Volver al Inicio", href="https://stem-bolivia.onrender.com", style={
            "color": "#007bff", 
            "font-size": "18px",
            "text-decoration": "none",
            "font-weight": "bold",
            "margin-bottom": "20px",
            "display": "inline-block"
        })
    ], style={"text-align": "left"}),


# Layout of the app
app.layout = html.Div(style={'backgroundColor': '#f7f9fc', 'padding': '20px'}, children=[
    html.H1("¡Sean bienvenidos al Portal Mujeres STEM de Bolivia!", style={'text-align': 'center', 'color': '#333'}),
    html.P("Este espacio podrás encontrar a mujeres bolivianas que se desenvuelven profesionalmente y lideran en las áreas de ciencia, tecnología, ingeniería y matemáticas (STEM). Encontrarás información clave como su nombre, profesión, ocupación, logros destacados y algún medio de contacto. Nuestro objetivo es visibilizar su impacto y conectar a quienes buscan inspiración, colaboración o referentes en estos campos.", 
           style={'text-align': 'center', 'color': '#555', 'margin-bottom': '30px'}),
    
    html.H1("", style={'text-align': 'center', 'color': '#333'}),
    html.P("Una visualización de mujeres destacadas en el campo STEM en Bolivia", style={'text-align': 'center', 'color': '#555'}),
    
    html.Div([
        html.Label('Filtrar por Campo STEM:', style={'font-weight': 'bold', 'color': '#333'}),
        dcc.Dropdown(
            id='filtro_stem',
            options=[{'label': i, 'value': i} for i in unique_stem_options] + [{'label': 'Todos los campos', 'value': 'Todos los campos'}],
            value='Todos los campos'
        )
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),
    
    html.Div([
        html.Label('Seleccionar ciudad:', style={'font-weight': 'bold', 'color': '#333'}),
        dcc.Dropdown(
            id='filtro_ciudad',
            options=[{'label': "Ver toda Bolivia", 'value': 'Todos'}] + [{'label': ciudad, 'value': ciudad} for ciudad in city_coordinates.keys() if ciudad != 'Todos'],
            value='Todos'
        )
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),
    
    dcc.Graph(id='mapa_interactivo', style={'height': '700px'}),

    html.P("¿Eres y/o conoces a una mujer boliviana trabajando en áreas STEM? Te invitamos a completar este breve formulario para ser incluida en nuestro portal si así lo deseas. Construiremos una red que inspire a más mujeres y fortalezca la presencia femenina en STEM.", 
           style={'text-align': 'center', 'margin-top': '30px'}),
    html.A("Completa el formulario aquí", href="https://docs.google.com/forms/d/e/1FAIpQLSfwBN3aT7V-P-qWVlNRC5VXuay5sBZTE2tCq7OUhFO7rnzXKw/viewform?usp=sf_link", target="_blank", style={'text-align': 'center', 'display': 'block', 'margin-top': '10px'}),
    html.P("¡Deja tu huella y únete al Portal Mujeres STEM Bolivia!", style={'text-align': 'center', 'margin-top': '10px', 'color': '#555'}),

    # Nota informativa sobre la versión beta
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
    [Input('filtro_stem', 'value'),
     Input('filtro_ciudad', 'value')]
)
def update_map(filtro_stem, filtro_ciudad):
    dff = df_bolivia_30_women.copy()
    if filtro_stem != 'Todos los campos':
        dff = dff[dff['Campo STEM'] == filtro_stem]
    
    coord = city_coordinates.get(filtro_ciudad, city_coordinates['Todos'])

    dff = ajustar_lat_long(dff, coord['zoom'])

    fig = go.Figure(go.Scattermapbox(
        lat=dff['Latitud'],
        lon=dff['Longitud'],
        mode='markers',
        marker=dict(
            size=18,
            color=dff['Color'],
            opacity=0.85
        ),
        text=dff['Nombre'],
        hoverinfo='text',
        hovertext=dff.apply(lambda row: f"<b>{row['Nombre']}</b><br>{row['Campo STEM']}<br><i>Institución:</i> {row['Institución']}<br><i>Logros:</i> {row['Destacado']}", axis=1),
        customdata=dff['Contacto (página personal, otros)']
    ))

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=coord['zoom'],
            center={"lat": coord['lat'], "lon": coord['lon']}
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig

# Callback to open external links when clicking on a map point
app.clientside_callback(
    """
    function(clickData) {
        if (clickData) {
            const url = clickData.points[0].customdata;
            window.open(url, '_blank');
        }
    }
    """,
    Output('mapa_interactivo', 'clickData'),
    Input('mapa_interactivo', 'clickData')
)

if __name__ == '__main__':
    app.run_server(debug=True, port=9090)
