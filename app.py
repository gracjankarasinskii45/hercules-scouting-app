import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Konfiguracja strony
st.set_page_config(
    page_title="HÉRCULES DE ALICANTE C.F. | Scouting Portal",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STYLIZACJA CSS (OFICJALNY PORTAL HÉRCULES CF) ---
st.markdown("""
    <style>
    /* Główna paleta barw Hércules C.F.: Granat (#001b44), Błękit (#0055ff), Złoto (#d4af37), Biel (#f8fafc) */
    .stApp {
        background-color: #080d1a;
        color: #1e293b;
    }
    
    /* Górny Belka Klubowa */
    .club-header {
        background: linear-gradient(90deg, #020b1e 0%, #002255 50%, #020b1e 100%);
        padding: 15px 30px;
        border-bottom: 3px solid #d4af37;
        margin: -60px -50px 25px -50px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    .club-title {
        color: #ffffff;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: 900;
        letter-spacing: 2px;
        margin: 0;
        font-size: 22px;
        text-transform: uppercase;
    }
    
    /* Ekran Powitalny / Hero Section */
    .hero-container {
        text-align: center;
        padding: 40px 20px;
        background: radial-gradient(circle, rgba(0,56,130,0.4) 0%, rgba(8,13,26,0.95) 70%);
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.3);
        margin: 20px auto;
        max-width: 850px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }
    
    .hero-logo {
        width: 140px;
        margin-bottom: 20px;
        filter: drop-shadow(0px 8px 16px rgba(0,0,0,0.7));
    }
    
    .hero-heading {
        color: #ffffff;
        font-size: 32px;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    
    .hero-sub {
        color: #94a3b8;
        font-size: 16px;
        margin-bottom: 25px;
    }

    /* Karty Treści w Stylu Artykułów / Portalowym */
    .content-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 28px;
        color: #0f172a;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 25px;
        border-top: 4px solid #003882;
    }
    
    .content-card h1, .content-card h2, .content-card h3 {
        color: #002255 !important;
        font-weight: 800;
    }

    /* Karta Zawodnika (Player Card) */
    .player-card-result {
        background: linear-gradient(135deg, #001f4d 0%, #000c24 100%);
        border: 2px solid #d4af37;
        border-radius: 16px;
        padding: 25px;
        color: #ffffff;
        margin-top: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.5);
    }
    
    .badge-tag {
        display: inline-block;
        background-color: #003882;
        color: #ffffff;
        padding: 5px 14px;
        border-radius: 15px;
        font-size: 13px;
        margin: 4px;
        border: 1px solid #d4af37;
        font-weight: 600;
    }
    
    /* Modyfikacja paska Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# URL Logo Hércules CF
HERCULES_LOGO_URL = "https://upload.wikimedia.org/wikipedia/en/thumb/0/02/Hercules_CF_logo.svg/1200px-Hercules_CF_logo.svg.png"

# --- SILNIK POZYCYJNY & UMIEJĘTNOŚCI (1-10) ---
POSITION_ENGINE = {
    "CB - Środkowy Obrońca": {
        "skills": ["Gra w powietrzu / Główki", "Pojedynki 1v1 defensywne", "Ustawianie się / Asekuracja", "Wprowadzanie piłki / Podanie", "Szybkość na krótkim dystansie", "Decyzyjność pod presją"],
        "profiles": {
            "Ball-Playing Defender": {"Wprowadzanie piłki / Podanie": 0.4, "Decyzyjność pod presją": 0.3, "Ustawianie się / Asekuracja": 0.3},
            "Stopper Agresywny": {"Pojedynki 1v1 defensywne": 0.4, "Gra w powietrzu / Główki": 0.4, "Szybkość na krótkim dystansie": 0.2},
            "Covering Defender (Asekurujący)": {"Ustawianie się / Asekuracja": 0.4, "Szybkość na krótkim dystansie": 0.4, "Decyzyjność pod presją": 0.2}
        }
    },
    "CM - Środkowy Pomocnik": {
        "skills": ["Przegląd pola i wizja", "Kultura podania (krótkie/długie)", "Odbiór i pressing", "Odporność na pressing", "Wydolność / Mobilność", "Decyzyjność i czas reakcji"],
        "profiles": {
            "Deep-Lying Playmaker": {"Kultura podania (krótkie/długie)": 0.4, "Przegląd pola i wizja": 0.4, "Odporność na pressing": 0.2},
            "Box-to-Box": {"Wydolność / Mobilność": 0.4, "Odbiór i pressing": 0.3, "Decyzyjność i czas reakcji": 0.3},
            "Advanced Playmaker": {"Przegląd pola i wizja": 0.4, "Odporność na pressing": 0.3, "Kultura podania (krótkie/długie)": 0.3}
        }
    },
    "W - Skrzydłowy": {
        "skills": ["Pojedynki 1v1 (Drybling)", "Szybkość i przyspieszenie", "Dośrodkowanie / Dogranie", "Wykończenie akcji", "Praca w defensywie", "Schodzenie do środka"],
        "profiles": {
            "Inverted Winger": {"Pojedynki 1v1 (Drybling)": 0.35, "Schodzenie do środka": 0.35, "Wykończenie akcji": 0.3},
            "Classic Winger": {"Szybkość i przyspieszenie": 0.4, "Dośrodkowanie / Dogranie": 0.4, "Pojedynki 1v1 (Drybling)": 0.2},
            "Wide Playmaker": {"Dośrodkowanie / Dogranie": 0.4, "Schodzenie do środka": 0.3, "Praca w defensywie": 0.3}
        }
    },
    "CF - Napastnik": {
        "skills": ["Wykończenie 1v1 / Strzał", "Gra tyłem do bramki", "Ruch bez piłki / Asekuracja", "Gra głową w polu karnym", "Pressing i intensywność", "Szybkość wyjścia na pozycję"],
        "profiles": {
            "Target Man": {"Gra tyłem do bramki": 0.4, "Gra głową w polu karnym": 0.4, "Wykończenie 1v1 / Strzał": 0.2},
            "Poacher (Lis pola karnego)": {"Wykończenie 1v1 / Strzał": 0.4, "Ruch bez piłki / Asekuracja": 0.4, "Szybkość wyjścia na pozycję": 0.2},
            "Pressing Forward": {"Pressing i intensywność": 0.4, "Szybkość wyjścia na pozycję": 0.3, "Ruch bez piłki / Asekuracja": 0.3}
        }
    },
    "RB/LB - Boczny Obrońca": {
        "skills": ["Szybkość i wytrzymałość", "Gra w defensywie 1v1", "Podłączenie się do ataku", "Dośrodkowanie z biegu", "Taktyczne powroty"],
        "profiles": {
            "Offensive Wingback": {"Podłączenie się do ataku": 0.4, "Dośrodkowanie z biegu": 0.35, "Szybkość i wytrzymałość": 0.25},
            "Defensive Fullback": {"Gra w defensywie 1v1": 0.45, "Taktyczne powroty": 0.35, "Szybkość i wytrzymałość": 0.2}
        }
    },
    "GK - Bramkarz": {
        "skills": ["Refleks na linii", "Wyjścia do dośrodkowań", "Gra nogami / Wprowadzenie", "Komunikacja i dowodzenie", "Gra w pojedynkach 1v1"],
        "profiles": {
            "Sweeper Keeper": {"Gra nogami / Wprowadzenie": 0.45, "Wyjścia do dośrodkowań": 0.3, "Refleks na linii": 0.25},
            "Shot Stopper": {"Refleks na linii": 0.5, "Gra w pojedynkach 1v1": 0.3, "Komunikacja i dowodzenie": 0.2}
        }
    }
}

AVAILABLE_BADGES = [
    "⚡ Szybki / Dynamiczny", "🧠 Lider / Komunikatywny", "🛡️ Twardy w 1v1",
    "🎯 Precyzyjna noga", "🔋 Końskie płuca", "🚀 Świetny w powietrzu",
    "💎 Wysoka kultura gry", "🎯 Groźne stałe fragmenty", "⚠️ Wymaga pracy nad mentalem"
]

TEXTS = {
    "Polski": {
        "portal_name": "HÉRCULES DE ALICANTE C.F.",
        "welcome_title": "DEPARTAMENT SKAUTINGU I ANALIZY",
        "welcome_sub": "Oficjalna platforma analityczna Akademii i Pierwszego Zespołu",
        "enter_btn": "WEJDŹ DO SYSTEMU SKAUTINGOWEGO",
        "nav_1": "📋 Nowy Raport",
        "nav_2": "🔍 Baza Zawodników",
        "nav_3": "📊 Analiza Kadr",
        "nav_4": "⚙️ Ustawienia",
        "calc_btn": "⚙️ PRZELICZ SILNIK I WYGENERUJ KARTĘ ZAWODNIKA",
        "save_db": "💾 Zapisz Kartę do Supabase"
    },
    "Español": {
        "portal_name": "HÉRCULES DE ALICANTE C.F.",
        "welcome_title": "DEPARTAMENTO DE SCOUTING Y ANALÍTICA",
        "welcome_sub": "Plataforma oficial de análisis de la Academia y Primer Equipo",
        "enter_btn": "ACCEDER AL SISTEMA DE SCOUTING",
        "nav_1": "📋 Nuevo Informe",
        "nav_2": "🔍 Base de Datos",
        "nav_3": "📊 Análisis de Plantilla",
        "nav_4": "⚙️ Ajustes",
        "calc_btn": "⚙️ CALCULAR MOTOR Y GENERAR TARJETA",
        "save_db": "💾 Guardar Tarjeta en Supabase"
    }
}

# Inicjalizacja stanu
if "entered" not in st.session_state:
    st.session_state.entered = False
if "lang" not in st.session_state:
    st.session_state.lang = "Polski"

# Supabase
supabase_client = None
try:
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase_client = create_client(url, key)
    DB_OK = True
except Exception:
    DB_OK = False

# --- EKRAN POWITALNY (HERO LANDING PANEL Z HERBEM NA ŚRODKU) ---
if not st.session_state.entered:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 3, 1])
    with col_l2:
        st.markdown(f"""
        <div class="hero-container">
            <img src="{HERCULES_LOGO_URL}" class="hero-logo" alt="Hércules CF Logo">
            <div class="hero-heading">HÉRCULES DE ALICANTE C.F.</div>
            <div class="hero-sub">DEPARTAMENT SKAUTINGU & AKADEMIA TALENTÓW</div>
            <p style="color: #cbd5e1; font-size: 14px; margin-bottom: 25px;">
                Oficjalny system analizy zawodników, dobierania profili taktycznych oraz ewaluacji potencjału.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
        with c_btn2:
            st.session_state.lang = st.selectbox("Idioma / Język", ["Polski", "Español"])
            if st.button("⚡ WEJDŹ DO SYSTEMU", type="primary"):
                st.session_state.entered = True
                st.rerun()
    st.stop()

# --- GÓRNY PASEK KLUBOWY (TOP NAVIGATION PORTAL) ---
t = TEXTS[st.session_state.lang]

col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        <img src="{HERCULES_LOGO_URL}" style="height: 50px;">
        <div>
            <h2 style="color: #ffffff; margin: 0; padding: 0; font-size: 22px; font-weight: 800;">{t['portal_name']}</h2>
            <span style="color: #d4af37; font-size: 13px; font-weight: 600;">PORTAL SKAUTINGOWY & BAZA ANALITYCZNA</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    st.session_state.lang = st.selectbox("Język / Lang", ["Polski", "Español"], label_visibility="collapsed")

# Zakładki jak na portalu informacyjnym
tab_form, tab_db, tab_analytics, tab_settings = st.tabs([t["nav_1"], t["nav_2"], t["nav_3"], t["nav_4"]])

# --- ZAKŁADKA 1: NOWY RAPORT (PORTAL FORM) ---
with tab_form:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📋 Formularz Oceny Zawodnika & Silnik Dopasowania")
    st.write("Wpisz dane zawodnika, wybierz pozycję i oceń dedykowany pakiet umiejętności w skali **1.0 - 10.0**.")

    col1, col2, col3 = st.columns(3)
    with col1:
        fname = st.text_input("Imię zawodnika", "Jan")
        lname = st.text_input("Nazwisko zawodnika", "Kowalski")
    with col2:
        position = st.selectbox("Pozycja Na Boisku", list(POSITION_ENGINE.keys()))
        club = st.text_input("Obecny Klub", "Akademia Hercules")
    with col3:
        birth_year = st.number_input("Rocznik", 2000, 2016, 2008)
        foot = st.selectbox("Noga dominująca", ["Prawa", "Lewa", "Obustronny"])

    st.markdown("---")
    st.markdown("### 🎯 Ocena Umiejętności Pozycyjnych (1.0 - 10.0)")

    pos_data = POSITION_ENGINE[position]
    skills_list = pos_data["skills"]
    profiles_dict = pos_data["profiles"]

    user_scores = {}
    cols_skills = st.columns(3)
    for idx, skill in enumerate(skills_list):
        with cols_skills[idx % 3]:
            user_scores[skill] = st.slider(f"{skill}", 1.0, 10.0, 7.0, 0.5)

    st.markdown("---")
    selected_badges = st.multiselect("📌 Przypinki i Cechy (Tagi):", AVAILABLE_BADGES, default=[AVAILABLE_BADGES[0], AVAILABLE_BADGES[2]])
    scout_notes = st.text_area("📝 Opinia i Rekomendacja Skauta:", "Zawodnika cechuje duża powtarzalność i opór na pressing w fazie budowania.")

    # Obliczenia silnika
    avg_score = sum(user_scores.values()) / len(user_scores)
    cr = round(avg_score * 10, 1)
    pr = round(min(99.0, cr * 1.15), 1)
    index_ti = round(avg_score * 9.5, 1)

    profile_matches = {}
    for prof_name, weights in profiles_dict.items():
        match_val = sum(user_scores[skill_name] * weight for skill_name, weight in weights.items())
        profile_matches[prof_name] = round((match_val / 10.0) * 100, 1)

    best_profile = max(profile_matches, key=profile_matches.get)

    if st.button(t["calc_btn"], type="primary"):
        st.markdown(f"""
        <div class="player-card-result">
            <h2 style="color: #60a5fa; margin-top:0;">🃏 {fname} {lname} ({birth_year})</h2>
            <p style="color: #cbd5e1;">Klub: <b>{club}</b> | Pozycja: <b>{position}</b> | Noga: <b>{foot}</b></p>
            <hr style="border-color: #1e3a8a;">
            <p style="font-size: 18px; color: #f8fafc;">Główny Profil Taktyczny: <b style="color: #34d399;">{best_profile} ({profile_matches[best_profile]}% dopasowania)</b></p>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Rating (CR)", f"{cr}")
        m2.metric("Potential Rating (PR)", f"{pr}")
        m3.metric("Index TI", f"{index_ti}")
        m4.metric("Dopasowanie Profilu", f"{profile_matches[best_profile]}%")

        st.markdown("**Wybrane przypinki:**")
        badges_html = "".join([f'<span class="badge-tag">{b}</span>' for b in selected_badges])
        st.markdown(badges_html, unsafe_allow_html=True)

        # Wykres Radarowy
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=list(user_scores.values()) + [list(user_scores.values())[0]],
            theta=list(user_scores.keys()) + [list(user_scores.keys())[0]],
            fill='toself',
            name=f"{fname} {lname}",
            line_color='#0055ff'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='black')
        )
        st.plotly_chart(fig, use_container_width=True)

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
            if DB_OK and supabase_client:
                try:
                    supabase_client.table("scouting_reports").insert(payload).execute()
                    st.success("Karta zawodnika pomyślnie zapisana w bazie Supabase!")
                except Exception as ex:
                    st.error(f"Błąd zapisu: {ex}")
            else:
                st.info("Karta wygenerowana i gotowa do zapisu.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ZAKŁADKA 2: BAZA ZAWODNIKÓW ---
with tab_db:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("🔍 Centralna Baza Obserwowanych Talentów")
    df = pd.DataFrame()
    if DB_OK and supabase_client:
        try:
            res = supabase_client.table("scouting_reports").select("*").execute()
            if res.data:
                df = pd.DataFrame(res.data)
        except Exception:
            pass

    if df.empty:
        df = pd.DataFrame([
            {"first_name": "Pablo", "last_name": "Torres", "birth_year": 2008, "club": "Hércules U19", "position": "CB - Środkowy Obrońca", "cr": 72.0, "pr": 86.5, "notes": "[Ball-Playing Defender] Przypinki: ⚡ Szybki, 🧠 Lider"},
            {"first_name": "Adrian", "last_name": "Gomez", "birth_year": 2009, "club": "Elche CF", "position": "W - Skrzydłowy", "cr": 75.5, "pr": 89.0, "notes": "[Inverted Winger] Przypinki: 🛡️ Twardy w 1v1"}
        ])

    st.dataframe(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- ZAKŁADKA 3: ANALIZA ---
with tab_analytics:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📊 Analiza Kadr i Rozkład Profili Taktycznych")
    c_a, c_b = st.columns(2)
    with c_a:
        fig_pie = px.pie(names=['Ball-Playing Defender', 'Box-to-Box', 'Inverted Winger', 'Target Man'], values=[30, 35, 20, 15], title="Rozkład Dopasowania Profili Taktycznych")
        st.plotly_chart(fig_pie, use_container_width=True)
    with c_b:
        fig_bar = px.bar(x=['2007', '2008', '2009', '2010'], y=[85.0, 82.1, 79.4, 77.0], title="Średni Potencjał PR w Rocznikach Akademickich")
        st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- ZAKŁADKA 4: USTAWIENIA ---
with tab_settings:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("⚙️ Status Portalu Skautingowego")
    st.json({
        "Club": "Hércules de Alicante C.F.",
        "System": "Portal Skautingowy & Baza Danych 2.0",
        "Supabase Database": "Connected" if DB_OK else "Offline"
    })
    st.markdown('</div>', unsafe_allow_html=True)
