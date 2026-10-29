"""
Application Web locale Streamlit : Scanner de Factures & Tickets de caisse.
100% Local, 100% Gratuit, ultra-léger (< 5 Go RAM consommés au pic, 0 Go au repos).
Supporte Images (PNG, JPG, WEBP) et PDF, avec RapidOCR (ONNX) et Tesseract.
"""

import gc
import json
import os
import io
import streamlit as st
from PIL import Image
import pandas as pd

from config import DEFAULT_MODEL, find_tesseract_path
from ocr_engine import (
    extract_text_from_image,
    extract_text_from_pdf,
    get_available_engines
)
from extractor import extract_invoice_data, check_ollama_status
from validator import validate_invoice_math

# --- Configuration de la page Streamlit ---
st.set_page_config(
    page_title="Scanner Factures & Tickets Local (IA & OCR Léger)",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Style CSS pour une interface professionnelle
st.markdown("""
<style>
    .status-badge {
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 15px;
    }
    .badge-ok { background-color: #d1e7dd; color: #0f5132; border: 1px solid #badbcc; }
    .badge-warn { background-color: #fff3cd; color: #664d03; border: 1px solid #ffecb5; }
    .badge-info { background-color: #cff4fc; color: #055160; border: 1px solid #b6effb; }
</style>
""", unsafe_allow_html=True)

# --- Barre latérale : Statut & Diagnostic Matériel ---
with st.sidebar:
    st.header("⚙️ Système & Diagnostic")

    # Diagnostic Moteurs OCR
    available_engines = get_available_engines()
    selected_engine = st.selectbox(
        "Moteur OCR (CPU)",
        options=available_engines if available_engines else ["Aucun moteur détecté"],
        index=0,
        help="RapidOCR fonctionne immédiatement sans installation système externe."
    )

    tess_path = find_tesseract_path()
    if tess_path:
        st.caption(f"Tesseract détecté : `{tess_path}`")
    else:
        st.caption("ℹ️ Tesseract non installé. RapidOCR (ONNX local) assure le relais en toute autonomie.")

    st.divider()

    # Diagnostic Ollama
    ollama_ok, ollama_msg = check_ollama_status()
    if ollama_ok:
        st.success("🟢 **Serveur Ollama :** En ligne")
    else:
        st.warning(f"🟡 **Serveur Ollama :** Déconnecté\n\n_{ollama_msg}_")

    st.subheader("🤖 Modèle IA Local")
    selected_model = st.selectbox(
        "Modèle Ollama (max 3B)",
        options=["qwen2.5:3b", "llama3.2:3b"],
        index=0,
        help="qwen2.5:3b est recommandé pour son respect strict du français et des calculs comptables."
    )

    st.divider()
    st.markdown("""
    **💡 Consommation Mémoire :**
    - Modèle Q4 : ~1.9 Go en RAM pendant l'inférence.
    - Déchargement immédiat de la RAM dès la fin (`keep_alive: 0`).
    - OCR CPU : ~80 Mo.
    - Aucune donnée n'est envoyée sur Internet.
    """)

# --- Corps principal ---
st.title("🧾 Scanner de Factures & Tickets de Caisse")
st.caption("100% Local • CPU uniquement • Respect strict de la RAM (< 3 Go en pic, 0 Go au repos)")

# Option pour tester avec l'exemple fourni
col_up, col_demo = st.columns([3, 1], gap="medium")

with col_up:
    uploaded_file = st.file_uploader(
        "Déposez votre facture ou ticket (PNG, JPG, WEBP ou PDF)",
        type=["png", "jpg", "jpeg", "webp", "pdf"]
    )

with col_demo:
    st.write(" ")
    st.write(" ")
    load_demo = st.button("🧪 Tester avec l'exemple de ticket", use_container_width=True)

# Détermination du document à analyser
active_file_bytes = None
active_file_type = None
active_file_name = None

if load_demo and os.path.exists("sample_ticket.png"):
    with open("sample_ticket.png", "rb") as f:
        active_file_bytes = f.read()
    active_file_type = "image/png"
    active_file_name = "sample_ticket.png"
elif uploaded_file is not None:
    active_file_bytes = uploaded_file.getvalue()
    active_file_type = uploaded_file.type
    active_file_name = uploaded_file.name

if active_file_bytes is not None:
    col_left, col_right = st.columns([1, 1], gap="medium")

    with col_left:
        st.subheader("📸 Aperçu du document")
        if active_file_type == "application/pdf" or active_file_name.lower().endswith(".pdf"):
            st.info(f"📄 Fichier PDF chargé : `{active_file_name}`")
        else:
            image_preview = Image.open(io.BytesIO(active_file_bytes))
            st.image(image_preview, use_container_width=True)

    with col_right:
        st.subheader("⚡ Traitement")
        if not ollama_ok:
            st.error("Ollama n'est pas détecté. Veuillez lancer Ollama dans un terminal (`ollama serve`).")
        else:
            if st.button("🚀 Extraire les données", type="primary", use_container_width=True):
                # 1. OCR
                with st.spinner("1/3 - Extraction du texte (OCR CPU léger)..."):
                    if active_file_type == "application/pdf" or active_file_name.lower().endswith(".pdf"):
                        raw_text = extract_text_from_pdf(io.BytesIO(active_file_bytes))
                    else:
                        img_to_ocr = Image.open(io.BytesIO(active_file_bytes))
                        raw_text = extract_text_from_image(img_to_ocr, engine_choice=selected_engine)

                if not raw_text.strip():
                    st.warning("Aucun texte n'a été détecté dans le document.")
                else:
                    # 2. LLM Extraction
                    with st.spinner(f"2/3 - Structuration JSON via {selected_model} (Ollama)..."):
                        data = extract_invoice_data(raw_text, model_name=selected_model)

                    # 3. Validation
                    with st.spinner("3/3 - Contrôle arithmétique comptable..."):
                        validation = validate_invoice_math(data)

                    # Libération de mémoire
                    gc.collect()

                    st.session_state["result_data"] = data
                    st.session_state["result_validation"] = validation
                    st.session_state["raw_ocr_text"] = raw_text

    # --- Affichage des résultats ---
    if "result_data" in st.session_state:
        data = st.session_state["result_data"]
        validation = st.session_state["result_validation"]
        raw_text = st.session_state.get("raw_ocr_text", "")

        st.divider()
        st.header("📊 Résultats de l'extraction")

        # Statut Arithmétique
        if validation["is_valid"]:
            st.markdown(
                '<div class="status-badge badge-ok">✅ Validation arithmétique réussie : Tous les totaux concordent</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="status-badge badge-warn">⚠️ Attention : Écart arithmétique détecté dans les totaux</div>',
                unsafe_allow_html=True
            )

        # Cartes métriques
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("🏢 Émetteur", data.get("emetteur") or "Non identifié")
        with m2:
            st.metric("📅 Date", data.get("date") or "Non identifiée")
        with m3:
            st.metric("Total HT", f"{data.get('total_ht', 0.0):.2f} €")
        with m4:
            st.metric("TVA", f"{data.get('montant_tva', 0.0):.2f} €")
        with m5:
            st.metric("Total TTC", f"{data.get('total_ttc', 0.0):.2f} €")

        # Rapport de vérification arithmétique
        with st.expander("🔍 Rapport de vérification arithmétique", expanded=not validation["is_valid"]):
            for check in validation["checks"]:
                st.write(check)

        # Tableau des articles
        st.subheader("🛒 Articles & Lignes détaillées")
        lignes = data.get("lignes", [])
        if lignes:
            df = pd.DataFrame(lignes)
            column_mapping = {
                "description": "Désignation",
                "quantite": "Quantité",
                "prix_unitaire": "Prix unitaire (€)",
                "total_ligne": "Total ligne (€)"
            }
            df = df.rename(columns=column_mapping)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Export CSV
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger les articles au format CSV",
                data=csv_data,
                file_name="articles_facture.csv",
                mime="text/csv"
            )
        else:
            st.info("Aucune ligne d'article détaillée n'a été extraite.")

        # Données JSON & Texte brut
        c_json, c_ocr = st.columns(2)
        with c_json:
            with st.expander("📄 JSON structuré (Données complètes)"):
                st.json(data)
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="💾 Télécharger le fichier JSON",
                    data=json_str,
                    file_name="facture_extraite.json",
                    mime="application/json",
                    use_container_width=True
                )

        with c_ocr:
            with st.expander("📝 Texte brut issu de l'OCR"):
                st.text_area("Texte extrait", raw_text, height=220, disabled=True)
