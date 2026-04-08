import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="TaskFlow", layout="wide")

def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 Acesso Restrito")
        senha = st.text_input("Senha:", type="password")
        if st.button("Entrar"):
            if senha == st.secrets["password"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return False
    return True

if not check_password():
    st.stop()

# --- SISTEMA DE TEMAS COM FIX DE COR ---
if "tema" not in st.session_state:
    st.session_state.tema = "Escritório"

def aplicar_estilo():
    if st.session_state.tema == "Escritório":
        st.markdown("""
            <style>
            /* Forçar fundo e cor do texto global */
            .stApp { background-color: #F8FAFC !important; color: #1E293B !important; }
            
            /* Corrigir inputs e textos que somem */
            input, textarea, p, li, span, label { color: #1E293B !important; }
            h1, h2, h3 { color: #0F172A !important; font-family: 'Inter', sans-serif; }
            
            /* Botão Escritório */
            .stButton>button { background-color: #1E293B !important; color: white !important; border-radius: 4px; }
            
            .task-card { background: white; padding: 20px; border-radius: 8px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; color: #1E293B; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;700&display=swap');
            
            /* Forçar fundo e cor do texto global no modo fofo */
            .stApp { background-color: #FFF5F7 !important; color: #5D4037 !important; }
            
            input, textarea, p, li, span, label { color: #5D4037 !important; }
            h1, h2, h3 { color: #D81B60 !important; font-family: 'Quicksand', sans-serif; }
            
            /* Botão Fofinho */
            .stButton>button { background-color: #FFB6C1 !important; color: #5D4037 !important; border-radius: 25px; border: 2px solid #FFC1CC; font-weight: bold; }
            
            .task-card { background: white; padding: 20px; border-radius: 25px; border-left: 10px solid #FFB6C1; box-shadow: 0 10px 15px rgba(255, 182, 193, 0.3); margin-bottom: 15px; color: #5D4037; }
            </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- CABEÇALHO ---
col_tit, col_tema = st.columns([0.7, 0.3])
with col_tit:
    st.title("✅ TaskFlow")
with col_tema:
    st.session_state.tema = st.selectbox("Trocar Estilo:", ["Escritório", "Fofinho"])

# --- CONTEÚDO ---
aba1, aba2, aba3 = st.tabs(["📊 Dashboard", "➕ Nova Tarefa", "📂 Anexos"])

with aba2:
    st.header("Cadastrar Objetivo")
    with st.form("nova_task"):
        titulo = st.text_input("O que precisa ser feito?")
        auxiliar = st.text_input("Quem vai ajudar?")
        prazo = st.date_input("Prazo")
        desc = st.text_area("Notas extras")
        if st.form_submit_button("Salvar Tarefa ✨"):
            st.balloons()
            st.success("Tarefa enviada para a planilha!")

with aba1:
    st.header("Seu Progresso")
    # Exemplo do Card com o texto forçado
    st.markdown('''
        <div class="task-card">
            <strong>Revisar Projeto de IA</strong><br>
            <span style="font-size: 0.8em;">👤 Auxiliar: João | 📅 Prazo: 12/04</span>
        </div>
    ''', unsafe_allow_html=True)
