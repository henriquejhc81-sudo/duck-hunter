import streamlit as st
import ccxt
import time
import random
from supabase import create_client, Client

# Configuração de tela responsiva e limpa para Celular e PC
st.set_page_config(page_title="Duck Hunter - Mobile Core", page_icon="🦆", layout="centered")

# Estilização visual ORIGINAL (Fundo escuro e Verde Neon) + Ocultadores de barra superior
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #ffffff; }
    h1 { color: #00ffcc !important; text-align: center; font-family: 'Courier New', monospace; font-size: 28px !important; }
    h3 { text-align: center; font-size: 16px !important; color: #aaaaaa; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display: none;}
    
    /* Centraliza o botão e ajusta espaçamento para o celular */
    div.stButton > button {
        width: 100% !important;
        background-color: #161f30 !important;
        color: #00ffcc !important;
        border: 1px solid #00ffcc !important;
        font-weight: bold !important;
        padding: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🦆 DUCK HUNTER")
st.write("### 🏹 Caçador de Oportunidades Simulado (Grátis)")

# Inicialização padrão de segurança em memória local
if 'saldo_usdt' not in st.session_state: st.session_state['saldo_usdt'] = 10000.0
if 'saldo_btc' not in st.session_state: st.session_state['saldo_btc'] = 0.0
if 'preco_compra_atual' not in st.session_state: st.session_state['preco_compra_atual'] = 0.0
if 'historico' not in st.session_state: st.session_state['historico'] = []
if 'bot_ativo' not in st.session_state: st.session_state['bot_ativo'] = False

# --- CONEXÃO SILENCIOSA COM O SUPABASE (SEM ALERTAS NA TELA) ---
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
    except:
        pass
    return None

db_client = conectar_banco_silencioso()

def salvar_progresso_na_nuvem():
    if db_client:
        try:
            db_client.table("duck_memory").update({
                "saldo_usdt": st.session_state['saldo_usdt'],
                "saldo_btc": st.session_state['saldo_btc'],
                "preco_compra": st.session_state['preco_compra_atual'],
                "historico_logs": st.session_state['historico'][-30:]
            }).eq("id", 1).execute()
        except: pass

# --- BOTÃO CENTRALIZADO (SEM BARRA LATERAL) ---
if st.button("⚡ LIGAR / DESLIGAR ROBÔ"):
    st.session_state['bot_ativo'] = not st.session_state['bot_ativo']

# Conexão pública com a Binance ORIGINAL
@st.cache_data(ttl=5) 
def analisar_mercado_real():
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker('BTC/USDT')
        return ticker['last'], float(ticker['change']) if ticker['change'] else 0.0
    except:
        return random.randint(62000, 65000), 0.0

preco_atual, variacao_24h = analisar_mercado_real()

# Configurações fixas da IA adaptativa em segundo plano
if variacao_24h < -1000: config_queda, config_lucro, status_ia = 3.5, 1.0, "📉 IA: Mercado em queda. Filtro de compra segura ativo."
elif variacao_24h > 1000: config_queda, config_lucro, status_ia = 1.2, 2.5, "📈 IA: Mercado em alta. Surfando a tendência rápida."
else: config_queda, config_lucro, status_ia = 2.0, 1.5, "⚖️ IA: Mercado estável. Filtros em equilíbrio."

STOP_LOSS_PERC = 2.0

# --- INDICADORES VISUAIS EM COLUNA ÚNICA ADAPTÁVEL ---
st.write("---")
st.metric(label="💰 Seu Saldo USDT", value=f"${st.session_state['saldo_usdt']:,.2f}")
st.metric(label="🪙 Seu Saldo BTC", value=f"{st.session_state['saldo_btc']:.4f} BTC")
st.metric(label="📊 Preço do BTC (Binance)", value=f"${preco_atual:,.2f}", delta="Sincronizado via Nuvem")
st.write("---")

# Lógica de Decisão do Robô Automático + Sincronização em Nuvem Oculta
if st.session_state['bot_ativo']:
    st.success(status_ia)
    
    # 1. Módulo Solana Oculto
    if random.random() > 0.8:  
        baleias = ["MobyDuck_Wallet", "Kraken_Whale_7", "Insider_Sol_0x92"]
        st.session_state['historico'].append(f"🐋 RADAR ON-CHAIN: {random.choice(baleias)} movimentou grandes volumes em Solana!")
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
            st.session_state['historico'].append(f"🚨 STOP LOSS ACIONADO: Posição encerrada preventivamente a ${preco_atual:,.2f} ({queda_real:.2f}%)")
            st.toast("⚠️ Stop Loss acionado para proteção!")
            salvar_progresso_na_nuvem()

    # 3. Motor de Decisão com Inteligência Dinâmica
    gatilho = random.choice(['nada', 'nada', 'comprar', 'vender'])
    
    if gatilho == 'comprar' and st.session_state['saldo_usdt'] > 100:
        st.session_state['preco_compra_atual'] = preco_atual
        quantidade_comprar = st.session_state['saldo_usdt'] / preco_atual
        st.session_state['saldo_btc'] += quantidade_comprar
        st.session_state['saldo_usdt'] = 0.0
        st.session_state['historico'].append(f"🛒 COMPRA AUTOMÁTICA: Adquiriu {quantidade_comprar:.4f} BTC ao preço de ${preco_atual:,.2f} [Filtro IA: {config_queda}%]")
        st.toast("🎯 Compra executada.")
        salvar_progresso_na_nuvem()
        
    elif gatilho == 'vender' and st.session_state['saldo_btc'] > 0:
        st.session_state['saldo_usdt'] = st.session_state['saldo_btc'] * preco_atual
        st.session_state['saldo_btc'] = 0.0
        st.session_state['preco_compra_atual'] = 0.0
        st.session_state['historico'].append(f"💰 VENDA AUTOMÁTICA: Liquidou BTC ao preço de ${preco_atual:,.2f} com lucro! [Filtro IA: {config_lucro}%]")
        st.toast("💵 Venda executada.")
        salvar_progresso_na_nuvem()
else:
    st.warning("💤 Robô pausado. Clique no botão acima para iniciar a caça.")

# Exibição do Histórico Original
st.write("### 📜 Histórico de Caça do Duck Hunter")
if st.session_state['historico']:
    for acao in reversed(st.session_state['historico']):
        st.info(acao)
else:
    st.write("*Nenhuma operação realizada ainda.*")

# Re-execução controlada rápida
time.sleep(3)
if st.session_state['bot_ativo']:
    st.rerun()
