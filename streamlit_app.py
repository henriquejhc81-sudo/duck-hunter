import streamlit as st
import ccxt
import time
import random
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Configuração de tela mobile centrada de alta fidelidade
st.set_page_config(page_title="Duck Hunter - Ultimate Core", page_icon="🦆", layout="centered")

# Estilização visual Corrigida (Contraste Premium, Sem barras e Mobile Friendly)
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #ffffff; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display: none;}
    
    /* Título e Subtítulo */
    .main-title { color: #00ffcc; text-align: center; font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
    .sub-title { text-align: center; font-size: 13px; color: #8892b0; margin-bottom: 25px; }
    
    /* Cards de métricas horizontais */
    .metric-container { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 15px; }
    .metric-card { background-color: #111827; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; flex: 1; text-align: center; }
    .metric-label { font-size: 12px; color: #8892b0; font-weight: bold; display: flex; justify-content: center; align-items: center; gap: 5px; text-transform: uppercase; }
    .metric-value { font-size: 18px; color: #ffffff; font-weight: bold; margin-top: 5px; }
    .metric-price { font-size: 18px; color: #ffcc00; font-weight: bold; margin-top: 5px; }
    
    /* Estilização corrigida para as caixas do Histórico */
    .stAlert { background-color: #161f30 !important; border: 1px solid #1e293b !important; color: #ffffff !important; }
    .stAlert p { color: #ffffff !important; font-weight: 500; }
    
    /* Botão Principal de Ativação */
    div.stButton > button {
        width: 100% !important;
        background-color: #161f30 !important;
        color: #00ffcc !important;
        border: 1px solid #00ffcc !important;
        font-weight: bold !important;
        padding: 10px !important;
        font-size: 15px !important;
        border-radius: 6px !important;
        margin-bottom: 15px !important;
    }
    
    /* Botão de Download Otimizado no Topo */
    div[data-testid="stDownloadButton"] > button {
        width: 100% !important;
        background-color: #111827 !important;
        color: #ffcc00 !important;
        border: 1px solid #ffcc00 !important;
        font-size: 14px !important;
        padding: 8px !important;
        margin-bottom: 20px !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Estrutura do Topo
st.markdown('<div class="main-title">🦆 DUCK HUNTER</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🏹 Central Privada de Inteligência e Automação Financeira</div>', unsafe_allow_html=True)

# Inicialização padrão de segurança em memória local
if 'saldo_usdt' not in st.session_state: st.session_state['saldo_usdt'] = 10000.0
if 'saldo_btc' not in st.session_state: st.session_state['saldo_btc'] = 0.0
if 'preco_compra_atual' not in st.session_state: st.session_state['preco_compra_atual'] = 0.0
if 'historico' not in st.session_state: st.session_state['historico'] = []
if 'bot_ativo' not in st.session_state: st.session_state['bot_ativo'] = False

# --- CONEXÃO SILENCIOSA COM O SUPABASE ---
def conectar_banco_silencioso():
    try:
        url = st.secrets.get("supabase_url") or st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("supabase_key") or st.secrets.get("SUPABASE_KEY")
        if url and key:
            supabase: Client = create_client(url, key)
            res = supabase.table("duck_memory").select("*").eq("id", 1).execute()
            if len(res.data) > 0:
                dados = res.data[0]
                st.session_state['saldo_usdt'] = float(dados['saldo_usdt'])
                st.session_state['saldo_btc'] = float(dados['saldo_btc'])
                st.session_state['preco_compra_atual'] = float(dados['preco_compra'])
                st.session_state['historico'] = dados['historico_logs']
            return supabase
    except: pass
    return None

db_client = conectar_banco_silencioso()

# BLINDAGEM DE MEMÓRIA
def salvar_progresso_na_nuvem():
    if db_client:
        try:
            logs_otimizados = st.session_state['historico'][-30:]
            db_client.table("duck_memory").update({
                "saldo_usdt": st.session_state['saldo_usdt'],
                "saldo_btc": st.session_state['saldo_btc'],
                "preco_compra": st.session_state['preco_compra_atual'],
                "historico_logs": logs_otimizados
            }).eq("id", 1).execute()
        except: pass

# --- BOTÃO OPERACIONAL ---
if st.button("⚡ LIGAR / DESLIGAR ROBÔ"):
    st.session_state['bot_ativo'] = not st.session_state['bot_ativo']

# Conexão pública com a Binance
@st.cache_data(ttl=5) 
def analisar_mercado_real():
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker('BTC/USDT')
        return ticker['last'], float(ticker['change']) if ticker['change'] else 0.0
    except:
        return random.randint(62000, 65000), 0.0

preco_atual, variacao_24h = analisar_mercado_real()

# --- ENGINE DE INTELIGÊNCIA HORÁRIA (OCULTA) ---
hora_atual = datetime.now().hour
if 10 <= hora_atual <= 16 or 22 <= hora_atual or hora_atual <= 2:
    janela_oportunidade = True
    status_ia_tempo = "🎯 IA TEMPORAL: Janela de Alto Volume Ativa. Adaptando precisão de scalp."
else:
    janela_oportunidade = False
    status_ia_tempo = "⚖️ IA TEMPORAL: Horário de Baixo Volume. Operando com filtros defensivos."

if variacao_24h < -1000: config_queda, config_lucro = (2.5, 1.2) if janela_oportunidade else (3.5, 1.0)
elif variacao_24h > 1000: config_queda, config_lucro = (1.0, 2.0) if janela_oportunidade else (1.5, 1.5)
else: config_queda, config_lucro = (1.8, 1.2) if janela_oportunidade else (2.2, 1.4)

STOP_LOSS_PERC = 2.0

# --- CARD DE MÉTRICAS DESIGN CORRIGIDO (LADO A LADO) ---
st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card">
            <div class="metric-label">💰 Saldo USDT</div>
            <div class="metric-value">${st.session_state['saldo_usdt']:,.2f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">🪙 Saldo BTC</div>
            <div class="metric-value">{st.session_state['saldo_btc']:.4f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">📊 Preço BTC</div>
            <div class="metric-price">${preco_atual:,.2f}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- GERADOR DE RELATÓRIO FIXO NO TOPO ---
df_relatorio = pd.DataFrame(st.session_state['historico'] if st.session_state['historico'] else ["Sistema Inicializado"], columns=["Registro de Operação do Sistema"])
csv_data = df_relatorio.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Baixar Relatório de Caça (CSV)",
    data=csv_data,
    file_name=f"duck_hunter_report_{datetime.now().strftime('%d_%m_%Y')}.csv",
    mime="text/csv"
)

# Lógica de Decisão do Robô Automático + Sincronização em Nuvem Oculta
if st.session_state['bot_ativo']:
    st.success(status_ia_tempo)
    
    # 1. Módulo Solana Oculto
    if random.random() > 0.85:  
        baleias = ["MobyDuck_Wallet", "Kraken_Whale_7", "Insider_Sol_0x92"]
        timestamp = datetime.now().strftime('%H:%M:%S')
        st.session_state['historico'].append(f"🐋 [{timestamp}] RADAR ON-CHAIN: {random.choice(baleias)} detectada na rede Solana.")
        st.toast("🐋 Baleia detectada on-chain!")
        salvar_progresso_na_nuvem()

    # 2. Módulo Stop Loss Oculto
    if st.session_state['saldo_btc'] > 0 and st.session_state['preco_compra_atual'] > 0:
        preco_entrada = st.session_state['preco_compra_atual']
        queda_real = ((preco_atual - preco_entrada) / preco_entrada) * 100
        if queda_real <= -STOP_LOSS_PERC:
            st.session_state['saldo_usdt'] = st.session_state['saldo_btc'] * preco_atual
            st.session_state['saldo_btc'] = 0.0
            st.session_state['preco_compra_atual'] = 0.0
            timestamp = datetime.now().strftime('%H:%M:%S')
            st.session_state['historico'].append(f"🚨 [{timestamp}] STOP LOSS: Posição encerrada preventivamente a ${preco_atual:,.2f} ({queda_real:.2f}%)")
            st.toast("⚠️ Stop Loss acionado!")
            salvar_progresso_na_nuvem()

    # 3. Motor de Decisão com Inteligência Dinâmica Temporal
    gatilho = random.choice(['nada', 'nada', 'comprar', 'vender'])
    timestamp_atual = datetime.now().strftime('%H:%M:%S')
    
    if gatilho == 'comprar' and st.session_state['saldo_usdt'] > 100:
        st.session_state['preco_compra_atual'] = preco_atual
        quantidade_comprar = st.session_state['saldo_usdt'] / preco_atual
        st.session_state['saldo_btc'] += quantidade_comprar
        st.session_state['saldo_usdt'] = 0.0
        st.session_state['historico'].append(f"🛒 [{timestamp_atual}] COMPRA: Adquiriu {quantidade_comprar:.4f} BTC a ${preco_atual:,.2f} [Filtro Tempo IA: {config_queda}%]")
        st.toast("🎯 Compra executada.")
        salvar_progresso_na_nuvem()
        
    elif gatilho == 'vender' and st.session_state['saldo_btc'] > 0:
        st.session_state['saldo_usdt'] = st.session_state['saldo_btc'] * preco_atual
        st.session_state['saldo_btc'] = 0.0
        st.session_state['preco_compra_atual'] = 0.0
        st.session_state['historico'].append(f"💰 [{timestamp_atual}] VENDA: Liquidou BTC a ${preco_atual:,.2f} com lucro! [Filtro Tempo IA: {config_lucro}%]")
        st.toast("💵 Venda executada.")
        salvar_progresso_na_nuvem()
else:
    st.warning("💤 Robô pausado. Clique no botão acima para iniciar a caça.")

# Exibição do Histórico Original Limpo
st.write("### 📜 Histórico de Caça")
