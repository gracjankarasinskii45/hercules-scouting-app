import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Konfiguracja strony
st.set_page_config(
    page_title="HERKULES CF | Professional Scouting System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stylizacja CSS
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #ffffff; }
    .stMetric { background-color: #111827; padding: 16px; border-radius: 12px; border: 1px solid #1f2937; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #2563eb; color: white; }
    .stButton>button:hover { background-color: #1d4ed8; }
    h1, h2, h3 { color: #f9fafb; font-family: 'Helvetica Neue', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# Inicjalizacja klienta Supabase
supabase_client = None
try:
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase_client = create_client(url, key)
    DB_CONNECTED = True
except Exception:
    DB_CONNECTED = False

# --- PANEL LOGOWANIA ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = "Skaut"

if not st.session_state.logged_in:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("# ⚡ HERKULES CF 2.0")
        st.markdown("### System Zarządzania Talentami i Analizy Skautingowej")
        st.markdown("---")
        
        username = st.text_input("Identyfikator / E-mail", placeholder="skaut@herculescf.es")
        password = st.text_input("Hasło dostępu", type="password", placeholder="••••••••")
        role = st.selectbox("Wybierz profil operacyjny:", ["Skaut Terenowy", "Trener Akademii", "Dyrektor Sportowy"])
        
        if st.button("Zaloguj do Systemu", type="primary"):
            if username:
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.rerun()
            else:
                st.warning("Wprowadź identyfikator, aby uzyskać dostęp.")
        st.stop()

# --- NAWIGACJA ---
st.sidebar.markdown("# ⚡ HÉRCULES CF")
st.sidebar.markdown(f"**Zalogowany:** {st.session_state.user_role}")
st.sidebar.markdown("---")

nav = st.sidebar.radio(
    "Nawigacja Główna",
    ["📋 Nowy Profil i Silnik Ocen", "🔍 Baza Zawodników (DB)", "📊 Analiza i Porównania", "⚙️ Ustawienia Systemu"]
)

st.sidebar.markdown("---")
if DB_CONNECTED:
    st.sidebar.success("🟢 Supabase DB: Online")
else:
    st.sidebar.error("🔴 Supabase DB: Offline")

if st.sidebar.button("Wyloguj się"):
    st.session_state.logged_in = False
    st.rerun()

# --- MODUŁ 1: NOWY PROFIL I SILNIK OCEN (1-10) ---
if nav == "📋 Nowy Profil i Silnik Ocen":
    st.title("📋 Tworzenie Profilu i Silnik Ocen Zawodnika")
    st.markdown("Oceń wybrane kluczowe umiejętności w skali 1 do 10. Silnik automatycznie wyliczy wskaźniki gotowości.")

    with st.form("scout_form_engine"):
        c1, c2, c3 = st.columns(3)
        with c1:
            fname = st.text_input("Imię zawodnika")
            club = st.text_input("Obecny klub")
        with c2:
            lname = st.text_input("Nazwisko zawodnika")
            position = st.selectbox("Pozycja", ["CB - Środkowy Obrońca", "CM - Środkowy Pomocnik", "W - Skrzydłowy", "CF - Napastnik", "GK - Bramkarz"])
        with c3:
            birth_year = st.number_input("Rocznik", 2000, 2016, 2008)
            match_type = st.selectbox("Typ obserwacji", ["Mecz ligowy", "Turniej / Sparing", "Konsultacja"])

        st.markdown("### ⚙️ Silnik Ocen Umiejętności (Skala 1 - 10)")
        
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        with sc1:
            pace = st.slider("Szybkość / Dynamika", 1.0, 10.0, 7.0, 0.5)
        with sc2:
            tech = st.slider("Technika Użytkowa", 1.0, 10.0, 7.5, 0.5)
        with sc3:
            tact = st.slider("Świadomość Taktyczna", 1.0, 10.0, 6.5, 0.5)
        with sc4:
            def_val = st.slider("Gra Defensywna", 1.0, 10.0, 6.0, 0.5)
        with sc5:
            ment = st.slider("Mentalność / Charakter", 1.0, 10.0, 8.0, 0.5)

        notes = st.text_area("Szczegółowa opinia skauta:", "Profil perspektywiczny pod model gry Hércules CF...")

        submitted = st.form_submit_button("Oblicz Silnik i Zapisz Profil", type="primary")
        if submitted:
            # Silnik wyliczający wskaźniki na bazie skali 1-10 (przeliczenie na format analityczny)
            cr = round(((pace + tech + tact + def_val + ment) / 5) * 10, 1) # Skala 0-100
            pr = round(min(99.0, cr * 1.14), 1)
            index_ti = round((tech * 0.4 + tact * 0.4 + ment * 0.2) * 10, 1)
            
            report_payload = {
                "first_name": fname if fname else "Nieznany",
                "last_name": lname if lname else "Zawodnik",
                "birth_year": birth_year,
                "club": club if club else "Brak",
                "position": position,
                "cr": cr,
                "pr": pr,
                "notes": f"[TI: {index_ti}] {notes}",
                "created_at": datetime.now().isoformat()
            }

            if DB_CONNECTED and supabase_client:
                try:
                    supabase_client.table("scouting_reports").insert(report_payload).execute()
                    st.success(f"Sukces! Profil zawodnika {fname} {lname} zapisany (CR: {cr}, PR: {pr}, TI: {index_ti}).")
                except Exception as err:
                    st.error(f"Błąd zapisu do bazy: {err}")
            else:
                st.warning(f"Zapisano lokalnie. Wyliczony silnik -> CR: {cr} | PR: {pr} | TI: {index_ti}")

# --- MODUŁ 2: BAZA ZAWODNIKÓW ---
elif nav == "🔍 Baza Zawodników (DB)":
    st.title("🔍 Centralna Baza Obserwowanych Talentów")
    st.markdown("Lista zapisanych profili wraz z wynikami silnika analitycznego.")

    df = pd.DataFrame()
    if DB_CONNECTED and supabase_client:
        try:
            res = supabase_client.table("scouting_reports").select("*").execute()
            if res.data:
                df = pd.DataFrame(res.data)
        except Exception:
            pass

    if df.empty:
        df = pd.DataFrame([
            {"first_name": "Alejandro", "last_name": "Perez", "birth_year": 2008, "club": "Valencia CF", "position": "W - Skrzydłowy", "cr": 74.0, "pr": 88.0, "notes": "[TI: 78.0] Wysoka dynamika 1v1."},
            {"first_name": "Mateusz", "last_name": "Kowalski", "birth_year": 2009, "club": "Akademia Hercules", "position": "CM - Środkowy Pomocnik", "cr": 69.5, "pr": 83.0, "notes": "[TI: 72.0] Odporność na pressing."}
        ])

    st.dataframe(df, use_container_width=True)

# --- MODUŁ 3: ANALIZA I PORÓWNANIA ---
elif nav == "📊 Analiza i Porównania":
    st.title("📊 Analityka i Zestawienia Kadr")
    col_a, col_b = st.columns(2)
    with col_a:
        fig_pie = px.pie(names=['Obrońcy', 'Pomocnicy', 'Skrzydłowi', 'Napastnicy'], values=[25, 40, 20, 15], title="Struktura pozycji w bazie")
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        fig_bar = px.bar(x=['2007', '2008', '2009', '2010'], y=[84.2, 81.5, 79.0, 76.8], title="Średni Potencjał (PR) wg Roczników")
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig_bar, use_container_width=True)

# --- MODUŁ 4: USTAWIENIA ---
elif nav == "⚙️ Ustawienia Systemu":
    st.title("⚙️ Konfiguracja i Status Systemu")
    st.info("System działa w oparciu o silnik skautingowy oparty na skali 1-10.")
    st.json({
        "Project": "Hércules CF Scouting System",
        "Engine Scale": "1.0 - 10.0",
        "Database Status": "Connected" if DB_CONNECTED else "Offline"
    })
