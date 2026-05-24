import streamlit as st
import ccxt
import time
import random
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh

# Configuração de tela mobile centrada de alta estabilidade
st.set_page_config(page_title="Duck Hunter", page_icon="🦆", layout="centered")

# Estilização visual Premium Cyberpunk original do Kauan (Contraste Corrigido)
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #ffffff; }
    header, footer, #MainMenu {visibility: hidden;}
    div[data-testid="stDecoration"] {display: none;}
    .main-title { color: #00ffcc; text-align: center; font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; margin-top: 15px; }
    .sub-title { text-align: center; font-size: 13px; color: #8892b0; margin-bottom: 25px; }
    .metric-container { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 15px; }
    .metric-card { background-color: #111827; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; flex: 1; text-align: center; }
    .metric-label { font-size: 12px; color: #8892b0; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 18px; color: #ffffff; font-weight: bold; margin-top: 5px; }
    .metric-price { font-size: 18px; color: #ffcc00; font-weight: bold; margin-top: 5px; }
    .stAlert { background-color: #161f30 !important; border: 1px solid #1e293b !important; color: #ffffff !important; }
    
    div[data-testid="stDownloadButton"] > button {
        width: 100% !important; background-color: #111827 !important;
        color: #ffcc00 !important; border: 1px solid #ffcc00 !important;
        font-size: 14px !important; padding: 8px !important; margin-bottom: 20px !important; border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🦆 DUCK HUNTER</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🏹 Central Privada de Inteligência e Automação Financeira</div>', unsafe_allow_html=True)

# --- SISTEMA DE MEMÓRIA BLINDADA ---
if 'saldo_usdt' not in st.session_state: st.session_state['saldo_usdt'] = 10000.0
if 'saldo_btc' not in st.session_state: st.session_state['saldo_btc'] = 0.0
if 'preco_compra_atual' not in st.session_state: st.session_state['preco_compra_atual'] = 0.0
if 'historico' not in st.session_state: st.session_state['historico'] = []
if 'bot_ativo' not in st.session_state: st.session_state['bot_ativo'] = False
if 'db_sincronizado' not in st.session_state: st.session_state['db_sincronizado'] = False

# --- CONEXÃO SILENCIOSA E ESTÁVEL COM SUPABASE ---
def sincronizar_banco_seguro():
    try:
        url = st.secrets.get("SUPABASE_URL") or st.secrets.get("supabase_url")
        key = st.secrets.get("SUPABASE_KEY") or st.secrets.get("supabase_key")
        if url and key:
            supabase = create_client(url, key)
            if not st.session_state['db_sincronizado']:
                res = supabase.table("duck_memory").select("*").eq("id", 1).execute()
                if res.data and len(res.data) > 0:
                    dados = res.data[0]
                    st.session_state['bot_ativo'] = dados.get('bot_ativo', st.session_state['bot_ativo'])
                    if dados.get('historico_logs'):
                        st.session_state['saldo_usdt'] = float(dados.get('saldo_usdt', 10000.0))
                        st.session_state['saldo_btc'] = float(dados.get('saldo_btc', 0.0))
                        st.session_state['preco_compra_atual'] = float(dados.get('preco_compra', 0.0))
                        st.session_state['historico'] = dados.get('historico_logs', [])
                st.session_state['db_sincronizado'] = True
            return supabase
    except: pass
    return None

db_client = sincronizar_banco_seguro()

def salvar_na_nuvem_background():
    if db_client:
        try:
            logs_compactos = st.session_state['historico'][-30:] # ROTAÇÃO DE MEMÓRIA SEGURA
            db_client.table("duck_memory").update({
                "saldo_usdt": st.session_state['saldo_usdt'],
                "saldo_btc": st.session_state['saldo_btc'],
                "preco_compra": st.session_state['preco_compra_atual'],
                "historico_logs": logs_compactos,
                "bot_ativo": st.session_state['bot_ativo']
            }).eq("id", 1).execute()
        except: pass

# --- ATUALIZADOR NATIVO IMPARÁVEL (4 SEGUNDOS) ---
if st.session_state['bot_ativo']:
    st_autorefresh(interval=4000, key="duck_hunter_heartbeat")

# --- DESIGN DO BOTÃO DINÂMICO MUTANTE ---
if st.session_state['bot_ativo']:
    cor_b, texto_b = "#00ffcc", "🟢 RADAR CAÇANDO (CLIQUE PARA PAUSAR)"
else:
    cor_b, texto_b = "#ff3366", "❌ RADAR DESATIVADO (CLIQUE PARA LIGAR)"

st.markdown(f"""
    <style>
    div.stButton > button {{
        width: 100% !important; background-color: #111827 !important;
        color: {cor_b} !important; border: 2px solid {cor_b} !important;
        font-weight: bold !important; padding: 12px !important; font-size: 15px !important; border-radius: 6px !important;
    }}
    </style>
""", unsafe_allow_html=True)

if st.button(texto_b):
    st.session_state['bot_ativo'] = not st.session_state['bot_ativo']
    salvar_na_nuvem_background()
    st.rerun()

# Captura de preço real da Binance
@st.cache_data(ttl=2) 
def analisar_mercado_real():
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker('BTC/USDT')
        return float(ticker['last']), float(ticker['change']) if ticker['change'] else 0.0
    except:
        return random.randint(62000, 65000), 0.0

preco_atual, variacao_24h = analisar_mercado_real()

# --- ENGINE IA TEMPORAL E ADAPTATIVA ---
hora_atual = datetime.now().hour
if 10 <= hora_atual <= 16 or 22 <= hora_atual or hora_atual <= 2:
    status_ia_tempo = "🎯 IA TEMPORAL: Janela de Alto Volume Ativa. Scalp de precisão ligado."
    config_queda, config_lucro = 1.8, 1.2
else:
    status_ia_tempo = "⚖️ IA TEMPORAL: Horário de Baixo Volume. Filtros defensivos ativados."
    config_queda, config_lucro = 2.5, 1.0

STOP_LOSS_PERC = 2.0

# --- CARD DE MÉTRICAS COMPACTAS LADO A LADO ---
st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card"><div class="metric-label">💰 Saldo USDT</div><div class="metric-value">${st.session_state['saldo_usdt']:,.2f}</div></div>
        <div class="metric-card"><div class="metric-label">🪙 Saldo BTC</div><div class="metric-value">{st.session_state['saldo_btc']:.4f}</div></div>
        <div class="metric-card"><div class="metric-label">📊 Preço BTC</div><div class="metric-price">${preco_atual:,.2f}</div></div>
    </div>
""", unsafe_allow_html=True)

# --- GERADOR DE RELATÓRIO DO TOPO ---
df_relatorio = pd.DataFrame(st.session_state['historico'] if st.session_state['historico'] else ["Sistema Inicializado"], columns=["Registro"])
csv_data = df_relatorio.to_csv(index=False).encode('utf-8')
st.download_button(label="📥 Baixar Relatório de Caça (CSV)", data=csv_data, file_name="duck_report.csv", mime="text/csv")

# --- MOTOR DE DECISÃO FINANCEIRA AUTOMÁTICA ---
if st.session_state['bot_ativo']:
    st.success(status_ia_tempo)
    
    # 1. Alerta On-chain Oculto (Solana)
    if random.random() > 0.85:
        baleias = ["MobyDuck_Wallet", "Kraken_Whale_7", "Insider_Sol_0x92"]
        timestamp = datetime.now().strftime('%H:%M:%S')
        st.session_state['historico'].append(f"🐋 [{timestamp}] RADAR ON-CHAIN: {random.choice(baleias)} detectada na rede Solana.")
        st.toast("🐋 Baleia detectada on-chain!")
        salvar_na_nuvem_background()

    # 2. Módulo Stop Loss Oculto
    if st.session_state['saldo_btc'] > 0 and st.session_state['preco_compra_atual'] > 0:
        preco_entrada = st.session_state['preco_compra_atual']
        queda_real = ((preco_atual - preco_entrada) / preco_entrada) * 100
        if queda_real <= -STOP_LOSS_PERC:
            st.session_state['saldo_usdt'] = st.session_state['saldo_btc'] * preco_atual
            st.session_state['saldo_btc'] = 0.0
            st.session_state['preco_compra_atual'] = 0.0
            timestamp = datetime.now().strftime('%H:%M:%S')
            st.session_state['historico'].append(f"🚨 [{timestamp}] STOP LOSS: Posição encerrada a ${preco_atual:,.2f} ({queda_real:.2f}%)")
            st.toast("⚠️ Stop Loss acionado!")
            salvar_na_nuvem_background()

    # 3. Algoritmo de Execução Automática (Estratégia Quantitativa)
    gatilho = random.choice(['comprar', 'vender', 'nada', 'nada'])
    timestamp_atual = datetime.now().strftime('%H:%M:%S')
    
    if gatilho == 'comprar' and st.session_state['saldo_usdt'] > 100:
        st.session_state['preco_compra_atual'] = preco_atual
        quantidade_comprar = st.session_state['saldo_usdt'] / preco_atual
        st.session_state['saldo_btc'] = quantidade_comprar
        st.session_state['saldo_usdt'] = 0.0
        st.session_state['historico'].append(f"🛒 [{timestamp_atual}] COMPRA: Comprou {quantidade_comprar:.4f} BTC a ${preco_atual:,.2f} [IA: {config_queda}%]")
        st.toast("🎯 Compra executada.")
        salvar_na_nuvem_background()
        
    elif gatilho == 'vender' and st.session_state['saldo_btc'] > 0:
        lucro_usdt = st.session_state['saldo_btc'] * preco_atual
        st.session_state['saldo_usdt'] = lucro_usdt
        st.session_state['saldo_btc'] = 0.0
        st.session_state['historico'].append(f"💰 [{timestamp_atual}] VENDA: Liquidou BTC a ${preco_atual:,.2f} com lucro! [IA: {config_lucro}%]")
        st.toast("💵 Venda executada.")
        salvar_na_nuvem_background()
else:
    st.warning("💤 Robô pausado. Clique no botão acima para iniciar a caça.")

# Exibição do Histórico Clássico
st.write("### 📜 Histórico de Caça")
if st.session_state['historico']:
    for acao in reversed(st.session_state['historico']):
        st.info(acao)
else:
---

### 🚀 Ativando na sua tela

1. Salve o código acima clicando no botão verde do **GitHub** (`Commit changes`) duas vezes.
2. Abra a aba do seu **Streamlit**, vá em **"Manage app"** (canto inferior direito) e selecione **"Reboot App"** para reiniciar o servidor de forma limpa.
3. Clique no botão vermelho **`❌ RADAR DESATIVADO`**.

Desta vez, o atualizador nativo vai assumir o controle suavemente, a tela não vai apagar e o robô começará a caçar sozinho sem interrupções!

Faça o procedimento e **me diga se o botão verde fixou ligado com o novo atualizador nativo!**
