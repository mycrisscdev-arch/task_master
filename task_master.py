import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import date, datetime
import time
import plotly.express as px
import pdfplumber

# --- CONFIGURAÇÃO SEGURA ---
try:
    URL_MINHA_PLANILHA = st.secrets["connections"]["gsheets"]["spreadsheet"]
except Exception:
    st.error("Erro: URL da planilha não configurada nos Secrets!")
    st.stop()

st.set_page_config(page_title="Gestor Familiar", page_icon="💰", layout="wide")

# --- CSS ADAPTATIVO REFINADO ---
st.markdown("""
    <style>
    .stApp { background-color: var(--background-color); }
    [data-testid="stStatusWidget"] {
        background-color: var(--background-color) !important;
        opacity: 0.9; backdrop-filter: blur(5px);
        width: 100vw !important; height: 100vh !important;
        position: fixed !important; top: 0 !important; left: 0 !important;
        z-index: 999999 !important; display: flex !important;
        justify-content: center !important; align-items: center !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; padding: 15px 0px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px; border-radius: 14px;
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1); border: 1px solid rgba(128,128,128,0.2);
        padding: 0px 30px;
    }
    .stTabs [aria-selected="true"] { background-color: #343a40 !important; color: white !important; border: none !important; }
    div.stButton > button[kind="primary"] {
        background-color: #343a40 !important; color: white !important;
        width: 100%; height: 60px; border-radius: 15px; font-weight: bold;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #495057 !important; color: white !important;
        width: 100%; height: 60px; border-radius: 15px; font-weight: bold;
    }
    div[data-testid="stForm"], .welcome-card {
        background-color: var(--secondary-background-color) !important;
        padding: 35px; border-radius: 20px;
        box-shadow: 0px 4px 25px rgba(0,0,0,0.1); margin-bottom: 25px;
        border: 1px solid rgba(128,128,128,0.1) !important;
    }
    .id-display {
        background-color: rgba(128,128,128,0.1);
        padding: 10px 20px; border-radius: 10px;
        font-family: monospace; font-size: 1.1em;
        border: 1px dashed rgba(128,128,128,0.3);
        display: inline-block; margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO E CARREGAMENTO ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_tudo():
    u = conn.read(spreadsheet=URL_MINHA_PLANILHA, worksheet="Usuarios", ttl="0")
    b = conn.read(spreadsheet=URL_MINHA_PLANILHA, worksheet="BaseDados", ttl="0")
    c = conn.read(spreadsheet=URL_MINHA_PLANILHA, worksheet="Config", ttl="0")
    d = conn.read(spreadsheet=URL_MINHA_PLANILHA, worksheet="Dicionario", ttl="0")
    for df in [u, b, c, d]: 
        df.columns = df.columns.str.strip()
    return u, b, c, d

if "logado" not in st.session_state:
    st.session_state.logado = False

# --- ACESSO ---
if not st.session_state.logado:
    st.title("💰 Gestor Familiar")
    t_log, t_cad = st.tabs(["🔐 Acessar", "✨ Criar Conta"])
    with t_log:
        with st.form("login"):
            em = st.text_input("E-mail").strip()
            pw = st.text_input("Senha", type="password").strip()
            if st.form_submit_button("ENTRAR", type="primary"):
                df_u, _, _, _ = carregar_tudo()
                user = df_u[(df_u['Email'] == em) & (df_u['Senha'] == pw)]
                if not user.empty:
                    st.session_state.logado = True
                    st.session_state.user_info = user.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Dados incorretos.")
    with t_cad:
        with st.form("cad"):
            n_em = st.text_input("E-mail")
            n_pw = st.text_input("Senha", type="password")
            n_sn = st.text_input("Sobrenome")
            if st.form_submit_button("CRIAR", type="primary"):
                df_u, _, _, df_d = carregar_tudo()
                f_id = f"FAM_{datetime.now().strftime('%M%S')}"
                u_new = pd.DataFrame([{'Email': n_em, 'Senha': n_pw, 'ID_Familia': f_id, 'Sobrenome': n_sn}])
                conn.update(spreadsheet=URL_MINHA_PLANILHA, data=pd.concat([df_u, u_new]), worksheet="Usuarios")
                d_init = pd.DataFrame([
                    {'ID_Familia': f_id, 'Chave': 'Sobrenome', 'Valor': n_sn},
                    {'ID_Familia': f_id, 'Chave': 'Membros', 'Valor': 'Eu, Parceiro(a)'},
                    {'ID_Familia': f_id, 'Chave': 'Categorias', 'Valor': 'Mercado, Casa, Lazer'},
                    {'ID_Familia': f_id, 'Chave': 'Cartoes', 'Valor': 'Cartão Black, Dinheiro, Débito'}
                ])
                conn.update(spreadsheet=URL_MINHA_PLANILHA, data=pd.concat([df_d, d_init]), worksheet="Dicionario")
                st.success(f"Conta criada! ID: {f_id}")
    st.stop()

# --- APP LOGADO ---
ID_FAMILIA = st.session_state.user_info['ID_Familia']
df_usuarios, df_base, df_config, df_dic_total = carregar_tudo()

df_db = df_base[df_base['ID_Familia'] == ID_FAMILIA].copy()
df_regras = df_config[df_config['ID_Familia'] == ID_FAMILIA].copy()
df_dic = df_dic_total[df_dic_total['ID_Familia'] == ID_FAMILIA].copy()
conf = dict(zip(df_dic['Chave'], df_dic['Valor']))

SOBRENOME = conf.get('Sobrenome', st.session_state.user_info['Sobrenome'])
LISTA_MEMBROS = conf.get('Membros', 'Eu').split(', ')
LISTA_CATS = conf.get('Categorias', 'Geral').split(', ')
LISTA_CARTOES = conf.get('Cartoes', 'Dinheiro').split(', ')

# HEADER
c1, c2 = st.columns([0.85, 0.15])
c1.subheader(f"👋 Olá, Família {SOBRENOME} !")
if c2.button("Sair"):
    st.session_state.logado = False
    st.rerun()

tab_home, tab_add, tab_dash, tab_ajustes = st.tabs(["🏠 Início", "➕ Lançar", "📊 Dashboard", "⚙️ Ajustes"])

with tab_home:
    st.markdown(f"""
    <div class="welcome-card">
        <h1>Bem-vindos! 🚀</h1>
        <p>Este é o seu centro de controle financeiro inteligente.</p>
        <hr style="opacity: 0.2; margin: 20px 0;">
        <h3>🔑 Identidade da Família</h3>
        <p>Copie o código abaixo para compartilhar o acesso:</p>
        <div class="id-display">{ID_FAMILIA}</div>
        <br><br>
        <h3>💡 Dicas Rápidas:</h3>
        <p>• <b>Lançar:</b> O app aprende com os nomes das faturas que você cadastra em 'Ajustes'.</p>
        <p>• <b>Ajustes:</b> Em 'Alterar Dados da Família', lembre-se que os valores devem ser <b>separados apenas por vírgula</b>.</p>
        <p>• <b>Faturas:</b> Importe PDF ou CSV e o sistema ignorará estornos negativos automaticamente.</p>
        <p>• <b>Tabela:</b> Você pode editar ou deletar linhas diretamente no Dashboard.</p>
    </div>
    """, unsafe_allow_html=True)

with tab_add:
    with st.expander("📄 Obter gastos da fatura (PDF ou CSV)"):
        fatura_file = st.file_uploader("Subir arquivo", type=['csv', 'pdf'], key="fatura_up")
        if fatura_file:
            df_f = None
            if fatura_file.name.endswith('.csv'):
                df_f = pd.read_csv(fatura_file, sep=None, engine='python')
            else:
                with pdfplumber.open(fatura_file) as pdf:
                    ext_data = []
                    for p in pdf.pages:
                        table = p.extract_table()
                        if table: ext_data.extend(table)
                    if ext_data: df_f = pd.DataFrame(ext_data[1:], columns=ext_data[0])

            if df_f is not None:
                c1, c2, c3 = st.columns(3)
                c_data = c1.selectbox("Coluna de Data", df_f.columns)
                c_desc = c2.selectbox("Coluna de Descrição", df_f.columns)
                c_valor = c3.selectbox("Coluna de Valor", df_f.columns)
                v_pay_f = st.selectbox("Forma de Pagamento", LISTA_CARTOES)

                if st.button("IMPORTAR TUDO", type="primary"):
                    novos = []
                    cont_ignorado = 0
                    for _, row in df_f.iterrows():
                        v_raw = str(row[c_valor]).replace('R$', '').replace(' ', '')
                        if ',' in v_raw and '.' in v_raw: v_raw = v_raw.replace('.', '').replace(',', '.')
                        elif ',' in v_raw: v_raw = v_raw.replace(',', '.')
                        
                        try: v_final = float(v_raw)
                        except: v_final = 0.0

                        if v_final > 0:
                            desc_orig = str(row[c_desc])
                            n_s, c_s, q_s = desc_orig, LISTA_CATS[0], LISTA_MEMBROS[0]
                            for _, r in df_regras.iterrows():
                                if str(r['Termo_Fatura']).upper() in desc_orig.upper():
                                    n_s, c_s, q_s = r['Nome_Amigavel'], r['Categoria_Padrao'], r['Membro_Padrao']
                                    break
                            
                            novos.append({'ID_Familia': ID_FAMILIA, 'Data': str(row[c_data]), 'Descrição': n_s, 'Valor': v_final, 'Familiar': q_s, 'Categoria': c_s, 'Pagamento': v_pay_f})
                        else:
                            cont_ignorado += 1
                    
                    if novos:
                        df_novos = pd.DataFrame(novos)
                        conn.update(spreadsheet=URL_MINHA_PLANILHA, data=pd.concat([df_base, df_novos]), worksheet="BaseDados")
                        st.success(f"Importado! ({cont_ignorado} itens negativos ignorados)")
                        time.sleep(1.5); st.rerun()
                    else: st.warning("Nenhum gasto positivo encontrado.")

    with st.form("novo_gasto", clear_on_submit=True):
        c1, c2 = st.columns(2)
        v_data = c1.date_input("Data")
        v_valor = c2.number_input("Valor R$", step=0.01)
        v_desc = st.text_input("Descrição (Ex: UBER TRIP)")
        n_s, c_s, q_s = v_desc, LISTA_CATS[0], LISTA_MEMBROS[0]
        for _, r in df_regras.iterrows():
            if str(r['Termo_Fatura']).upper() in v_desc.upper() and v_desc != "":
                n_s, c_s, q_s = r['Nome_Amigavel'], r['Categoria_Padrao'], r['Membro_Padrao']
                st.caption(f"✨ Mapeado: {n_s}")
                break
        c3, c4, c5 = st.columns(3)
        v_quem = c3.selectbox("Quem?", LISTA_MEMBROS, index=LISTA_MEMBROS.index(q_s) if q_s in LISTA_MEMBROS else 0)
        v_cat = c4.selectbox("Categoria", LISTA_CATS, index=LISTA_CATS.index(c_s) if c_s in LISTA_CATS else 0)
        v_pay = c5.selectbox("Pagamento", LISTA_CARTOES)
        if st.form_submit_button("SALVAR GASTO", type="secondary"):
            nl = pd.DataFrame([{'ID_Familia': ID_FAMILIA, 'Data': v_data.strftime('%Y-%m-%d'), 'Descrição': n_s, 'Valor': v_valor, 'Familiar': v_quem, 'Categoria': v_cat, 'Pagamento': v_pay}])
            conn.update(spreadsheet=URL_MINHA_PLANILHA, data=pd.concat([df_base, nl]), worksheet="BaseDados")
            st.success("Salvo!"); time.sleep(0.5); st.rerun()

with tab_dash:
    if df_db.empty:
        st.info("ℹ️ Nenhum gasto lançado ainda.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Acumulado", f"R$ {df_db['Valor'].sum():,.2f}")
        m2.metric("Média por Lançamento", f"R$ {df_db['Valor'].mean():,.2f}")
        m3.metric("Nº de Gastos", len(df_db))

        g1, g2 = st.columns(2)
        with g1: st.plotly_chart(px.pie(df_db, values='Valor', names='Categoria', hole=0.4, title="Divisão por Categoria"), use_container_width=True)
        with g2: st.plotly_chart(px.bar(df_db.groupby('Familiar')['Valor'].sum().reset_index(), x='Familiar', y='Valor', title="Gastos por Membro", color='Familiar'), use_container_width=True)
        
        df_db['Data'] = pd.to_datetime(df_db['Data'])
        st.plotly_chart(px.line(df_db.sort_values('Data').groupby('Data')['Valor'].sum().reset_index(), x='Data', y='Valor', title="Evolução de Gastos Diários", markers=True), use_container_width=True)

        st.write("### 📝 Histórico Editável")
        df_editavel = df_db.drop(columns=['ID_Familia'])
        
        df_editado = st.data_editor(
            df_editavel,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "Valor": st.column_config.NumberColumn("Valor R$", format="R$ %.2f"),
                "Familiar": st.column_config.SelectboxColumn("Quem?", options=LISTA_MEMBROS, required=True),
                "Categoria": st.column_config.SelectboxColumn("Categoria", options=LISTA_CATS, required=True),
                "Pagamento": st.column_config.SelectboxColumn("Pagamento", options=LISTA_CARTOES, required=True),
            },
        )
        
        if st.button("Sincronizar Edições na Planilha"):
            try:
                df_salvar = df_editado.copy()
                # Limpeza de linhas vazias/deletadas
                df_salvar = df_salvar.dropna(how='all')
                
                if not df_salvar.empty:
                    df_salvar['Data'] = pd.to_datetime(df_salvar['Data'], errors='coerce')
                    df_salvar = df_salvar.dropna(subset=['Data'])
                    df_salvar['Data'] = df_salvar['Data'].dt.strftime('%Y-%m-%d')
                
                df_salvar['ID_Familia'] = ID_FAMILIA
                df_final = pd.concat([df_base[df_base['ID_Familia'] != ID_FAMILIA], df_salvar])
                
                with st.spinner("Sincronizando..."):
                    conn.update(spreadsheet=URL_MINHA_PLANILHA, data=df_final, worksheet="BaseDados")
                    time.sleep(1) # Fôlego para a API
                
                st.success("Dados atualizados!"); time.sleep(0.5); st.rerun()
            except Exception:
                st.error("Erro ao salvar. Verifique se deletou linhas corretamente ou se a conexão caiu.")

with tab_ajustes:
    st.subheader("⚙️ Configurações do Perfil")
    with st.expander("✏️ Alterar Dados da Família"):
        with st.form("perfil"):
            f_sob = st.text_input("Sobrenome da Família", value=SOBRENOME)
            f_mem = st.text_area("Membros (separe por vírgula)", value=", ".join(LISTA_MEMBROS))
            f_cat = st.text_area("Categorias (separe por vírgula)", value=", ".join(LISTA_CATS))
            f_car = st.text_area("Cartões/Contas (separe por vírgula)", value=", ".join(LISTA_CARTOES))
            if st.form_submit_button("ATUALIZAR TUDO", type="secondary"):
                df_outros = df_dic_total[df_dic_total['ID_Familia'] != ID_FAMILIA]
                novos = pd.DataFrame([{'ID_Familia': ID_FAMILIA, 'Chave': k, 'Valor': v} for k,v in zip(['Sobrenome','Membros','Categorias','Cartoes'], [f_sob, f_mem, f_cat, f_car])])
                conn.update(spreadsheet=URL_MINHA_PLANILHA, data=pd.concat([df_outros, novos]), worksheet="Dicionario")
                st.success("Configurações salvas!"); time.sleep(0.5); st.rerun()

    with st.form("nova_regra"):
        st.write("🤖 Criar Regra de Inteligência")
        c1, c2 = st.columns(2)
        rt, rn = c1.text_input("Se na fatura vier..."), c2.text_input("Salvar como...")
        rc, rq = st.selectbox("Categoria", LISTA_CATS), st.selectbox("Quem gasta", LISTA_MEMBROS)
        if st.form_submit_button("CRIAR REGRA"):
            nr = pd.DataFrame([{'ID_Familia': ID_FAMILIA, 'Termo_Fatura': rt.upper(), 'Nome_Amigavel': rn, 'Categoria_Padrao': rc, 'Membro_Padrao': rq}])
            conn.update(spreadsheet=URL_MINHA_PLANILHA, data=pd.concat([df_config, nr]), worksheet="Config")
            st.success("Regra criada!"); st.rerun()
