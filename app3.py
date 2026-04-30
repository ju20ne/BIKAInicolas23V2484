import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Configuration de la page
st.set_page_config(page_title="Collecte des Déchets", layout="wide")

# --- SYSTÈME DE STOCKAGE PRÉCIS ---
# On définit le nom du fichier de stockage
DB_FILE = "base_donnees_dechets.csv"

def charger_donnees():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # Structure précise de la base de données
        return pd.DataFrame(columns=['ID', 'Date', 'Secteur', 'Type_Dechet', 'Poids_kg', 'Responsable'])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

# Initialisation de l'état de la session
if 'db_eco' not in st.session_state:
    st.session_state.db_eco = charger_donnees()

# --- INTERFACE ---
st.title("🗑️ Collecte des Déchets")
st.markdown("Système de suivi en temps réel des rejets par département.")
st.markdown("---")

# Sidebar pour la saisie
with st.sidebar:
    st.header(" Nouvelle Entrée")
    with st.form("form_collecte"):
        secteur = st.selectbox("Département", ["Logistique", "Bureaux", "Production", "Cantine", "Maintenance"])
        type_dechet = st.radio("Nature du déchet", ["Plastique", "Papier/Carton", "Organique", "Métal", "Verre"])
        poids = st.number_input("Poids collecté (en kg)", min_value=0.1, step=0.1)
        responsable = st.text_input("Nom de l'agent")
        
        # Le bouton d'entrée (validation)
        submit = st.form_submit_button(" Valider l'enregistrement")

        if submit:
            if responsable:
                nouvelle_entree = {
                    'ID': len(st.session_state.db_eco) + 1,
                    'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'Secteur': secteur,
                    'Type_Dechet': type_dechet,
                    'Poids_kg': poids,
                    'Responsable': responsable
                }
                
                # Ajout à la session et sauvegarde physique dans le CSV
                st.session_state.db_eco = pd.concat([st.session_state.db_eco, pd.DataFrame([nouvelle_entree])], ignore_index=True)
                sauvegarder_donnees(st.session_state.db_eco)
                st.success("Donnée enregistrée avec succès dans le fichier CSV !")
            else:
                st.error("Veuillez indiquer le nom du responsable.")

# --- AFFICHAGE ET ANALYSE ---
df = st.session_state.db_eco

if not df.empty:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(" Derniers enregistrements")
        # Affichage du tableau avec style
        st.dataframe(df.tail(10), use_container_width=True)
        
        total_poids = df['Poids_kg'].sum()
        st.metric("Total Accumulé", f"{total_poids:.2f} kg", delta=f"{len(df)} entrées")

    with col2:
        st.subheader("Répartition par Matière")
        fig = px.pie(df, values='Poids_kg', names='Type_Dechet', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader(" Historique des collectes par secteur")
    fig_bar = px.bar(df, x='Date', y='Poids_kg', color='Secteur', 
                     hover_data=['Responsable'], barmode='group')
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Bouton pour exporter les données
    st.download_button(
        label=" Télécharger l'historique complet (CSV)",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"export_dechets_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
    )
else:
    st.info(" Bienvenue ! Utilisez le formulaire à gauche pour enregistrer votre première collecte.")

