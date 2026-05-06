import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. NASTAVITVE STRANI
st.set_page_config(page_title="Izviri pitne vode", layout="wide")

st.title("💧 Zemljevid naravnih izvirov pitne vode")
st.markdown("Interaktivni zemljevid z informacijami o dostopnosti in varnosti vode.")

# 2. PODATKOVNA BAZA (V realnosti bi to bil Google Sheets ali SQL)
data = {
    'Ime': ['Grofova voda', 'Izvir Nadiže', 'Slatinski vrelec Nuskova', 'Izvir Hublja'],
    'Lat': [46.1825, 46.4744, 46.8322, 45.8978],
    'Lon': [13.7542, 13.6826, 16.0234, 13.9167],
    'Opis': [
        'Starodaven izvir pri Tolminu, znan po zdravilnih lastnostih.',
        'Visokogorski izvir v dolini Tamar, ki kmalu ponikne.',
        'Naravna mineralna voda z visoko vsebnostjo železa.',
        'Mogočen kraški izvir nad Ajdovščino, izjemno aktiven po dežju.'
    ],
    'Avto': [False, False, True, True],
    'Kolo': [True, True, True, True],
    'Pes': [True, True, True, True],
    'Slika': [
        'https://wikimedia.org',
        'https://wikimedia.org',
        'https://wikimedia.org',
        'https://wikimedia.org'
    ]
}

df = pd.DataFrame(data)

# 3. STRANSKA VRSTICA (Filtri in Opozorilo)
st.sidebar.header("Filtri dostopnosti")
f_avto = st.sidebar.checkbox("Dostopno z avtom")
f_kolo = st.sidebar.checkbox("Dostopno s kolesom")

# Logika za opozorilo o dežju (Simulacija - v praksi povežeš na Weather API)
st.sidebar.warning("⚠️ **OPOZORILO:** Zaradi nedavnega deževja na območju Julijskih Alp priporočamo prekuhavanje vode iz gozdnih izvirov!")

# Filtriranje podatkov
filtered_df = df.copy()
if f_avto:
    filtered_df = filtered_df[filtered_df['Avto'] == True]
if f_kolo:
    filtered_df = filtered_df[filtered_df['Kolo'] == True]

# 4. PRIKAZ ZEMLJEVIDA
m = folium.Map(location=[46.1512, 14.9955], zoom_start=8, tiles="Stamen Terrain" if 'Stamen' in str(folium.TileLayer) else "OpenStreetMap")

for i, row in filtered_df.iterrows():
    popup_content = f"""
    <div style='width: 200px;'>
        <h4>{row['Ime']}</h4>
        <img src='{row['Slika']}' width='180'>
        <p>{row['Opis']}</p>
        <p><b>Dostop:</b> {'🚗' if row['Avto'] else ''} {'🚲' if row['Kolo'] else ''} {'🥾' if row['Pes'] else ''}</p>
    </div>
    """
    folium.Marker(
        [row['Lat'], row['Lon']],
        popup=folium.Popup(popup_content, max_width=250),
        tooltip=row['Ime']
    ).add_to(m)

st_folium(m, width=900, height=500)

# 5. PODROBNOSTI POD ZEMLJEVIDOM
st.subheader("Seznam izvirov")
st.dataframe(filtered_df[['Ime', 'Opis', 'Avto', 'Kolo', 'Pes']])
