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
import os

if os.path.isfile("RIOs/registro.csv"):
    RIO =pd.read_csv("RIOs/registro.csv").assign(
        datetime = lambda data: pd.to_datetime(data.datetime)
    )
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


# Page title
st.title('Real-time Data Scraping and Plotting')

# Create placeholder for the plot
plot_placeholder = st.empty()

# Add a download button for the CSV
if st.button('Download CSV'):
    df = pd.DataFrame(st.session_state.data)
    st.download_button(
        label="Download data as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='scraped_data.csv',
        mime='text/csv',
    )

while True:
    hora_actual = dt.datetime.now()
    url = f'https://www.coordinador.cl/wp-admin/admin-ajax.php?action=export_energia_csv&fecha_inicio={hora_actual.strftime("%Y-%m-%d")}&fecha_termino={hora_actual.strftime("%Y-%m-%d")}&hora_inicio=00:00:00&hora_termino=23:59:59'
    scraper = cloudscraper.create_scraper()
    response = scraper.get(
        url
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
        i+=1
        time.sleep(120)
        continue

    if dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 0, 0, 0) < hora_actual <= dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 8, 0, 0):
        bloque = 0
    elif dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 8, 0, 0) < hora_actual <= dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 18, 0, 0):
        bloque = 1
    elif dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 18, 0, 0) < hora_actual <= dt.datetime(hora_actual.year, hora_actual.month, hora_actual.day, 23, 0, 0)+dt.timedelta(hours=1):
        bloque = 2
    url = f"https://www.coordinador.cl/wp-content/uploads/{hora_actual.year}/{str(hora_actual.month).zfill(2)}/PROGRAMA{hora_actual.strftime('%Y%m%d')}.zip"
    # Download the zip file
    response = scraper.get(url)
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
        datetime = lambda data: pd.to_datetime(data.FECHA+" "+data.HORA)
    ).dropna().drop_duplicates().reset_index(drop =True)
    ultimo_dato = aux.datetime.max()
    if ultimo_dato not in pd.to_datetime(RIO.datetime).to_list():
        aux_final = aux.query("datetime == @ultimo_dato")
        RIO = pd.concat([RIO, aux_final], ignore_index=True)
        RIO.to_csv("RIOs/registro.csv", index = False)
        for i in aux_final.columns:
            data[i].append(aux_final[i].values[0])

    fig = px.line(RIO, x = "datetime", y = "cmg",
                  title = "Real-time RIO",
                  labels = {"datetime": "Fecha y Hora", "cmg": "USD/MWh Barra Nueva Pan de Azucar"})
    st.plotly_chart(fig, use_container_width=True)
    time.sleep(60)