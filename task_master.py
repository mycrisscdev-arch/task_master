import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TaskFlow Pro", layout="wide", page_icon="📝")

# --- GERENCIAMENTO DE ARQUIVOS ---
UPLOAD_DIR = "meus_anexos_tasks"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def salvar_arquivo(file):
    path = os.path.join(UPLOAD_DIR, file.name)
    with open(path, "wb") as f:
        f.write(file.getbuffer())
    return path

def get_binary_file_downloader_html(bin_file, file_label='Arquivo'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">📥 Baixar {file_label}</a>'
    return href

# --- CONTROLE DE ESTILO (TEMAS) ---
if "tema" not in st.session_state:
    st.session_state.tema = "Escritório"

def aplicar_css():
    if st.session_state.tema == "Escritório":
        st.markdown("""
            <style>
            .stApp { background-color: #F8FAFC; }
            [data-testid="stSidebar"] { background-color: #0F172A; color: white; }
            .stButton>button { background-color: #1E293B; color: white; border-radius: 4px; border: none; width: 100%; }
            h1, h2, h3 { color: #0F172A; font-family: 'Inter', sans-serif; }
            .task-card { background: white; padding: 20px; border-radius: 8px; border-left: 6px solid #3B82F6; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 15px; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;700&display=swap');
            .stApp { background-color: #FFF5F7; }
            [data-testid="stSidebar"] { background-color: #FFE4E1; }
            .stButton>button { background-color: #FFB6C1; color: #5D4037; border-radius: 25px; border: 2px solid #FFC1CC; font-weight: bold; width: 100%; }
            h1, h2, h3 { color: #D81B60; font-family: 'Quicksand', sans-serif; }
            .stTextInput>div>div>input { border-radius: 20px; border: 1px solid #FFB6C1; }
            .task-card { background: white; padding: 20px; border-radius: 25px; border-left: 10px solid #FFB6C1; box-shadow: 0 10px 15px -3px rgba(255, 182, 193, 0.3); margin-bottom: 15px; }
            </style>
        """, unsafe_allow_html=True)

aplicar_css()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🚀 TaskFlow")
    st.session_state.tema = st.radio("Modo Visual:", ["Escritório", "Fofinho"])
    st.divider()
    menu = st.radio("Menu Principal", ["📊 Dashboard", "➕ Nova Tarefa", "📂 Meus Anexos"])

# --- TELAS ---

if menu == "➕ Nova Tarefa":
    st.title("✨ " + ("Nova Demanda" if st.session_state.tema == "Escritório" else "Nova Missão Mágica"))
    
    with st.form("form_nova_task", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo = st.text_input("Título da Tarefa")
            categoria = st.selectbox("Categoria", ["Trabalho", "Pessoal", "Estudos", "Saúde"])
            quem = st.text_input("Quem ajuda? (Auxiliar)")
        with c2:
            data = st.date_input("Data Limite", value=datetime.now())
            prioridade = st.select_slider("Prioridade", options=["Baixa", "Média", "Alta"])
            anexo = st.file_uploader("Documentos")

        subtarefas = st.text_area("Subtarefas (uma por linha)", placeholder="Ex:\n- Ligar para fornecedor\n- Enviar e-mail")
        notas = st.text_area("Notas adicionais")
        
        if st.form_submit_button("Lançar Agora!"):
            if anexo:
                salvar_arquivo(anexo)
            st.success("Tarefa registrada com sucesso!")

elif menu == "📊 Dashboard":
    st.title("📈 Visão Geral")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Em Aberto", "12")
    m2.metric("Concluídas", "45", "+5")
    m3.metric("Urgentes", "2")

    st.divider()

    # Exemplo de Task Card
    st.markdown('<div class="task-card">', unsafe_allow_html=True)
    col_check, col_txt, col_btn = st.columns([0.1, 0.6, 0.3])
    with col_check:
        st.checkbox(" ", key="c1")
    with col_txt:
        st.markdown(f"**Finalizar Protótipo do App**")
        st.caption("👤 Auxiliar: Gemini | 📅 Prazo: 10/04")
    with col_btn:
        with st.expander("Detalhes"):
            st.write("**Subtarefas:**")
            st.write("- [x] Definir cores")
            st.write("- [ ] Criar banco de dados")
            st.button("Marcar como urgente", key="u1")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📂 Meus Anexos":
    st.title("📁 Arquivos da Conta")
    arquivos = os.listdir(UPLOAD_DIR)
    if arquivos:
        for arq in arquivos:
            caminho_completo = os.path.join(UPLOAD_DIR, arq)
            col_a, col_b = st.columns([0.8, 0.2])
            col_a.write(f"📄 {arq}")
            html_botao = get_binary_file_downloader_html(caminho_completo, arq)
            col_b.markdown(html_botao, unsafe_allow_html=True)
    else:
        st.info("Nenhum anexo encontrado.")
