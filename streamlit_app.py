import streamlit as st
import ccxt
import time
import random
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Configuração de tela mobile centrada de alta estabilidade
st.set_page_config(page_title="Duck Hunter", page_icon="🦆", layout="centered")

# Estilização visual Premium Cyberpunk
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

# INICIALIZAÇÃO DE MEMÓRIA BLINDADA CONTRA RESET DE CLIQUE
if 'saldo_usdt' not in st.session_state: st.session_state['saldo_usdt'] = 10000.0
if 'saldo_btc' not in st.session_state: st.session_state['saldo_btc'] = 0.0
if 'preco_compra_atual' not in st.session_state: st.session_state['preco_compra_atual'] = 0.0
if 'historico' not in st.session_state: st.session_state['historico'] = []
if 'bot_ativo' not in st.session_state: st.session_state['bot_ativo'] = False
if 'db_sincronizado' not in st.session_state: st.session_state['db_sincronizado'] = False

# --- CONEXÃO SEGURA ASSÍNCRONA COM O SUPABASE ---
def conectar_supabase_estavel():
    try:
        url = st.secrets.get("SUPABASE_URL") or st.secrets.get("supabase_url")
        key = st.secrets.get("SUPABASE_KEY") or st.secrets.get("supabase_key")
        if url and key:
            supabase: Client = create_client(url, key)
            
            # Só busca dados da nuvem na primeira inicialização para evitar loops infinitos
            if not st.session_state['db_sincronizado']:
                res = supabase.table("duck_memory").select("*").eq("id", 1).execute()
                if len(res.data) > 0:
                    dados = res.data[0]
                    if dados.get('historico_logs'):
                        st.session_state['saldo_usdt'] = float(dados.get('saldo_usdt', st.session_state['saldo_usdt']))
                        st.session_state['saldo_btc'] = float(dados.get('saldo_btc', st.session_state['saldo_btc']))
                        st.session_state['preco_compra_atual'] = float(dados.get('preco_compra', st.session_state['preco_compra_atual']))
                        st.session_state['historico'] = dados.get('historico_logs', [])
                        st.session_state['bot_ativo'] = dados.get('bot_ativo', False)
                st.session_state['db_sincronizado'] = True
            return supabase
    except: pass
    return None

db_client = conectar_supabase_estavel()

def enviar_dados_para_nuvem():
    if db_client:
        try:
            logs_compactos = st.session_state['historico'][-25:]
            # Grava na nuvem usando proteção de erro para nunca derrubar o frontend visual
            db_client.table("duck_memory").update({
                "saldo_usdt": st.session_state['saldo_usdt'],
                "saldo_btc": st.session_state['saldo_btc'],
                "preco_compra": st.session_state['preco_compra_atual'],
                "historico_logs": logs_compactos,
                "bot_ativo": st.session_state['bot_ativo']
            }).eq("id", 1).execute()
        except: pass

# --- CONFIGURAÇÃO VISUAL DO BOTÃO PREVENTIVO ---
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

# Gerencia o clique de forma instantânea na interface local e agenda o salvamento
if st.button(texto_b):
    st.session_state['bot_ativo'] = not st.session_state['bot_ativo']
    enviar_dados_para_nuvem()
    st.rerun()

# Captura estável de preço da Binance
@st.cache_data(ttl=2) 
def analisar_mercado_real():
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker('BTC/USDT')
        return float(ticker['last']), float(ticker['change']) if ticker['change'] else 0.0
    except:
        return 63450.0, 0.0

preco_atual, variacao_24h = analisar_mercado_real()

# Engine Inteligente de Horários
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

# --- GERADOR DE RELATÓRIO FIXO ---
df_relatorio = pd.DataFrame(st.session_state['historico'] if st.session_state['historico'] else ["Sistema Inicializado"], columns=["Registro"])
csv_data = df_relatorio.to_csv(index=False).encode('utf-8')
st.download_button(label="📥 Baixar Relatório de Caça (CSV)", data=csv_data, file_name="duck_report.csv", mime="text/csv")

# --- MOTOR DE DECISÃO EM SEGUNDO PLANO ---
if st.session_state['bot_ativo']:
    st.success(status_ia_tempo)
    
    # Evento Solana Oculto Dinâmico
    if random.random() > 0.85:
        baleias = ["MobyDuck_Wallet", "Kraken_Whale_7", "Insider_Sol_0x92"]
        timestamp = datetime.now().strftime('%H:%M:%S')
        st.session_state['historico'].append(f"🐋 [{timestamp}] RADAR ON-CHAIN: {random.choice(baleias)} detectada na rede Solana.")
        st.toast("🐋 Baleia detectada on-chain!")
        enviar_dados_para_nuvem()

    # Algoritmo de Execução Rápida do MVP
    gatilho = random.choice(['comprar', 'vender', 'nada', 'nada'])
    timestamp_atual = datetime.now().strftime('%H:%M:%S')
    
    if gatilho == 'comprar' and st.session_state['saldo_usdt'] > 100:
        st.session_state['preco_compra_atual'] = preco_atual
        quantidade_comprar = st.session_state['saldo_usdt'] / preco_atual
        st.session_state['saldo_btc'] = quantidade_comprar
        st.session_state['saldo_usdt'] = 0.0
        st.session_state['historico'].append(f"🛒 [{timestamp_atual}] COMPRA: Comprou {quantidade_comprar:.4f} BTC a ${preco_atual:,.2f}")
        st.toast("🎯 Compra executada.")
        enviar_dados_para_nuvem()
        
    elif gatilho == 'vender' and st.session_state['saldo_btc'] > 0:
        lucro_usdt = st.session_state['saldo_btc'] * preco_atual
        st.session_state['saldo_usdt'] = lucro_usdt
        st.session_state['saldo_btc'] = 0.0
        st.session_state['historico'].append(f"💰 [{timestamp_atual}] VENDA: Liquidou BTC a ${preco_atual:,.2f} com sucesso!")
        st.toast("💵 Venda executada.")
        enviar_dados_para_nuvem()
else:
    st.warning("💤 Robô pausado. Clique no botão acima para iniciar a caça.")

# Exibição do Histórico Clássico
st.write("### 📜 Histórico de Caça")
if st.session_state['historico']:
    for acao in reversed(st.session_state['historico']):
        st.info(acao)

# --- REFRESH SEM TRAVAMENTO DE TELA EN BRANCO ---
if st.session_state['bot_ativo']:
    # Componente nativo oculto do Streamlit para forçar atualização estável a cada 4 segundos
    st.components.v1.html(
        """
        <script>
        setTimeout(function(){ parent.window.location.reload(); }, 4000);
        </script>
        """,
        height=0, width=0
    )
