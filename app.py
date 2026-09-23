import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Konfiguracja strony
st.set_page_config(
    page_title="HERKULES 2.0 | System Skautingowy",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stylizacja CSS (Nowoczesny ciemny motyw piłkarski)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    h1, h2, h3 {
        color: #f0f6fc;
    }
    </style>
""", unsafe_allow_html=True)

# Próba połączenia z Supabase (jeśli skonfigurowane w Secrets)
supabase_client = None
try:
    from supabase import create_client, Client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase_client: Client = create_client(url, key)
    CONNECTION_OK = True
except Exception as e:
    CONNECTION_OK = False

# --- PANELE BOCZNE I NAWIGACJA ---
st.sidebar.markdown("# ⚡ HERKULES 2.0")
st.sidebar.markdown("**System Skautingowy & Baza Wiedzy**")
st.sidebar.markdown("---")

menu_choice = st.sidebar.radio(
    "Nawigacja Modułowa:",
    ["📊 Formularz Skautowy", "🧠 Słownik Ról Taktycznych", "📂 Baza Zawodników (DB)", "📈 Raporty i Porównania"]
)

st.sidebar.markdown("---")
if CONNECTION_OK:
    st.sidebar.success("🟢 Supabase: Połączono stabilnie")
else:
    st.sidebar.warning("⚠️ Supabase: Brak sekretów / Offline")

# --- MODUŁ 1: FORMULARZ SKAUTOWY ---
if menu_choice == "📊 Formularz Skautowy":
    st.title("⚡ Nowy Raport Obserwacyjny")
    st.markdown("Wprowadź parametry zawodnika oraz oceny analityczne w skali 1-100.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("I. Dane Personalne i Klubowe")
        first_name = st.text_input("Imię zawodnika", "Jan")
        last_name = st.text_input("Nazwisko zawodnika", "Kowalski")
        birth_year = st.number_input("Rocznik", min_value=2000, max_value=2016, value=2008)
        current_club = st.text_input("Obecny Klub", "Akademia Hercules")
        position = st.selectbox("Pozycja Główna", ["CB - Środkowy Obrońca", "CM - Środkowy Pomocnik", "W - Skrzydłowy", "CF - Napastnik"])
        preferred_foot = st.selectbox("Noga dominująca", ["Prawa", "Lewa", "Obie"])

    with col2:
        st.subheader("II. Profil Analityczny (1-100)")
        pacing = st.slider("Szybkość / Dynamika", 1, 100, 75)
        technique = st.slider("Technika Użytkowa", 1, 100, 80)
        tactical = st.slider("Świadomość Taktyczna", 1, 100, 70)
        defend = st.slider("Gra Defensywna / Pojedynki", 1, 100, 65)
        mental = st.slider("Mentalność / Charakter", 1, 100, 85)

    # Obliczenie wskaźników
    current_rating = round((pacing + technique + tactical + defend + mental) / 5, 1)
    potential_rating = round(current_rating * 1.15 if current_rating < 90 else 99.0, 1)
    index_ti = round((technique * 0.4 + tactical * 0.4 + mental * 0.2), 1)

    st.markdown("---")
    st.subheader("III. Podgląd Indeksów i Radar Zawodnika")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current (CR)", f"{current_rating}")
    m2.metric("Potential (PR)", f"{potential_rating}")
    m3.metric("DPS (Dynamika)", f"+{(potential_rating - current_rating):.1f}")
    m4.metric("Index (TI)", f"{index_ti}")

    # Wykres radarowy
    categories = ['Szybkość', 'Technika', 'Taktyka', 'Defensywa', 'Mentalność']
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[pacing, technique, tactical, defend, mental, pacing],
        theta=categories + [categories[0]],
        fill='toself',
        name=f'{first_name} {last_name}',
        line_color='#00ffcc'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        st.plotly_chart(fig, use_container_width=True)
        
    with col_r2:
        st.markdown("### 📝 Opinia Skauta")
        scout_notes = st.text_area("Kluczowe uwagi, profil motoryczny, rekomendacja transferowa:", "Zawodnik perspektywiczny, bardzo wysoka dynamika w fazie przejścia.")
        
        if st.button("💾 Zapisz Raport do Bazy Supabase", type="primary"):
            report_data = {
                "first_name": first_name,
                "last_name": last_name,
                "birth_year": birth_year,
                "club": current_club,
                "position": position,
                "cr": current_rating,
                "pr": potential_rating,
                "notes": scout_notes,
                "created_at": datetime.now().isoformat()
            }
            if CONNECTION_OK and supabase_client:
                try:
                    supabase_client.table("scouting_reports").insert(report_data).execute()
                    st.success("Raport zapisany pomyślnie w bazie Supabase!")
                except Exception as ex:
                    st.error(f"Błąd zapisu do bazy: {ex}")
            else:
                st.info("Tryb lokalny: Raport symulowany jako zapisany (brak aktywnego Supabase).")

# --- MODUŁ 2: SŁOWNIK RÓL TAKTYCZNYCH ---
elif menu_choice == "🧠 Słownik Ról Taktycznych":
    st.title("🧠 Słownik Ról Taktycznych Hércules CF")
    st.markdown("Standardy profilowania zawodników pod model gry Akademii.")

    tab_pos1, tab_pos2, tab_pos3 = st.tabs(["Środkowy Obrońca (CB)", "Środkowy Pomocnik (CM)", "Skrzydłowy (W)"])

    with tab_pos1:
        st.subheader("Środkowy Obrońca wyprowadzający piłkę (Ball-Playing Defender)")
        st.markdown("""
        - **Kluczowe atrybuty:** Opór pod presją, celność długiego podania, gra w powietrzu.
        - **Wymagany Indeks TI min.:** 65.0
        - **Zadania w fazie budowania:** Inicjowanie akcji linią podania do drugiej linii, odczytywanie pressingu rywala.
        """)

    with tab_pos2:
        st.subheader("Środkowy Pomocnik typu Box-to-Box")
        st.markdown("""
        - **Kluczowe atrybuty:** Wydolność tlenowa, odbiór piłki, wbieganie w pole karne drugiego tempa.
        - **Wymagany Indeks TI min.:** 70.0
        - **Zadania:** Intensywny pressing po stracie, zabezpieczanie przestrzeni centralnych.
        """)

    with tab_pos3:
        st.subheader("Skrzydłowy / Odwrócony Skrzydłowy")
        st.markdown("""
        - **Kluczowe atrybuty:** Pojedynki 1v1 w bocznym sektorze, przyspieszenie z miejsca, dogranie w strefę ECO.
        - **Wymagany Indeks TI min.:** 68.0
        - **Zadania:** Rozciąganie defensywy przeciwnika, gra kombinacyjna w bocznych korytarzach.
        """)

# --- MODUŁ 3: BAZA ZAWODNIKÓW ---
elif menu_choice == "📂 Baza Zawodników (DB)":
    st.title("📂 Centralna Baza Zawodników Skautowanych")
    st.markdown("Przeglądaj, filtruj i analizuj zgromadzone raporty zawodników.")

    # Pobieranie danych z Supabase lub dane testowe
    df_players = pd.DataFrame()
    if CONNECTION_OK and supabase_client:
        try:
            response = supabase_client.table("scouting_reports").select("*").execute()
            if response.data:
                df_players = pd.DataFrame(response.data)
        except Exception:
            pass

    if df_players.empty:
        # Przykładowe dane pokazowe, jeśli baza jest pusta
        df_players = pd.DataFrame([
            {"first_name": "Mateusz", "last_name": "Wiśniewski", "birth_year": 2009, "club": "Wisła Kraków", "position": "CM - Środkowy Pomocnik", "cr": 68.5, "pr": 82.0, "notes": "Duża kultura gry."},
            {"first_name": "Carlos", "last_name": "Gomez", "birth_year": 2008, "club": "Elche CF", "position": "W - Skrzydłowy", "cr": 72.0, "pr": 86.5, "notes": "Świetny drybling w 1v1."},
            {"first_name": "Dawid", "last_name": "Kaczmarek", "birth_year": 2010, "club": "Akademia Hercules", "position": "CB - Środkowy Obrońca", "cr": 64.0, "pr": 79.0, "notes": "Bardzo dobra czytelność gry w defensywie."}
        ])

    st.dataframe(df_players, use_container_width=True)

# --- MODUŁ 4: RAPORTY I PORÓWNANIA ---
elif menu_choice == "📈 Raporty i Porównania":
    st.title("📈 Analiza Porównawcza Kadr")
    st.markdown("Zestawienie średniego potencjału roczników oraz rozkładu pozycji.")

    chart_data = pd.DataFrame({
        'Rocznik': [2008, 2009, 2010, 2011],
        'Średni Potencjał (PR)': [83.5, 80.2, 78.4, 76.1],
        'Liczba Obserwacji': [12, 19, 8, 15]
    })

    fig_bar = px.bar(chart_data, x='Rocznik', y='Średni Potencjał (PR)', color='Średni Potencjał (PR)', title="Średni Potencjał Zawodników wg Roczników")
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    st.plotly_chart(fig_bar, use_container_width=True)
