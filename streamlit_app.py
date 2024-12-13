import streamlit as st
import plotly.express as px
import pandas as pd
import os
from datetime import datetime
from scrappRIO import update_rio
from visualization import create_html_visualization
import random
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import google.auth
import pickle

# Configuración de la página
st.set_page_config(
    page_title="Data Visualization",
    page_icon="📊",
    layout="wide"
)

# Set up the OAuth 2.0 flow
def authenticate_user():
    # Load credentials from the secrets
    client_id = st.secrets["google"]["client_id"]
    client_secret = st.secrets["google"]["client_secret"]

    # Debug: Print client ID and redirect URIs
    print(f"Client ID: {client_id}")
    print("Redirect URIs: http://localhost:8501")

    # Load credentials from the file
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    else:
        creds = None

    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_config(
                {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost:8501"]
                    }
                },
                scopes=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid']
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.write(f"Please go to this URL: {auth_url}")
            code = st.text_input("Enter the authorization code:")
            if code:
                flow.fetch_token(code=code)
                creds = flow.credentials
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
    return creds

@st.cache_data(ttl=random.randint(45, 65))  # Cache por 60 segundos
def load_data(creds):
    """Cargar y cachear datos del CSV"""
    update_rio(creds)
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
    df, modification_time = load_data(authenticate_user())
    fig = create_plot(df)
    html_content = create_html_visualization(fig, modification_time)
    st.components.html(html_content)

if __name__ == "__main__":
    creds = authenticate_user()
    if creds:
        st.success("You are authenticated!")
        # You can now use the credentials to access Google APIs
    else:
        st.error("Authentication failed.")