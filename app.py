import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Konfiguracja strony
st.set_page_config(
    page_title="HÉRCULES CF | Scouting & Talent System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stylizacja CSS
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #ffffff; }
    .stMetric { background-color: #111827; padding: 14px; border-radius: 10px; border: 1px solid #1f2937; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #2563eb; color: white; }
    .stButton>button:hover { background-color: #1d4ed8; }
    .player-card {
        background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
        border: 2px solid #2563eb;
        border-radius: 16px;
        padding: 24px;
        margin-top: 15px;
    }
    .badge-tag {
        display: inline-block;
        background-color: #1e3a8a;
        color: #93c5fd;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid #3b82f6;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# SŁOWNIK POZYCJI, DEDYKOWANYCH UMIEJĘTNOŚCI (1-10) I WZORÓW DOPASOWANIA PROFILI
POSITION_ENGINE = {
    "CB - Środkowy Obrońca": {
        "skills": [
            "Gra w powietrzu / Główki",
            "Pojedynki 1v1 defensywne",
            "Ustawianie się / Asekuracja",
            "Wprowadzanie piłki / Podanie",
            "Szybkość na krótkim dystansie",
            "Decyzyjność pod presją"
        ],
        "profiles": {
            "Ball-Playing Defender": {"Wprowadzanie piłki / Podanie": 0.4, "Decyzyjność pod presją": 0.3, "Ustawianie się / Asekuracja": 0.3},
            "Stopper Agresywny": {"Pojedynki 1v1 defensywne": 0.4, "Gra w powietrzu / Główki": 0.4, "Szybkość na krótkim dystansie": 0.2},
            "Covering Defender (Asekurujący)": {"Ustawianie się / Asekuracja": 0.4, "Szybkość na krótkim dystansie": 0.4, "Decyzyjność pod presją": 0.2}
        }
    },
    "CM - Środkowy Pomocnik": {
        "skills": [
            "Przegląd pola i wizja",
            "Kultura podania (krótkie/długie)",
            "Odbiór i pressing",
            "Odporność na pressing",
            "Wydolność / Mobilność",
            "Decyzyjność i czas reakcji"
        ],
        "profiles": {
            "Deep-Lying Playmaker": {"Kultura podania (krótkie/długie)": 0.4, "Przegląd pola i wizja": 0.4, "Odporność na pressing": 0.2},
            "Box-to-Box": {"Wydolność / Mobilność": 0.4, "Odbiór i pressing": 0.3, "Decyzyjność i czas reakcji": 0.3},
            "Advanced Playmaker": {"Przegląd pola i wizja": 0.4, "Odporność na pressing": 0.3, "Kultura podania (krótkie/długie)": 0.3}
        }
    },
    "W - Skrzydłowy": {
        "skills": [
            "Pojedynki 1v1 (Drybling)",
            "Szybkość i przyspieszenie",
            "Dośrodkowanie / Dogranie",
            "Wykończenie akcji",
            "Praca w defensywie",
            "Schodzenie do środka"
        ],
        "profiles": {
            "Inverted Winger": {"Pojedynki 1v1 (Drybling)": 0.35, "Schodzenie do środka": 0.35, "Wykończenie akcji": 0.3},
            "Classic Winger": {"Szybkość i przyspieszenie": 0.4, "Dośrodkowanie / Dogranie": 0.4, "Pojedynki 1v1 (Drybling)": 0.2},
            "Wide Playmaker": {"Dośrodkowanie / Dogranie": 0.4, "Schodzenie do środka": 0.3, "Praca w defensywie": 0.3}
        }
    },
    "CF - Napastnik": {
        "skills": [
            "Wykończenie 1v1 / Strzał",
            "Gra tyłem do bramki",
            "Ruch bez piłki / Asekuracja",
            "Gra głową w polu karnym",
            "Pressing i intensywność",
            "Szybkość wyjścia na pozycję"
        ],
        "profiles": {
            "Target Man": {"Gra tyłem do bramki": 0.4, "Gra głową w polu karnym": 0.4, "Wykończenie 1v1 / Strzał": 0.2},
            "Poacher (Lis pola karnego)": {"Wykończenie 1v1 / Strzał": 0.4, "Ruch bez piłki / Asekuracja": 0.4, "Szybkość wyjścia na pozycję": 0.2},
            "Pressing Forward": {"Pressing i intensywność": 0.4, "Szybkość wyjścia na pozycję": 0.3, "Ruch bez piłki / Asekuracja": 0.3}
        }
    },
    "RB/LB - Boczny Obrońca / Wahadłowy": {
        "skills": [
            "Szybkość i wytrzymałość",
            "Gra w defensywie 1v1",
            "Podłączenie się do ataku",
            "Dośrodkowanie z biegu",
            "Taktyczne powroty"
        ],
        "profiles": {
            "Offensive Wingback": {"Podłączenie się do ataku": 0.4, "Dośrodkowanie z biegu": 0.35, "Szybkość i wytrzymałość": 0.25},
            "Defensive Fullback": {"Gra w defensywie 1v1": 0.45, "Taktyczne powroty": 0.35, "Szybkość i wytrzymałość": 0.2},
            "Inverted Fullback": {"Taktyczne powroty": 0.4, "Gra w defensywie 1v1": 0.3, "Podłączenie się do ataku": 0.3}
        }
    },
    "GK - Bramkarz": {
        "skills": [
            "Refleks na linii",
            "Wyjścia do dośrodkowań",
            "Gra nogami / Wprowadzenie",
            "Komunikacja i dowodzenie",
            "Gra w pojedynkach 1v1"
        ],
        "profiles": {
            "Sweeper Keeper": {"Gra nogami / Wprowadzenie": 0.45, "Wyjścia do dośrodkowań": 0.3, "Refleks na linii": 0.25},
            "Shot Stopper": {"Refleks na linii": 0.5, "Gra w pojedynkach 1v1": 0.3, "Komunikacja i dowodzenie": 0.2}
        }
    }
}

AVAILABLE_BADGES = [
    "⚡ Szybki / Dynamiczny",
    "🧠 Lider / Komunikatywny",
    "🛡️ Twardy w 1v1",
    "🎯 Precyzyjna noga",
    "🔋 Końskie płuca",
    "🚀 Świetny w powietrzu",
    "💎 Wysoka kultura gry",
    "🎯 Groźne stałe fragmenty",
    "⚠️ Wymaga pracy nad mentalem",
    "⚠️ Podatny na błędy pod presją"
]

TEXTS = {
    "Polski": {
        "title": "⚡ HÉRCULES CF 2.0",
        "subtitle": "System Oceniający Zawodników Akademickich i Pierwszego Zespołu",
        "nav_form": "📋 Formularz Oceny & Silnik Dopasowania",
        "nav_db": "🔍 Baza Zawodników & Karty",
        "nav_analytics": "📊 Analiza Taktyczna",
        "nav_settings": "⚙️ Ustawienia Systemu",
        "scout_opinion": "📝 Opinia i Rekomendacja Skauta",
        "badges_label": "📌 Przypinki i Cechy Charakterystyczne (Tagi):",
        "generate_btn": "⚙️ Przelicz Silnik i Wygeneruj Kartę Zawodnika",
        "card_title": "🃏 KARTA ZAWODNIKA (GENERATOR AKADEMII)",
        "matched_profile": "Główny Dopasowany Profil Taktyczny:",
        "save_db": "💾 Zapisz Kartę do Bazy Supabase"
    },
    "Español": {
        "title": "⚡ HÉRCULES CF 2.0",
        "subtitle": "Sistema de Evaluación de Jugadores de la Academia y Primer Equipo",
        "nav_form": "📋 Formulario de Evaluación y Motor de Perfiles",
        "nav_db": "🔍 Base de Datos y Tarjetas",
        "nav_analytics": "📊 Análisis Táctico",
        "nav_settings": "⚙️ Ajustes del Sistema",
        "scout_opinion": "📝 Opinión y Recomendación del Ojeador",
        "badges_label": "📌 Etiquetas y Características Clave (Tags):",
        "generate_btn": "⚙️ Calcular Motor y Generar Tarjeta",
        "card_title": "🃏 TARJETA DEL JUGADOR (GENERADOR ACADEMIA)",
        "matched_profile": "Perfil Táctico Principal Asignado:",
        "save_db": "💾 Guardar Tarjeta en la Base Supabase"
    }
}

# Połączenie Supabase
supabase_client = None
try:
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase_client = create_client(url, key)
    DB_CONNECTED = True
except Exception:
    DB_CONNECTED = False

# --- PRAWY GÓRNY RÓG: PRZEŁĄCZNIK JĘZYKA ---
col_head, col_lang = st.columns([5, 1])
with col_lang:
    selected_lang = st.selectbox("Idioma / Język", ["Polski", "Español"], label_visibility="collapsed")

t = TEXTS[selected_lang]

# --- NAWIGACJA BOCZNA ---
st.sidebar.markdown(f"# {t['title']}")
st.sidebar.markdown(f"*{t['subtitle']}*")
st.sidebar.markdown("---")

nav = st.sidebar.radio("Menu Operacyjne", [t["nav_form"], t["nav_db"], t["nav_analytics"], t["nav_settings"]])

st.sidebar.markdown("---")
if DB_CONNECTED:
    st.sidebar.success("🟢 Supabase DB: Online")
else:
    st.sidebar.error("🔴 Supabase DB: Offline")

# --- MODUŁ 1: FORMULARZ OCENY & SILNIK DOPASOWANIA ---
if nav == t["nav_form"]:
    st.title(t["nav_form"])
    st.markdown("Wybierz pozycję, aby załadować **dedykowany pakiet umiejętności (skala 1-10)** oraz przeliczyć profil taktyczny.")

    c1, c2, c3 = st.columns(3)
    with c1:
        fname = st.text_input("Imię zawodnika", "Jan")
        lname = st.text_input("Nazwisko zawodnika", "Kowalski")
    with c2:
        position = st.selectbox("Pozycja Na Boisku", list(POSITION_ENGINE.keys()))
        club = st.text_input("Obecny Klub", "Akademia Hercules")
    with c3:
        birth_year = st.number_input("Rocznik", 2000, 2016, 2008)
        foot = st.selectbox("Noga dominująca", ["Prawa", "Lewa", "Obustronny"])

    st.markdown("---")
    st.subheader("🎯 Dedykowany Pakiet Umiejętności Pozycyjnych (1.0 - 10.0)")

    # Dynamiczne ładowanie cech dla wybranej pozycji
    current_pos_data = POSITION_ENGINE[position]
    skills_list = current_pos_data["skills"]
    profiles_dict = current_pos_data["profiles"]

    user_scores = {}
    cols_skills = st.columns(3)
    for idx, skill in enumerate(skills_list):
        with cols_skills[idx % 3]:
            user_scores[skill] = st.slider(f"{skill}", 1.0, 10.0, 7.0, 0.5)

    st.markdown("---")
    selected_badges = st.multiselect(t["badges_label"], AVAILABLE_BADGES, default=[AVAILABLE_BADGES[0], AVAILABLE_BADGES[2]])
    scout_notes = st.text_area(t["scout_opinion"], "Zawodnik o bardzo dobrej strukturze decyzyjnej pod presją. Odpowiedni profil motoryczny.")

    # KALKULACJE SILNIKA MATEMATYCZNEGO
    avg_score = sum(user_scores.values()) / len(user_scores)
    cr = round(avg_score * 10, 1) # Przeliczenie na bazę 0-100
    pr = round(min(99.0, cr * 1.15), 1)
    index_ti = round(avg_score * 9.5, 1)

    # Wyliczanie dopasowania do profili taktycznych
    profile_matches = {}
    for prof_name, weights in profiles_dict.items():
        match_val = sum(user_scores[skill_name] * weight for skill_name, weight in weights.items())
        profile_matches[prof_name] = round((match_val / 10.0) * 100, 1)

    best_profile = max(profile_matches, key=profile_matches.get)

    st.markdown("---")
    if st.button(t["generate_btn"], type="primary"):
        st.markdown(f"""
        <div class="player-card">
            <h2 style="color: #60a5fa; margin-bottom: 0;">🃏 {fname} {lname} ({birth_year})</h2>
            <p style="color: #9ca3af; font-size: 16px;">Klub: <b>{club}</b> | Pozycja: <b>{position}</b> | Noga: <b>{foot}</b></p>
            <hr style="border-color: #374151;">
            <p style="font-size: 18px; color: #f3f4f6;">{t['matched_profile']} <b style="color: #34d399;">{best_profile} ({profile_matches[best_profile]}% dopasowania)</b></p>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Rating (CR)", f"{cr}")
        m2.metric("Potential Rating (PR)", f"{pr}")
        m3.metric("Index TI (Taktyka)", f"{index_ti}")
        m4.metric("Dopasowanie Profilowe", f"{profile_matches[best_profile]}%")

        # Wyświetlanie przypinek
        st.markdown("### 📌 Przypinki (Tagi) Zawodnika:")
        badges_html = "".join([f'<span class="badge-tag">{b}</span>' for b in selected_badges])
        st.markdown(badges_html, unsafe_allow_html=True)

        # Radar umiejętności
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=list(user_scores.values()) + [list(user_scores.values())[0]],
            theta=list(user_scores.keys()) + [list(user_scores.keys())[0]],
            fill='toself',
            name=f"{fname} {lname}",
            line_color='#3b82f6'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)

        # PRZYCISK ZAPISU DO SUPABASE
        if st.button(t["save_db"]):
            payload = {
                "first_name": fname,
                "last_name": lname,
                "birth_year": birth_year,
                "club": club,
                "position": position,
                "cr": cr,
                "pr": pr,
                "notes": f"[{best_profile}] Przypinki: {', '.join(selected_badges)} | Uwagi: {scout_notes}",
                "created_at": datetime.now().isoformat()
            }
            if DB_CONNECTED and supabase_client:
                try:
                    supabase_client.table("scouting_reports").insert(payload).execute()
                    st.success("Karta zawodnika pomyślnie zapisana w bazie Supabase!")
                except Exception as ex:
                    st.error(f"Błąd zapisu: {ex}")
            else:
                st.info("Karta zapisana w trybie podglądu (Lokalnie).")

# --- MODUŁ 2: BAZA ZAWODNIKÓW ---
elif nav == t["nav_db"]:
    st.title(t["nav_db"])
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
            {"first_name": "Pablo", "last_name": "Torres", "birth_year": 2008, "club": "Hércules U19", "position": "CB - Środkowy Obrońca", "cr": 72.0, "pr": 86.5, "notes": "[Ball-Playing Defender] Przypinki: ⚡ Szybki, 🧠 Lider"},
            {"first_name": "Adrian", "last_name": "Gomez", "birth_year": 2009, "club": "Elche CF", "position": "W - Skrzydłowy", "cr": 75.5, "pr": 89.0, "notes": "[Inverted Winger] Przypinki: 🛡️ Twardy w 1v1, 🎯 Precyzyjna noga"}
        ])

    st.dataframe(df, use_container_width=True)

# --- MODUŁ 3: ANALIZA TAKTYCZNA ---
elif nav == t["nav_analytics"]:
    st.title(t["nav_analytics"])
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(names=['Ball-Playing Defender', 'Box-to-Box', 'Inverted Winger', 'Target Man'], values=[30, 35, 20, 15], title="Rozkład Dopasowanych Profili Taktycznych")
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        fig_bar = px.bar(x=['2007', '2008', '2009', '2010'], y=[85.0, 82.1, 79.4, 77.0], title="Średni Potencjał PR w Rocznikach Akademickich")
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig_bar, use_container_width=True)

# --- MODUŁ 4: USTAWIENIA ---
elif nav == t["nav_settings"]:
    st.title(t["nav_settings"])
    st.json({
        "System": "Hércules CF Scouting Engine 2.0",
        "Scale": "Position Specific (1.0 - 10.0)",
        "Database Status": "Online" if DB_CONNECTED else "Offline"
    })
