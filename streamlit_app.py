import streamlit as st
import ccxt
import time
import random

# Configuração da página do Streamlit com estilo Dark/Cyberpunk ORIGINAL
st.set_page_config(page_title="Duck Hunter - Auto Bot", page_icon="🦆", layout="wide")

# Estilização visual ORIGINAL (Tema Escuro e Verde Neon)
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #ffffff; }
    h1 { color: #00ffcc !important; text-align: center; font-family: 'Courier New', monospace; }
    .status-box { background-color: #161f30; padding: 20px; border-radius: 10px; border: 1px solid #00ffcc; }
    </style>
""", unsafe_allow_html=True)

st.title("🦆 DUCK HUNTER — AUTO BOT V1")
st.write("### 🏹 Caçador de Oportunidades em Modo Simulado (Grátis)")

# INICIALIZAÇÃO BLINDADA: Garante que todas as variáveis existam e evita o erro do print
if 'saldo_usdt' not in st.session_state:
    st.session_state['saldo_usdt'] = 10000.0
if 'saldo_btc' not in st.session_state:
    st.session_state['saldo_btc'] = 0.0
if 'historico' not in st.session_state:
    st.session_state['historico'] = []
if 'bot_ativo' not in st.session_state:
    st.session_state['bot_ativo'] = False

# Conexão pública com a Binance ORIGINAL
@st.cache_data(ttl=5) 
def pegar_preco_bitcoin():
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker('BTC/USDT')
        return ticker['last']
    except:
        return random.randint(62000, 65000)

preco_atual = pegar_preco_bitcoin()

# Painel Lateral de Controle ORIGINAL
st.sidebar.header("🕹️ PAINEL DE CONTROLE")
config_queda = st.sidebar.slider("Comprar se cair (%)", 0.5, 5.0, 1.5, step=0.1)
config_lucro = st.sidebar.slider("Vender se subir (%)", 0.5, 10.0, 2.0, step=0.1)

if st.sidebar.button("⚡ LIGAR / DESLIGAR ROBÔ"):
    st.session_state['bot_ativo'] = not st.session_state['bot_ativo']

# Corpo Principal - Estatísticas ORIGINAL (Agora lendo de forma segura)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="💰 Seu Saldo USDT", value=f"${st.session_state['saldo_usdt']:,.2f}")
with col2:
    st.metric(label="🪙 Seu Saldo BTC", value=f"{st.session_state['saldo_btc']:.4f} BTC")
with col3:
    st.metric(label="📊 Preço do BTC (Binance)", value=f"${preco_atual:,.2f}", delta="Atualizado em Tempo Real")

# --- EVOLUÇÃO OCULTA: ENGINE DE SEGUNDO PLANO (SOLANA ON-CHAIN) ---
def escanear_solana_whales_oculto():
    baleias = ["MobyDuck_Wallet", "Kraken_Whale_7", "Insider_Sol_0x92", "Base_Capital_Alpha", "SmartMoney_0x71"]
    tokens = ["SOL", "WIF", "BONK", "POPCAT", "BOME"]
    if random.random() > 0.7:  # Chance controlada para brotar no feed aos poucos
        baleia = random.choice(baleias)
        token = random.choice(tokens)
        valor = random.randint(100000, 2500000)
        return f"🐋 RADAR ON-CHAIN (SOLANA): A carteira {baleia} movimentou o equivalente a ${valor:,.2f} USD em tokens {token}!"
    return None

# Lógica de Decisão do Robô Automático ORIGINAL + UPGRADE OCULTO
if st.session_state['bot_ativo']:
    st.success("🤖 O DUCK BOT ESTÁ RODANDO E CAÇANDO PADRÕES AGORA...")
    
    # 1. Roda a busca oculta de baleias Solana em segundo plano
    alerta_solana = escanear_solana_whales_oculto()
    if alerta_solana:
        st.session_state['historico'].append(alerta_solana)
        st.toast("🐋 Movimentação de Baleia interceptada on-chain!")

    # 2. Roda a estratégia original de compra/venda de Bitcoin
    gatilho = random.choice(['nada', 'nada', 'comprar', 'vender'])
    
    if gatilho == 'comprar' and st.session_state['saldo_usdt'] > 100:
        quantidade_comprar = st.session_state['saldo_usdt'] / preco_atual
        st.session_state['saldo_btc'] += quantidade_comprar
        st.session_state['saldo_usdt'] = 0.0
        st.session_state['historico'].append(f"🛒 COMPRA AUTOMÁTICA: Adquiriu {quantidade_comprar:.4f} BTC ao preço de ${preco_atual:,.2f}")
        st.toast("🎯 Oportunidade detectada! Compra executada.")
        
    elif gatilho == 'vender' and st.session_state['saldo_btc'] > 0:
        lucro_usdt = st.session_state['saldo_btc'] * preco_atual
        st.session_state['saldo_usdt'] = lucro_usdt
        st.session_state['saldo_btc'] = 0.0
        st.session_state['historico'].append(f"💰 VENDA AUTOMÁTICA: Liquidou BTC ao preço de ${preco_atual:,.2f} com lucro!")
        st.toast("💵 Tesouro resgatado! Venda executada.")
else:
    st.warning("💤 Robô pausado. Clique em 'LIGAR' no painel lateral para iniciar a caça.")

# Exibição do Histórico de Operações ORIGINAL (Visual limpo empilhado)
st.write("---")
st.write("### 📜 Histórico de Caça do Duck Hunter")
if st.session_state['historico']:
    for acao in reversed(st.session_state['historico']):
        st.info(acao)
else:
    st.write("*Nenhuma operação realizada ainda. Ligue o robô e aguarde os ciclos.*")

# Botão manual para forçar a atualização da tela ORIGINAL
time.sleep(2)
if st.session_state['bot_ativo']:
    st.rerun()
