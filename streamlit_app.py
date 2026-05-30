import streamlit as st
import pandas as pd
import numpy as np
from orquestrador import OrquestradorMaster

st.set_page_config(page_title="DUCK HUNTER | HUD", page_icon="🦆", layout="wide")

if 'hydra' not in st.session_state: st.session_state.hydra = OrquestradorMaster()
if 'logs' not in st.session_state: st.session_state.logs = []

st.title("🦆 DUCK_HUNTER | QUANTUM HUD v4.0")

if st.button("EXECUTAR VARREDURA DA HIDRA"):
    dados = {m: round(np.random.uniform(0.0001, 65000), 4) for m in ['BTC', 'ETH', 'SOL']}
    analise = st.session_state.hydra.executar_consenso_hidra("Analise para lucro máximo", str(dados))
    st.session_state.logs.append(analise)

for log in reversed(st.session_state.logs):
    st.info(log)
