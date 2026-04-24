import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


st.set_page_config(page_title="EcoInsight Pro", layout="wide")


if 'db_eco' not in st.session_state:
    st.session_state.db_eco = pd.DataFrame(columns=['Date', 'Secteur', 'Type_Dechet', 'Poids_kg'])


st.title("🌿 EcoInsight Pro : Collecte & Analyse")
st.markdown("---")


with st.sidebar:
    st.header("📥 Collecte des Données")
    with st.form("form_collecte"):
        secteur = st.selectbox("Département", ["Logistique", "Bureaux", "Production", "Cantine"])
        type_dechet = st.radio("Nature du déchet", ["Plastique", "Papier/Carton", "Organique", "Métal"])
        poids = st.number_input("Poids collecté (en kg)", min_value=0.1, step=0.1)
        submit = st.form_submit_button("Enregistrer la donnée")

        if submit:
            nouvelle_entree = {
                'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'Secteur': secteur,
                'Type_Dechet': type_dechet,
                'Poids_kg': poids
            }
            st.session_state.db_eco = pd.concat([st.session_state.db_eco, pd.DataFrame([nouvelle_entree])], ignore_index=True)
            st.session_state.db_eco.to_csv("donnees_collectees.csv", index=False)
            st.success("Donnée enregistrée avec succès !")


col1, col2 = st.columns([1, 1])

df = st.session_state.db_eco

if not df.empty:
    with col1:
        st.subheader("📊 Aperçu des données")
        st.dataframe(df.tail(10), use_container_width=True)
        

        total_poids = df['Poids_kg'].sum()
        st.metric("Total Collecté", f"{total_poids:.2f} kg")

    with col2:
        st.subheader("📈 Analyse de Répartition")
        
        fig = px.pie(df, values='Poids_kg', names='Type_Dechet', title="Répartition par type de déchet", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("⏱️ Évolution temporelle par Secteur")
    fig_line = px.bar(df, x='Date', y='Poids_kg', color='Secteur', barmode='group')
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("Aucune donnée disponible. Veuillez remplir le formulaire à gauche.")
