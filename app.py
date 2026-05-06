import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# 1. NASTAVITVE
st.set_page_config(page_title="Vsi izviri Slovenije (OSM Live)", layout="wide")

st.title("💧 Živ zemljevid vseh izvirov pitne vode")
st.write("Podatki so pridobljeni v živo iz OpenStreetMap baze za celo Slovenijo.")

# 2. FUNKCIJA ZA PRIDOBIVANJE PODATKOV IZ SPLETA (OpenStreetMap)
@st.cache_data(ttl=3600) # Podatke shrani za 1 uro, da ne preobremenimo strežnika
def get_osm_springs():
    # Overpass Query: Poišči vse izvire (natural=spring) v Sloveniji
    overpass_url = "http://overpass-api.de"
    overpass_query = """
    [out:json][timeout:25];
    area["name"="Slovenija"]->.searchArea;
    (
      node["natural"="spring"]["drinking_water"="yes"](area.searchArea);
      node["amenity"="drinking_water"](area.searchArea);
    );
    out body;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    
    # Pretvori v tabelo
    out = []
    for element in data['elements']:
        name = element.get('tags', {}).get('name', 'Neznan izvir')
        out.append({
            'Ime': name,
            'Lat': element['lat'],
            'Lon': element['lon'],
            'Opis': element.get('tags', {}).get('description', 'Naravni vir pitne vode.'),
            'Dostop_Avto': element.get('tags', {}).get('motorcar', 'ni podatka'),
            'Slika': 'https://placeholder.com'
        })
    return pd.DataFrame(out)

# 3. NALAGANJE
try:
    df = get_osm_springs()
    st.success(f"Našel sem {len(df)} lokacij po celi Sloveniji!")

    # 4. STRANSKA VRSTICA
    st.sidebar.header("Opozorila")
    st.sidebar.info("Podatki prihajajo iz skupnosti OSM. Pred pitjem vedno preverite stanje na terenu.")
    
    # Iskalnik
    search_query = st.sidebar.text_input("Išči po imenu (npr. 'Soča')")
    if search_query:
        df = df[df['Ime'].str.contains(search_query, case=False)]

    # 5. ZEMLJEVID
    m = folium.Map(location=[46.1512, 14.9955], zoom_start=8)

    # Uporabimo MarkerCluster, ker je točk ogromno (več kot 500)
    from folium.plugins import MarkerCluster
    marker_cluster = MarkerCluster().add_to(m)

    for i, row in df.iterrows():
        popup_html = f"<b>{row['Ime']}</b><br>{row['Opis']}"
        folium.Marker(
            [row['Lat'], row['Lon']],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=row['Ime'],
            icon=folium.Icon(color='blue', icon='tint')
        ).add_to(marker_cluster)

    st_folium(m, width=1000, height=600)
    
    # Tabela
    st.dataframe(df[['Ime', 'Lat', 'Lon']])

except Exception as e:
    st.error(f"Prišlo je do napake pri pridobivanju podatkov: {e}")
