import streamlit as st
import plotly.express as px
import pandas as pd
import os
from datetime import datetime
from scrappRIO import update_rio
from visualization import create_html_visualization
import random

# Configuración de la página
st.set_page_config(
    page_title="Data Visualization",
    page_icon="📊",
    layout="wide"
)

# Aplicar estilos personalizados
st.markdown("""
    <style>
        .main {
            padding: 20px;
        }
        .stPlotlyChart {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=random.randint(45, 65))  # Cache por 60 segundos
def load_data():
    """Cargar y cachear datos del CSV"""
    update_rio()
    try:
        csv_path = os.path.join('data', 'registro.csv')
        df = pd.read_csv(csv_path).assign(
            datetime = lambda data: pd.to_datetime(data.datetime)
        ).sort_values(by = "datetime").reset_index(drop = True)
        modification_time = datetime.fromtimestamp(
            os.path.getmtime(csv_path)
        ).strftime('%I:%M:%S %p')
        return df, modification_time
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame({
            'x': list(range(10)),
            'y': [0] * 10
        }), datetime.now().strftime('%I:%M:%S %p')

def create_plot(df):
    """Crear gráfico con Plotly"""
    fig = px.line(
        df, 
        x='datetime', 
        y='cmg', 
        title='Data Trend Analysis',
        template='plotly_white',
        hover_data = 'BCMG P.AZUCAR_22O'
    )
    
    fig.update_layout(
        font_family="Roboto",
        title={
            'font_size': 24,
            'xanchor': 'center',
            'x': 0.5
        },
        xaxis_title="Time",
        yaxis_title="Value",
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f0f0f0'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f0f0f0'
        ),
        margin=dict(t=50, l=50, r=50, b=50)
    )
    
    fig.update_traces(
        line=dict(width=2.5, color='#2c3e50'),
        mode='lines+markers',
        marker=dict(size=6)
    )
    
    return fig

def main():    
    # Crear y mostrar el gráfico
    df, modification_time = load_data()
    fig = create_plot(df)
    html_content = create_html_visualization(fig, modification_time)
    st.components.html(html_content)

    # Botón para actualización manual
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main() 