import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TaskMaster Pro", layout="wide", page_icon="✅")

# --- CONTROLE DE TEMA (O "Pique" do Visual) ---
if "tema" not in st.session_state:
    st.session_state.tema = "Escritório"

def set_tema():
    if st.session_state.tema == "Escritório":
        # Visual Clean / Corporativo
        st.markdown("""
            <style>
            .main { background-color: #F0F2F6; }
            .stButton>button { background-color: #004085; color: white; border-radius: 4px; }
            .stTextInput>div>div>input { border-radius: 4px; }
            h1 { color: #1f2937; font-family: 'Segoe UI', sans-serif; }
            </style>
        """, unsafe_allow_html=True)
    else:
        # Visual Rosinha / Fofinho
        st.markdown("""
            <style>
            .main { background-color: #FFF5F7; }
            .stButton>button { background-color: #FFB6C1; color: #704242; border-radius: 20px; border: 2px solid #FFD1DC; }
            .stTextInput>div>div>input { border-radius: 15px; border: 1px solid #FFB6C1; }
            h1 { color: #D81B60; font-family: 'Quicksand', sans-serif; }
            .st-emotion-cache-1cvow48 { border-radius: 20px; border: 2px solid #FFD1DC; } /* Cards fofos */
            </style>
        """, unsafe_allow_html=True)

# Chamada inicial do tema
set_tema()

# --- SIDEBAR DE NAVEGAÇÃO ---
with st.sidebar:
    st.title("🗂️ Menu de Tarefas")
    st.session_state.tema = st.radio("Ambiente:", ["Escritório", "Pessoal (Fofinho)"])
    
    st.divider()
    menu = st.radio("Ir para:", ["📋 Minhas Tarefas", "➕ Nova Tarefa", "📊 Dashboard"])

# --- LÓGICA DE LANÇAMENTO (FORMULÁRIO) ---
if menu == "➕ Nova Tarefa":
    st.title("✨ Criar Novo Objetivo")
    
    with st.form("form_tarefa", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("Título da Tarefa")
            categoria = st.selectbox("Categoria", ["Trabalho", "Estudos", "Casa", "Lazer", "Saúde"])
            auxiliar = st.text_input("Pessoa Auxiliando (opcional)")
        
        with col2:
            prazo = st.date_input("Prazo Final", value=datetime.now())
            prioridade = st.select_slider("Prioridade", options=["Baixa", "Média", "Alta"])
            arquivos = st.file_uploader("Anexar Documentos", accept_multiple_files=True)

        descricao = st.text_area("Descrição detalhada")
        
        # Sistema de Subtarefas Simples
        st.markdown("---")
        st.subheader("📌 Subtarefas")
        sub_input = st.text_area("Liste as subtarefas (uma por linha)")

        if st.form_submit_button("Lançar Tarefa 🚀"):
            # Aqui entraria a lógica de salvar no banco de dados (ex: SQLite ou Sheets)
            st.success("Tarefa enviada para o seu universo de produtividade!")

# --- VISUALIZAÇÃO ---
elif menu == "📋 Minhas Tarefas":
    st.title("🔎 Gerenciamento")
    
    # Exemplo de como as tarefas seriam exibidas com opção de concluir
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([0.1, 0.5, 0.2, 0.2])
        c1.checkbox(" ", key="task1")
        c2.markdown("**Revisar documentação técnica**")
        c3.caption("📅 15/10")
        c4.write("👤 João")
        
        # Subtarefas aparecem como um "expandível"
        with st.expander("Ver subtarefas"):
            st.checkbox("Parte 1: Levantamento de requisitos", value=True)
            st.checkbox("Parte 2: Diagrama de fluxo")

# --- DASHBOARD ---
elif menu == "📊 Dashboard":
    st.title("📈 Progresso Geral")
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Pendentes", 8)
    col_m2.metric("Concluídas", 24, "+3 hoje")
    col_m3.metric("Foco da Semana", "Estudos")
