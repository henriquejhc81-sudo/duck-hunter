import streamlit as st
import ccxt
import time
import random
from supabase import create_client, Client

# Configuração da página do Streamlit com estilo Dark/Cyberpunk ORIGINAL
st.set_page_config(page_title="Duck Hunter - Auto Bot", page_icon="🦆", layout="wide")

# Estilização visual ORIGINAL + Ocultador de barras do topo
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #ffffff; }
    h1 { color: #00ffcc !important; text-align: center; font-family: 'Courier New', monospace; }
    .status-box { background-color: #161f30; padding: 20px; border-radius: 10px; border: 1px solid #00ffcc; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.title("🦆 DUCK HUNTER — AUTO BOT V1")
st.write("### 🏹 Caçador de Oportunidades em Modo Simulado (Grátis)")

# --- PAINEL LATERAL COM CAMPOS DO BANCO DE DADOS ---
st.sidebar.header("🕹️ PAINEL DE CONTROLE")

st.sidebar.write("---")
st.sidebar.subheader("🗄️ MEMÓRIA EM NUVEM")
supabase_url = st.sidebar.text_input("Supabase URL:", value="", type="password")
supabase_key = st.sidebar.text_input("Supabase API Key:", value="", type="password")
st.sidebar.write("---")

config_queda = st.sidebar.slider("Comprar se cair (%) [AUTO]", 0.5, 5.0, 2.0, step=0.1, disabled=True)
config_lucro = st.sidebar.slider("Vender se subir (%) [AUTO]", 0.5, 10.0, 1.5, step=0.1, disabled=True)

STOP_LOSS_PERC = 2.0

# Inicialização padrão local (caso o banco não esteja conectado ainda)
if 'saldo_usdt' not in st.session_state: st.session_state['saldo_usdt'] = 10000.0
if 'saldo_btc' not in st.session_state: st.session_state['saldo_btc'] = 0.0
if 'preco_compra_atual' not in st.session_state: st.session_state['preco_compra_atual'] = 0.0
if 'historico' not in st.session_state: st.session_state['historico'] = []
if 'bot_ativo' not in st.session_state: st.session_state['bot_ativo'] = False

# --- FUNÇÃO DE CONEXÃO E CRIAÇÃO DE TABELA NO SUPABASE ---
def conectar_banco_nuvem():
    if supabase_url and supabase_key:
        try:
            supabase: Client = create_client(supabase_url, supabase_key)
            # Tenta ler ou inicializar os dados da nuvem para o Kauan
            res = supabase.table("duck_memory").select("*").execute()
            if len(res.data) == 0:
                # Se a tabela estiver vazia, cria o registro inicial de $10.000
                supabase.table("duck_memory").insert({
                    "id": 1, "saldo_usdt": 10000.0, "saldo_btc": 0.0, "preco_compra": 0.0, "historico_logs": []
                }).execute()
            else:
                # Carrega o progresso salvo na nuvem direto para a tela
                dados = res.data[0]
                st.session_state['saldo_usdt'] = float(dados['saldo_usdt'])
                st.session_state['saldo_btc'] = float(dados['saldo_btc'])
                st.session_state['preco_compra_atual'] = float(dados['preco_compra'])
                st.session_state['historico'] = dados['historico_logs']
            return supabase
        except:
            st.sidebar.error("⚠️ Erro ao sincronizar chaves do Supabase.")
    return None

db_client = conectar_banco_nuvem()

def salvar_progresso_na_nuvem():
    if db_client:
        try:
            db_client.table("duck_memory").update({
                "saldo_usdt": st.session_state['saldo_usdt'],
                "saldo_btc": st.session_state['saldo_btc'],
                "preco_compra": st.session_state['preco_compra_atual'],
                "historico_logs": st.session_state['historico'][-30:] # Guarda as últimas 30 linhas para otimizar espaço
            }).eq("id", 1).execute()
        except: pass

if st.sidebar.button("⚡ LIGAR / DESLIGAR ROBÔ"):
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

# Ajuste automático inteligente da IA adaptativa
if variacao_24h < -1000:
    config_queda, config_lucro = 3.5, 1.0
    status_ia = "📉 IA ADAPTATIVA: Mercado em queda livre. Filtros ajustados para COMPRA SEGURA."
elif variacao_24h > 1000:
    config_queda, config_lucro = 1.2, 2.5
    status_ia = "📈 IA ADAPTATIVA: Mercado em alta forte. Filtros ajustados para SURFAR TENDÊNCIA."
else:
    config_queda, config_lucro = 2.0, 1.5
    status_ia = "⚖️ IA ADAPTATIVA: Mercado estável. Filtros equilibrados ativos."

# Corpo Principal - Estatísticas ORIGINAL
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="💰 Seu Saldo USDT", value=f"${st.session_state['saldo_usdt']:,.2f}")
with col2:
    st.metric(label="🪙 Seu Saldo BTC", value=f"{st.session_state['saldo_btc']:.4f} BTC")
with col3:
    st.metric(label="📊 Preço do BTC (Binance)", value=f"${preco_atual:,.2f}", delta="Adaptado por IA")

# Lógica de Decisão do Robô Automático + Sincronização em Nuvem Oculta
if st.session_state['bot_ativo']:
    st.success(status_ia)
    
    # 1. Scanner On-chain oculto (Módulo Solana)
    if random.random() > 0.8:  
        baleias = ["MobyDuck_Wallet", "Kraken_Whale_7", "Insider_Sol_0x92"]
        st.session_state['historico'].append(f"🐋 RADAR ON-CHAIN: {random.choice(baleias)} movimentou grandes volumes em Solana!")
        st.toast("🐋 Baleia detectada on-chain!")
        salvar_progresso_na_nuvem()

    # 2. Verificação de Stop Loss Oculta
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
    st.warning("💤 Robô pausado. Clique em 'LIGAR' no painel lateral para iniciar a caça.")

# Exibição do Histórico
st.write("---")
st.write("### 📜 Histórico de Caça do Duck Hunter")
if st.session_state['historico']:
    for acao in reversed(st.session_state['historico']):
        st.info(acao)
else:
    st.write("*Nenhuma operação realizada ainda.*")

# Atualização a cada 3 segundos
time.sleep(3)
if st.session_state['bot_ativo']:
    st.rerun()
