import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client
import json

# Configuration
st.set_page_config(
    page_title="HERKULES SCOUTING 2.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark/Gold Styling
st.markdown("""
    <style>
        .main { background-color: #0b132b; color: #ffffff; }
        .stButton>button { background-color: #d4af37; color: #0b132b; font-weight: bold; border-radius: 6px; border: none; }
        .stButton>button:hover { background-color: #00f5d4; color: #0b132b; }
        .metric-card { background-color: #1c2541; padding: 15px; border-radius: 8px; border: 1px solid rgba(212,175,55,0.3); text-align: center; }
        .metric-title { font-size: 12px; color: #a0aec0; }
        .metric-value { font-size: 24px; font-weight: bold; color: #d4af37; }
    </style>
""", unsafe_allow_html=True)

# Supabase Initialization
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("Brak połączenia z bazą Supabase. Skonfiguruj klucze w Streamlit Secrets.")

# Navigation Sidebar
st.sidebar.title("⚡ HERKULES 2.0")
st.sidebar.caption("System Skautingowy & Baza Wiedzy")

page = st.sidebar.radio(
    "Nawigacja Modułowa:",
    ["📊 Formularz Skautowy", "📚 Słownik Ról Taktycznych", "📁 Baza Zawodników"]
)

# ====================================================================
# MODUŁ 1: FORMULARZ SKAUTOWY & CALCULATOR
# ====================================================================
if page == "📊 Formularz Skautowy":
    st.header("⚡ Nowy Raport Obserwacyjny")
    st.caption("Wprowadź oceny parametrów zawodnika w skali 1-100")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("I. Dane Zawodnika")
        first_name = st.text_input("Imię zawodnika", "Jan")
        last_name = st.text_input("Nazwisko zawodnika", "Kowalski")
        birth_year = st.number_input("Rocznik", min_value=2000, max_value=2020, value=2008)
        current_club = st.text_input("Obecny Klub", "Akademia Herkules")
        position = st.selectbox("Pozycja Główna", ["CB - Środkowy Obrońca", "CM - Środkowy Pomocnik", "ST - Napastnik"])
        foot = st.radio("Noga dominująca", ["Prawa", "Lewa", "Obunóż"], horizontal=True)

        st.subheader("II. Ocena Osi Głównych (Current vs Potential)")
        offense_cr = st.slider("Ofensywa (Current)", 1, 100, 55)
        offense_pr = st.slider("Ofensywa (Potential)", 1, 100, 75)
        
        defense_cr = st.slider("Defensywa (Current)", 1, 100, 65)
        defense_pr = st.slider("Defensywa (Potential)", 1, 100, 80)
        
        creation_cr = st.slider("Kreacja (Current)", 1, 100, 67)
        creation_pr = st.slider("Kreacja (Potential)", 1, 100, 85)
        
        physique_cr = st.slider("Fizyczność (Current)", 1, 100, 76)
        physique_pr = st.slider("Fizyczność (Potential)", 1, 100, 88)
        
        mental_cr = st.slider("Mental (Current)", 1, 100, 62)
        mental_pr = st.slider("Mental (Potential)", 1, 100, 80)

    # Calculate Metrics
    cr_score = round((offense_cr + defense_cr + creation_cr + physique_cr + mental_cr) / 5, 1)
    pr_score = round((offense_pr + defense_pr + creation_pr + physique_pr + mental_pr) / 5, 1)
    dps_score = round(pr_score - cr_score, 1)
    transitional_index = round((physique_cr * 0.4) + (mental_cr * 0.6), 1)

    with col2:
        st.subheader("III. Podgląd Analityczny Na Żywo")
        
        # Metrics Display
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current (CR)", cr_score)
        m2.metric("Potential (PR)", pr_score)
        m3.metric("DPS", f"+{dps_score}", delta_color="normal")
        m4.metric("Index (TI)", transitional_index)

        # Plotly Radar Chart
        categories = ['Ofensywa', 'Defensywa', 'Kreacja', 'Fizyczność', 'Mental']
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=[offense_pr, defense_pr, creation_pr, physique_pr, mental_pr],
            theta=categories,
            fill='toself',
            name='Potential (PR)',
            line_color='#00f5d4'
        ))

        fig.add_trace(go.Scatterpolar(
            r=[offense_cr, defense_cr, creation_cr, physique_cr, mental_cr],
            fill='toself',
            name='Current (CR)',
            line_color='#d4af37'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
                bgcolor='#1c2541'
            ),
            paper_bgcolor='#0b132b',
            font_color='#ffffff',
            margin=dict(l=40, r=40, t=20, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

        if st.button("💾 Zapisz Raport do Bazy Supabase"):
            try:
                # Save player
                player_res = supabase.table("players").insert({
                    "first_name": first_name,
                    "last_name": last_name,
                    "birth_year": birth_year,
                    "current_club": current_club,
                    "preferred_foot": foot,
                    "primary_position": position[:2]
                }).execute()
                
                player_id = player_res.data[0]['id']

                # Save report
                supabase.table("scouting_reports").insert({
                    "player_id": player_id,
                    "cr_score": cr_score,
                    "pr_score": pr_score,
                    "dps_score": dps_score,
                    "transitional_index": transitional_index,
                    "kpi_ratings": json.dumps({"CR": cr_score, "PR": pr_score}),
                    "tactical_fits": json.dumps({"Primary": position}),
                    "top_development_priorities": json.dumps(["Atak przestrzeni", "Finalizacja"])
                }).execute()

                st.success("✅ Raport został pomyślnie zapisany w zaszyfrowanej bazie danych!")
            except Exception as e:
                st.error(f"Błąd zapisu: {e}")

# ====================================================================
# MODUŁ 2: SŁOWNIK RÓL TAKTYCZNYCH (DLA TRENERA I SKAUTA)
# ====================================================================
elif page == "📚 Słownik Ról Taktycznych":
    st.header("📚 Baza Wiedzy & Słownik Ról Taktycznych")
    st.caption("Oficjalna metodologia klubowa — profilowanie ról bez nazwisk zawodników")

    try:
        roles_data = supabase.table("tactical_roles").select("*").execute()
        roles_df = pd.DataFrame(roles_data.data)

        if not roles_df.empty:
            positions = roles_df['position_code'].unique()
            selected_pos = st.selectbox("Wybierz Pozycję:", positions)

            filtered_roles = roles_df[roles_df['position_code'] == selected_pos]
            selected_role_name = st.selectbox("Wybierz Rolę Taktyczną:", filtered_roles['role_name'].unique())

            role_info = filtered_roles[filtered_roles['role_name'] == selected_role_name].iloc[0]

            st.markdown(f"### 📌 Profil: {role_info['role_name']}")
            st.info(role_info['description'])

            col_scout, col_coach = st.columns(2)

            with col_scout:
                st.subheader("👁️ Instrukcja dla Skauta")
                st.warning(role_info['scout_instructions'])

            with col_coach:
                st.subheader("📋 Wytyczne dla Trenera Akademii")
                st.success(role_info['coach_instructions'])
        else:
            st.info("Brak zdefiniowanych ról w bazie danych.")
    except Exception as e:
        st.error(f"Nie udało się pobrać ról taktycznych: {e}")

# ====================================================================
# MODUŁ 3: BAZA ZAWODNIKÓW
# ====================================================================
elif page == "📁 Baza Zawodników":
    st.header("📁 Zapisani Zawodnicy w Systemie")
    try:
        players_data = supabase.table("players").select("*").execute()
        df_p = pd.DataFrame(players_data.data)
        if not df_p.empty:
            st.dataframe(df_p[['first_name', 'last_name', 'birth_year', 'current_club', 'primary_position', 'preferred_foot']], use_container_width=True)
        else:
            st.write("Baza zawodników jest obecnie pusta.")
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
