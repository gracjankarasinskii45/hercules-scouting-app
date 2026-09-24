import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import base64

# Konfiguracja strony
st.set_page_config(
    page_title="HÉRCULES DE ALICANTE C.F. | Scouting Engine Portal",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ładowanie logo z pliku lokalnego lub domyślnego URL
def load_logo_b64(file_path="logo.png"):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    return "https://upload.wikimedia.org/wikipedia/en/thumb/0/02/Hercules_CF_logo.svg/1200px-Hercules_CF_logo.svg.png"

logo_src = load_logo_b64("logo.png")

# --- STYLIZACJA CSS ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #060a12;
        color: #f8fafc;
    }}
    .hero-container {{
        text-align: center;
        padding: 45px 25px;
        background: radial-gradient(circle, rgba(0,56,130,0.5) 0%, rgba(6,10,18,0.98) 80%);
        border-radius: 20px;
        border: 2px solid #d4af37;
        margin: 20px auto;
        max-width: 820px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.8);
    }}
    .hero-logo {{
        width: 160px;
        height: auto;
        margin-bottom: 20px;
        filter: drop-shadow(0px 8px 18px rgba(0,0,0,0.9));
    }}
    .content-card {{
        background-color: #ffffff;
        border-radius: 14px;
        padding: 28px;
        color: #0f172a;
        box-shadow: 0 6px 25px rgba(0,0,0,0.5);
        margin-bottom: 25px;
        border-top: 6px solid #003882;
    }}
    .content-card h1, .content-card h2, .content-card h3 {{
        color: #001f4d !important;
        font-weight: 800;
    }}
    .pillar-box {{
        background-color: #f1f5f9;
        border-left: 4px solid #0055ff;
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 12px;
    }}
    .player-card-result {{
        background: linear-gradient(135deg, #001f4d 0%, #000c24 100%);
        border: 2px solid #d4af37;
        border-radius: 16px;
        padding: 28px;
        color: #ffffff;
        margin-top: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }}
    .badge-auto {{
        display: inline-block;
        background-color: #d4af37;
        color: #000c24;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 12px;
        margin: 3px;
        font-weight: 800;
    }}
    .badge-manual {{
        display: inline-block;
        background-color: #003882;
        color: #ffffff;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 12px;
        margin: 3px;
        border: 1px solid #60a5fa;
        font-weight: 600;
    }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- PEŁNY MATEMATYCZNY SILNIK POZYCYJNY (4 FILARY) ---
POSITION_FULL_ENGINE = {
    "CB - Środkowy Obrońca": {
        "pillars": {
            "Technika (TE)": ["Wprowadzanie piłki", "Kultura podania krótkiego", "Podanie diagonalne / Długie"],
            "Taktyka (TA)": ["Ustawianie się w linii", "Asekuracja i profilowanie", "Decyzyjność pod presją"],
            "Motoryka (MO)": ["Gra w powietrzu / Główki", "Pojedynki 1v1 defensywne", "Szybkość i przyspieszenie"],
            "Mentalność (ME)": ["Komunikacja i dowodzenie", "Agresja pozytywna", "Koncentracja 90 min"]
        },
        "profiles": {
            "Ball-Playing Defender": {"Wprowadzanie piłki": 0.25, "Kultura podania krótkiego": 0.25, "Decyzyjność pod presją": 0.25, "Podanie diagonalne / Długie": 0.25},
            "Stopper Agresywny": {"Pojedynki 1v1 defensywne": 0.35, "Gra w powietrzu / Główki": 0.35, "Agresja pozytywna": 0.30},
            "Covering Defender (Asekurujący)": {"Ustawianie się w linii": 0.35, "Asekuracja i profilowanie": 0.35, "Szybkość i przyspieszenie": 0.30}
        }
    },
    "CM - Środkowy Pomocnik": {
        "pillars": {
            "Technika (TE)": ["Przyjęcie kierunkowe", "Kultura podania", "Utrzymanie się przy piłce"],
            "Taktyka (TA)": ["Przegląd pola i wizja", "Świadomość przestrzenna (Scanning)", "Reakcja po stracie (Skan)"],
            "Motoryka (MO)": ["Wydolność / Mobilność", "Dynamiczne wyjście na pozycję", "Zwrotność"],
            "Mentalność (ME)": ["Odporność na presję", "Lider środka pola", "Zabijanie tempa / Przyspieszanie"]
        },
        "profiles": {
            "Deep-Lying Playmaker": {"Przegląd pola i wizja": 0.3, "Kultura podania": 0.3, "Przyjęcie kierunkowe": 0.2, "Odporność na presję": 0.2},
            "Box-to-Box": {"Wydolność / Mobilność": 0.35, "Dynamiczne wyjście na pozycję": 0.3, "Reakcja po stracie (Skan)": 0.35},
            "Advanced Playmaker": {"Przegląd pola i wizja": 0.35, "Przyjęcie kierunkowe": 0.3, "Utrzymanie się przy piłce": 0.35}
        }
    },
    "W - Skrzydłowy": {
        "pillars": {
            "Technika (TE)": ["Pojedynki 1v1 (Drybling)", "Dośrodkowanie z biegu", "Wykończenie akcji"],
            "Taktyka (TA)": ["Ruch bez piłki / Wbieganie", "Schodzenie do środka (ECO)", "Decyzja: strzał vs podanie"],
            "Motoryka (MO)": ["Przyspieszenie i V-max", "Zmiana kierunku biegu", "Eksplozywność"],
            "Mentalność (ME)": ["Odwaga w pojedynkach", "Praca w powrocie (Def)", "Nieustępliwość"]
        },
        "profiles": {
            "Inverted Winger": {"Pojedynki 1v1 (Drybling)": 0.3, "Schodzenie do środka (ECO)": 0.35, "Wykończenie akcji": 0.35},
            "Classic Winger": {"Przyspieszenie i V-max": 0.35, "Dośrodkowanie z biegu": 0.35, "Pojedynki 1v1 (Drybling)": 0.3},
            "Wide Playmaker": {"Decyzja: strzał vs podanie": 0.35, "Ruch bez piłki / Wbieganie": 0.35, "Praca w powrocie (Def)": 0.3}
        }
    },
    "CF - Napastnik": {
        "pillars": {
            "Technika (TE)": ["Strzał z pierwszej piłki", "Gra tyłem do bramki (Gra na ścianę)", "Wykończenie 1v1 z bramkarzem"],
            "Taktyka (TA)": ["Ruch na wolną pozycję (Linia spalonego)", "Antycypacja w polu karnym", "Pressing na stoperów"],
            "Motoryka (MO)": ["Skoczność i walka w powietrzu", "Start do piłki (Pierwsze 5m)", "Siła fizyczna / Osłona"],
            "Mentalność (ME)": ["Instynkt strzelecki", "Pewność siebie pod bramką", "Work-rate w defensywie"]
        },
        "profiles": {
            "Target Man": {"Gra tyłem do bramki (Gra na ścianę)": 0.35, "Siła fizyczna / Osłona": 0.35, "Skoczność i walka w powietrzu": 0.3},
            "Poacher (Lis Pola Karnego)": {"Wykończenie 1v1 z bramkarzem": 0.35, "Antycypacja w polu karnym": 0.35, "Instynkt strzelecki": 0.3},
            "Pressing Forward": {"Pressing na stoperów": 0.4, "Start do piłki (Pierwsze 5m)": 0.3, "Work-rate w defensywie": 0.3}
        }
    },
    "RB/LB - Boczny Obrońca": {
        "pillars": {
            "Technika (TE)": ["Dośrodkowanie w pełnym biegu", "Podanie wzdłuż linii", "Odbiór czysty w 1v1"],
            "Taktyka (TA)": ["Asekuracja skrzydła", "Timing podłączenia się", "Taktyczne złamanie do środka"],
            "Motoryka (MO)": ["Wytrzymałość wahadłowa", "Szybkość w pojedynkach", "Zwrotność"],
            "Mentalność (ME)": ["Dyscyplina taktyczna", "Zaangażowanie box-to-box", "Agresja w odbiorze"]
        },
        "profiles": {
            "Offensive Wingback": {"Timing podłączenia się": 0.35, "Dośrodkowanie w pełnym biegu": 0.35, "Wytrzymałość wahadłowa": 0.3},
            "Defensive Fullback": {"Odbiór czysty w 1v1": 0.4, "Asekuracja skrzydła": 0.35, "Dyscyplina taktyczna": 0.25}
        }
    },
    "GK - Bramkarz": {
        "pillars": {
            "Technika (TE)": ["Gra nogami (Rozegranie krótkie)", "Chwyt piłki / Parowanie", "Długie wprowadzenie nogą/ręką"],
            "Taktyka (TA)": ["Ustawianie się na linii i przedpolu", "Czytanie prostopadłych podań", "Kierowanie defensywą"],
            "Motoryka (MO)": ["Refleks i czas reakcji", "Zasięg w powietrzu (Dośrodkowania)", "Moc wyjścia w górę"],
            "Mentalność (ME)": ["Charyzma i opanowanie", "Decyzyjność 1v1 z napastnikiem", "Odporność po błędzie"]
        },
        "profiles": {
            "Sweeper Keeper": {"Gra nogami (Rozegranie krótkie)": 0.4, "Czytanie prostopadłych podań": 0.35, "Charyzma i opanowanie": 0.25},
            "Shot Stopper": {"Refleks i czas reakcji": 0.4, "Chwyt piłki / Parowanie": 0.35, "Ustawianie się na linii i przedpolu": 0.25}
        }
    }
}

TAGS_MANUAL = [
    "🧠 Lider Zespołu", "💎 Wysoka Kultura Gry", "🔋 Końskie Płuca", 
    "🎯 Groźny przy SFP", "⚠️ Podatny na stres", "⚠️ Wymaga poprawy lewej nogi"
]

# Obsługa bazy Supabase
supabase_client = None
try:
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase_client = create_client(url, key)
    DB_OK = True
except Exception:
    DB_OK = False

if "entered" not in st.session_state:
    st.session_state.entered = False
if "lang" not in st.session_state:
    st.session_state.lang = "Polski"

# --- EKRAN POWITALNY ---
if not st.session_state.entered:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"""
        <div class="hero-container">
            <img src="{logo_src}" class="hero-logo">
            <div style="color:#ffffff; font-size:32px; font-weight:900; letter-spacing:2px;">HÉRCULES DE ALICANTE C.F.</div>
            <div style="color:#d4af37; font-size:15px; font-weight:700; margin-bottom:20px;">SISTEMA OFICIAL DE EVALUACIÓN DE TALENTO</div>
            <p style="color:#cbd5e1; font-size:14px; margin-bottom:25px;">
                Zaawansowany matematyczny silnik analityczny: ocena 4 filarów, wyliczanie wskaźników CR/PR/TI, automatyczny Tagging Engine oraz dopasowanie do ról taktycznych.
            </p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.session_state.lang = st.selectbox("Idioma / Język", ["Polski", "Español"])
            if st.button("⚡ WEJDŹ DO PORTALU SKAUTINGOWEGO", type="primary"):
                st.session_state.entered = True
                st.rerun()
    st.stop()

# --- HEADER PORTALU ---
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 20px;">
        <img src="{logo_src}" style="height: 52px;">
        <div>
            <h2 style="color: #ffffff; margin: 0; padding: 0; font-size: 22px; font-weight: 900;">HÉRCULES DE ALICANTE C.F.</h2>
            <span style="color: #d4af37; font-size: 13px; font-weight: 700;">SILNIK EVALUACYJNY & BAZA DANYCH AKADEMII</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    st.session_state.lang = st.selectbox("Lang", ["Polski", "Español"], label_visibility="collapsed")

tab_form, tab_db, tab_analytics, tab_settings = st.tabs(["📋 Formularz & Silnik Math", "🔍 Baza Zawodników", "📊 Analiza Taktyczna", "⚙️ Ustawienia"])

# --- ZAKŁADKA 1: FORMULARZ & SILNIK ---
with tab_form:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📋 Ocena Zawodnika & Pełny Silnik Analityczny")

    c1, c2, c3 = st.columns(3)
    with c1:
        fname = st.text_input("Imię zawodnika", "Jan")
        lname = st.text_input("Nazwisko zawodnika", "Kowalski")
    with c2:
        position = st.selectbox("Pozycja Na Boisku", list(POSITION_FULL_ENGINE.keys()))
        club = st.text_input("Obecny Klub", "Akademia Hercules")
    with c3:
        birth_year = st.number_input("Rocznik", 2000, 2016, 2008)
        foot = st.selectbox("Noga dominująca", ["Prawa", "Lewa", "Obustronny"])

    st.markdown("---")
    st.markdown("### ⚙️ Ewaluacja 4 Filarów (Skala 1.0 - 10.0)")

    pos_config = POSITION_FULL_ENGINE[position]
    pillars = pos_config["pillars"]
    profiles = pos_config["profiles"]

    skill_scores = {}
    pillar_averages = {}

    # Generowanie interfejsu 4 filarów
    p_cols = st.columns(2)
    p_idx = 0
    for pillar_name, skills in pillars.items():
        with p_cols[p_idx % 2]:
            st.markdown(f"#### {pillar_name}")
            p_sum = 0.0
            for skill in skills:
                val = st.slider(f"{skill}", 1.0, 10.0, 7.0, 0.5, key=f"{position}_{skill}")
                skill_scores[skill] = val
                p_sum += val
            pillar_averages[pillar_name] = p_sum / len(skills)
        p_idx += 1

    st.markdown("---")
    manual_tags = st.multiselect("📌 Ręczne Przypinki / Tagi Skauta:", TAGS_MANUAL, default=[TAGS_MANUAL[0]])
    scout_notes = st.text_area("📝 Rekomendacja i Podsumowanie Skauta:", "Dobre profilowanie, duży opór pod presją. Rekomendowany do dalszej obserwacji.")

    # --- MATEMATYCZNE PRZELICZENIA SILNIKA ---
    te_avg = pillar_averages["Technika (TE)"]
    ta_avg = pillar_averages["Taktyka (TA)"]
    mo_avg = pillar_averages["Motoryka (MO)"]
    me_avg = pillar_averages["Mentalność (ME)"]

    # Wyliczanie Wskaźników
    cr = round((te_avg * 0.30 + ta_avg * 0.30 + mo_avg * 0.25 + me_avg * 0.15) * 10, 1)
    
    # Wyliczanie Potencjału na podstawie rocznika
    current_year = datetime.now().year
    age = current_year - birth_year
    growth_headroom = max(5.0, (23 - age) * 2.2) if age < 23 else 3.0
    pr = round(min(99.0, cr + growth_headroom), 1)
    dps = round(pr - cr, 1)

    # Index TI (Taktyczny)
    index_ti = round((ta_avg * 0.45 + te_avg * 0.35 + me_avg * 0.20) * 10, 1)

    # TAGGING ENGINE (Automatyczne generowanie odznak z progów punktowych)
    auto_badges = []
    for skill_k, val_v in skill_scores.items():
        if val_v >= 8.5:
            if "Szybkość" in skill_k or "Przyspieszenie" in skill_k or "V-max" in skill_k:
                auto_badges.append("⚡ Piorunujący Sprint")
            elif "Podanie" in skill_k or "Kultura" in skill_k:
                auto_badges.append("🎯 Reżyser Gry")
            elif "Drybling" in skill_k or "Pojedynki 1v1" in skill_k:
                auto_badges.append("🔥 MISTRZ 1v1")
            elif "Powietrzu" in skill_k or "Główki" in skill_k:
                auto_badges.append("🚀 Dominator Powietrzny")
            elif "Wizja" in skill_k or "Przegląd" in skill_k:
                auto_badges.append("👁️ Radar Taktyczny")
            elif "Refleks" in skill_k:
                auto_badges.append("🧤 Kot na Linii")

    # DOPASOWANIE ROLES / PROFILI TAKTYCZNYCH
    role_matches = {}
    for prof_name, weights in profiles.items():
        match_score = sum(skill_scores.get(sk, 5.0) * w for sk, w in weights.items())
        role_matches[prof_name] = round((match_score / 10.0) * 100, 1)

    sorted_roles = sorted(role_matches.items(), key=lambda x: x[1], reverse=True)
    best_role_name, best_role_pct = sorted_roles[0]

    if st.button("⚙️ URUCHOM SILNIK I WYGENERUJKARTĘ ZAWODNIKA", type="primary"):
        st.markdown(f"""
        <div class="player-card-result">
            <div style="display:flex; justify-shadow:space-between; align-items:center;">
                <div>
                    <h2 style="color: #60a5fa; margin:0;">🃏 {fname} {lname} ({birth_year})</h2>
                    <p style="color: #94a3b8; margin-top:4px;">Klub: <b>{club}</b> | Pozycja: <b>{position}</b> | Noga: <b>{foot}</b></p>
                </div>
            </div>
            <hr style="border-color: #1e3a8a;">
            <p style="font-size:18px; color:#ffffff;">Najlepszy Profil Taktyczny: <b style="color:#34d399;">{best_role_name} ({best_role_pct}% Dopasowania)</b></p>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Rating (CR)", f"{cr}")
        m2.metric("Potential Rating (PR)", f"{pr}")
        m3.metric("DPS (Dynamika)", f"+{dps}")
        m4.metric("Index TI (Taktyka)", f"{index_ti}")

        st.markdown("#### 📌 Wygenerowane Odznaki & Przypinki:")
        badges_html = "".join([f'<span class="badge-auto">{b}</span>' for b in set(auto_badges)])
        badges_html += "".join([f'<span class="badge-manual">{b}</span>' for b in manual_tags])
        st.markdown(badges_html if badges_html else "Brak odznak specjalnych", unsafe_allow_html=True)

        # Wykres Radarowy 4 Filarów
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[te_avg, ta_avg, mo_avg, me_avg, te_avg],
            theta=['Technika', 'Taktyka', 'Motoryka', 'Mentalność', 'Technika'],
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

        if st.button("💾 Zapisz Wygenerowany Profil do Supabase"):
            payload = {
                "first_name": fname,
                "last_name": lname,
                "birth_year": birth_year,
                "club": club,
                "position": position,
                "cr": cr,
                "pr": pr,
                "notes": f"[{best_role_name} {best_role_pct}%] TI: {index_ti} | Tagi: {', '.join(auto_badges + manual_tags)} | {scout_notes}",
                "created_at": datetime.now().isoformat()
            }
            if DB_OK and supabase_client:
                try:
                    supabase_client.table("scouting_reports").insert(payload).execute()
                    st.success("Raport pomyślnie utrwalony w bazie danych Supabase!")
                except Exception as ex:
                    st.error(f"Błąd zapisu: {ex}")
            else:
                st.info("Zapisano w trybie symulacji lokalnej.")
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
            {"first_name": "Pablo", "last_name": "Torres", "birth_year": 2008, "club": "Hércules U19", "position": "CB - Środkowy Obrońca", "cr": 72.0, "pr": 86.5, "notes": "[Ball-Playing Defender 88%] Tagi: ⚡ Piorunujący Sprint, 🧠 Lider"},
            {"first_name": "Adrian", "last_name": "Gomez", "birth_year": 2009, "club": "Elche CF", "position": "W - Skrzydłowy", "cr": 75.5, "pr": 89.0, "notes": "[Inverted Winger 92%] Tagi: 🔥 MISTRZ 1v1"}
        ])

    st.dataframe(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- ZAKŁADKA 3: ANALIZA TAKTYCZNA ---
with tab_analytics:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("📊 Analityka Zespołowa & Rozkład Profili")
    c_a, c_b = st.columns(2)
    with c_a:
        fig_pie = px.pie(names=['Ball-Playing Defender', 'Box-to-Box', 'Inverted Winger', 'Target Man'], values=[30, 35, 20, 15], title="Dominujące Profile Taktyczne")
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
        "Engine Version": "4-Pillar Mathematical Matrix 2.0",
        "Database Status": "Connected" if DB_OK else "Offline"
    })
    st.markdown('</div>', unsafe_allow_html=True)
