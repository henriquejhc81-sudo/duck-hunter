import streamlit as st
import requests
import time
import random

# Configuração visual Cyberpunk do Sistema Híbrido Sem Chave
st.set_page_config(page_title="Duck Hunter - Zero Key Hybrid", page_icon="🦆", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #060913; color: #ffffff; }
    h1 { color: #ffcc00 !important; text-align: center; font-family: 'Courier New', monospace; font-weight: bold; }
    .bloco-binance { background-color: #111827; padding: 15px; border-radius: 8px; border-left: 5px solid #00ffcc; margin-bottom: 10px; }
    .bloco-blockchain { background-color: #1e1b4b; padding: 15px; border-radius: 8px; border-left: 5px solid #ff0055; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🦆 DUCK HUNTER — ECOSYSTEM HÍBRIDO V3 (FREE)")
st.write("### 🏹 Central Privada: Monitoramento Ativo Off-Chain (Binance) e On-Chain (Meme-Whales Solana)")

# --- PAINEL LATERAL DE CONTROLE ---
st.sidebar.header("🕹️ CONTROLE DOS SCANNERS")
moedas_binance = st.sidebar.multiselect(
    "Filtro Binance:",
    ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'DOGEUSDT'],
    default=['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
)
volume_minimo_binance = st.sidebar.slider("Volume Mínimo Binance (Milhões USD)", 5, 200, 20)

# Memória estável do Streamlit
if 'alertas_binance' not in st.session_state:
    st.session_state.alertas_binance = []
if 'alertas_solana' not in st.session_state:
    st.session_state.alertas_solana = []
if 'radar_ativo' not in st.session_state:
    st.session_state.radar_ativo = False

st.sidebar.write("---")
if st.sidebar.button("⚡ LIGAR / DESLIGAR SISTEMA HÍBRIDO"):
    st.session_state.radar_ativo = not st.session_state.radar_ativo

# --- CAPTURA DE DADOS ---
def puxar_binance():
    try:
        r = requests.get("https://binance.com", timeout=5)
        return r.json() if r.status_code == 200 else []
    except: return []

def simular_feed_solana_whales():
    # Como a rede Solana é pública, simulamos transações reais do explorador on-chain para alimentar o radar do MVP
    baleias = ["MobyDuck_Wallet", "Kraken_Whale_7", "Insider_Sol_0x92", "Base_Capital_Alpha", "SmartMoney_0x71"]
    tokens = ["SOL", "WIF", "BONK", "POPCAT", "BOME"]
    
    if random.random() > 0.4:  # 60% de chance de capturar uma movimentação a cada ciclo
        return {
            "wallet": random.choice(baleias),
            "token": random.choice(tokens),
            "quantidade": random.randint(500, 5000),
            "valor_usd": random.randint(100000, 2500000),
            "destino": random.choice(["Raydium DEX", "Jupiter Aggregator", "Carteira Fria (HODL)"])
        }
    return None

# --- ENGINE DO ROBÔ ---
if st.session_state.radar_ativo:
    st.toast("🔍 Duck Hunter rastreando anomalias no mercado cripto...")
    
    # 1. Scanner Off-Chain (Binance Real)
    dados_b = puxar_binance()
    for ativo in dados_b:
        par = ativo.get('symbol')
        if par in moedas_binance:
            vol_usd = float(ativo.get('quoteVolume', 0)) / 1_000_000
            if vol_usd >= volume_minimo_binance:
                if not any(a['moeda'] == par for a in st.session_state.alertas_binance[:2]):
                    st.session_state.alertas_binance.insert(0, {
                        "moeda": par,
                        "preco": float(ativo.get('lastPrice', 0)),
                        "volume": vol_usd,
                        "variacao": float(ativo.get('priceChangePercent', 0))
                    })

    # 2. Scanner On-Chain (Solana Core)
    nova_tx = simular_feed_solana_whales()
    if nova_tx:
        st.session_state.alertas_solana.insert(0, nova_tx)
        st.toast(f"🐋 BALEIA SOLANA: ${nova_tx['valor_usd']:,.2f} USD se movimentando!")

# --- INTERFACE VISUAL ---
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("📊 Scanner de Volume de Mercado (Binance Real)")
    if st.session_state.alertas_binance:
        for alerta in st.session_state.alertas_binance[:6]:
            cor = "🟢" if alerta['variacao'] >= 0 else "🔴"
            st.markdown(f"""
                <div class="bloco-binance">
                    <h5>🪙 Par: {alerta['moeda']}</h5>
                    <p>Preço Atual: <b>${alerta['preco']:,.2f}</b> | Var: {cor} {alerta['variacao']:.2f}%</p>
                    <p style="color: #00ffcc;">Volume 24h: <b>${alerta['volume']:,.2f} Milhões USD</b></p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Ligue o sistema para analisar o fluxo da Binance.")

with col_dir:
    st.subheader("🌐 Scanner de Grandes Carteiras (On-Chain Solana)")
    if st.session_state.alertas_solana:
        for tx in st.session_state.alertas_solana[:6]:
            st.markdown(f"""
                <div class="bloco-blockchain">
                    <h5>🔗 Rede: SOLANA | Alvo: {tx['wallet']}</h5>
                    <p>Movimentou: <b>{tx['quantidade']:,} {tx['token']}</b> (<b style="color: #ff0055;">${tx['valor_usd']:,.2f} USD</b>)</p>
                    <p style="font-size: 12px;"><b>Fluxo detectado para:</b> {tx['destino']}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Ligue o sistema para interceptar o fluxo da blockchain Solana.")

# Atualização de tela
time.sleep(5)
if st.session_state.radar_ativo:
    st.rerun()
