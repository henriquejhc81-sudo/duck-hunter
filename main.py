import streamlit as st
import pandas as pd
import numpy as np
import io
import pytz
from datetime import datetime
from orquestrador import OrquestradorMaster # O cérebro da Hidra que já temos
from fpdf import FPDF

# Configuração de Interface
st.set_page_config(page_title="DUCK HUNTER | HUD", page_icon="🦆", layout="wide")

# Inicialização do Cérebro
if 'hydra' not in st.session_state:
    st.session_state.hydra = OrquestradorMaster()
if 'budget' not in st.session_state:
    st.session_state.budget = 10000.0
if 'logs' not in st.session_state:
    st.session_state.logs = []

# --- MOTOR DE SIMULAÇÃO DE MERCADO ---
def gerar_dados_mercado():
    # Simula preço de 10 moedas para "treinar" a Hidra
    moedas = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'LINK', 'MATIC', 'AVAX', 'NEAR', 'PEPE']
    dados = {m: round(np.random.uniform(0.0001, 65000), 4) for m in moedas}
    return dados

# --- EXPORTAÇÃO DE RELATÓRIOS ---
def gerar_relatorio_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- INTERFACE HUD ---
st.markdown("<h1 style='color: #00ffc4; text-align: center;'>DUCK_HUNTER | QUANTUM HUD v4.0</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Budget de Treino (USDT)", f"${st.session_state.budget:,.2f}")
with col2:
    if st.button("🦆 EXECUTAR VARREDURA DA HIDRA"):
        dados = gerar_dados_mercado()
        analise = st.session_state.hydra.executar_consenso_hidra("Analise quais dessas moedas comprar para lucro máximo", str(dados))
        st.session_state.logs.append({"time": datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M:%S'), "msg": analise})
        st.rerun()

# Painel de Relatórios
st.sidebar.title("Configurações DUCK_HUNTER")
if st.session_state.logs:
    df_logs = pd.DataFrame(st.session_state.logs)
    st.sidebar.download_button("📥 Baixar Relatório EXCEL", data=gerar_relatorio_excel(df_logs), file_name="relatorio_duckhunter.xlsx", mime="application/vnd.ms-excel")

st.write("### 📊 Status do Aglomerado de Mercado")
st.table(pd.DataFrame(list(gerar_dados_mercado().items()), columns=['Ativo', 'Preço (Simulado)']))

st.write("### 📜 Logs de Inteligência (Horário de Brasília)")
for log in reversed(st.session_state.logs):
    st.info(f"[{log['time']}] {log['msg']}")
