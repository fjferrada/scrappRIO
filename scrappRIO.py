import pandas as pd
from io import StringIO
import requests
import cloudscraper
import zipfile
import io
import pandas as pd
import datetime as dt
import time
import streamlit as st
import plotly.express as px
import random
import os

if os.path.isfile("RIOs/registro.csv"):
    RIO =pd.read_csv("RIOs/registro.csv").assign(
        datetime = lambda data: pd.to_datetime(data.datetime)
    ).sort_values(by = "datetime").reset_index(drop = True)
else:
    if not os.path.exists("RIOs/"):
        os.mkdir("RIOs/")
    RIO = pd.DataFrame({
        'datetime': [],
        'BCMG P.AZUCAR_22O': [],
        'cmg': [],
        'FECHA': [],
        'HORA': []
    })
    
data = {
    i : RIO[i].to_list() for i in RIO.columns    
}

# Initialize session state with loaded data
if 'data' not in st.session_state:
    st.session_state.data = data
    
st.title('Real-time Data Scraping and Plotting')
if st.button('Download CSV'):
    df = pd.DataFrame(st.session_state.data)
    st.download_button(
        label="Download data as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='scraped_data.csv',
        mime='text/csv',
    )
plot_spot = st.empty() # holding the spot for the graph
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.902.62 Safari/537.36 Edg/92.0.902.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 OPR/78.0.4093.147',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.902.62 Safari/537.36 Edg/92.0.902.62'
]
n_n = 0
while True:
    # while True:
    hora_actual = dt.datetime.now()
    url = f'https://www.coordinador.cl/wp-admin/admin-ajax.php?action=export_energia_csv&fecha_inicio={hora_actual.strftime("%Y-%m-%d")}&fecha_termino={hora_actual.strftime("%Y-%m-%d")}&hora_inicio=00:00:00&hora_termino=23:59:59'
    scraper = cloudscraper.create_scraper()
    response = scraper.get(
            url, headers = {
        'User-Agent': random.choice(user_agents)
        }
    )
        # response.content
        # pd.read_csv(StringIO(response.content.decode('utf-8-sig')))
        # Based on the error message, it seems the CSV data has an inconsistent number of columns
        # Let's try to read and clean the data first
    
        # Print the raw content to inspect it
    
        # Try reading with error_bad_lines=False to skip problematic rows
    try:
        rio = pd.read_csv(StringIO(response.content.decode('utf-8-sig')), 
                    sep=';',
                    on_bad_lines='skip',
                    skiprows=4)["FECHA;HORA;BCMG P.AZUCAR_22O".split(";")] # For newer pandas versions
    except Exception as e:
        print("no captura")
        print(response.content.decode('utf-8-sig'))
        time.sleep(random.uniform(15,30))
        continue

    if dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 0, 0, 0) < hora_actual <= dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 8, 0, 0):
        bloque = 0
    elif dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 8, 0, 0) < hora_actual <= dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 18, 0, 0):
        bloque = 1
    elif dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 18, 0, 0) < hora_actual <= dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 23, 0, 0)+dt.timedelta(hours=1):
        bloque = 2
    url = f"https://www.coordinador.cl/wp-content/uploads/{hora_actual.year}/{str(hora_actual.month).zfill(2)}/PROGRAMA{hora_actual.strftime('%Y%m%d')}.zip"
    # Download the zip file
    time.sleep(random.uniform(1,4))
    response = scraper.get(url, headers = {
    'User-Agent': random.choice(user_agents)
    })
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))

    # Find the xlsx file containing "PO" in the name
    xlsx_file = [f for f in zip_file.namelist() if "PO" in f][0]

    # Read the specific sheet with selected columns
    cols_to_use = [[3,4],
                [7,8],
                [11,12]]
    dt.datetime.now()
    df = pd.read_excel(
                zip_file.open(xlsx_file),
                sheet_name="TCO",
                usecols=[i-1 for i in cols_to_use[bloque]],
                skiprows=6
            )
    df.columns = "BCMG P.AZUCAR_22O;cmg".split(";")
    df = pd.concat(
        [
            df,
            pd.DataFrame([["ERNC",0]], columns = "BCMG P.AZUCAR_22O;cmg".split(";")) 
        ],
        ignore_index=True
    ).dropna().drop_duplicates()
    aux = rio.drop_duplicates().merge(df, on = "BCMG P.AZUCAR_22O", how = "left").assign(
        datetime = lambda data: pd.to_datetime(data.FECHA+" "+data.HORA, format='%Y-%m-%d %H:%M:%S')
    ).dropna().drop_duplicates().reset_index(drop =True)
    ultimo_dato = aux.datetime.max()
    if ultimo_dato not in pd.to_datetime(RIO.datetime).to_list():
        all_dates_in_rio = RIO.datetime.unique()
        aux_not_in_RIO = aux.query("~datetime.isin(@all_dates_in_rio)")
        if len(aux_not_in_RIO) > 0:
            RIO = pd.concat([RIO, aux_not_in_RIO], ignore_index=True).sort_values(by = "datetime").reset_index(drop = True)
            RIO.to_csv("RIOs/registro.csv", index = False)
    filtro_fecha = dt.datetime.now() - dt.timedelta(hours = 48)
    for i in RIO.columns:
        #if len(RIO) > 48:
        st.session_state.data[i] = RIO.query("datetime >= @filtro_fecha")[i].to_list()
    filtroFecha = dt.datetime.now()-dt.timedelta(hours = 48)
    fig = px.line(x = st.session_state.data["datetime"], y = st.session_state.data["cmg"]
                  , hover_data = {"price_maker": st.session_state.data["BCMG P.AZUCAR_22O"]}
                  , title = "Real-time RIO"
                  , labels = {"datetime": "Fecha y Hora", "cmg": "USD/MWh Barra Nueva Pan de Azucar"})
    fig.update_layout(
        xaxis=dict(
            title=dict(
                text="time"
            )
        ),
        yaxis=dict(
            title=dict(
                text="USD/MWh"
            )
        )
    )
    with plot_spot:
        st.plotly_chart(fig, use_container_width = True, key = f"key_{n_n}")
    n_n+=1
    # st.line_chart(x = st.session_state.data["datetime"], y = st.session_state.data["cmg"])
    time.sleep(random.uniform(45,60))
        # plot_placeholder.plotly_chart(fig, use_container_width=True, key = "plot_1")
