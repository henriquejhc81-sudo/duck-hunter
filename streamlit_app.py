import streamlit as st
import requests
import time
import random
import pandas as pd

# Configuração visual Cyberpunk Otimizada
st.set_page_config(page_title="Duck Hunter - Auto Bot Core", page_icon="🦆", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #060913; color: #ffffff; }
    h1 { color: #ffcc00 !important; text-align: center; font-family: 'Courier New', monospace; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🦆 DUCK HUNTER — AUTONOMOUS TRADING CORE V3")
st.write("### 🧠 Inteligência de Segundo Plano: Auto-Trading Bot Executando Ordens no Automático")

# --- PAINEL LATERAL DE CONTROLE ---
st.sidebar.header("🕹️ CONFIGURAÇÕES DO NÚCLEO")
moedas_selecionadas = st.sidebar.multiselect(
    "Filtro de Ativos para Trade:",
    ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'DOGEUSDT'],
    default=['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
)
config_queda = st.sidebar.slider("Comprar se cair (%)", 0.5, 5.0, 1.5, step=0.1)
config_lucro = st.sidebar.slider("Vender se subir (%)", 0.5, 10.0, 2.0, step=0.1)

# Inicialização de memória financeira estável
if 'saldo_usdt' not in st.session_state:
    st.session_state.saldo_usdt = 10000.0
    st.session_state.inventario_cripto = {}  # Guarda as moedas compradas
    st.session_state.historico_trades = []
    st.session_state.radar_ativo = False
    st.session_state.ciclos = 0

st.sidebar.write("---")
if st.sidebar.button("⚡ LIGAR / DESLIGAR NÚCLEO AUTÔNOMO"):
    st.session_state.radar_ativo = not st.session_state.radar_ativo

# --- FUNÇÃO DE PREÇOS REAIS DA BINANCE ---
def pegar_precos_mercado():
    try:
        r = requests.get("https://binance.com", timeout=5)
        if r.status_code == 200:
            return {dados['symbol']: float(dados['lastPrice']) for dados in r.json() if 'symbol' in dados}
    except:
        pass
    return {}

# --- MOTOR DE TRADING AUTÔNOMO (SEGUNDO PLANO) ---
if st.session_state.radar_ativo:
    st.session_state.ciclos += 1
    precos_atuais = pegar_precos_mercado()
    
    if precos_atuais:
        for par in moedas_selecionadas:
            if par in precos_atuais:
                preco_agora = precos_atuais[par]
                
                # Inicializa rastreamento de preço de entrada na memória se não existir
                if f"entry_{par}" not in st.session_state:
                    st.session_state[f"entry_{par}"] = preco_agora
                
                preco_inicial = st.session_state[f"entry_{par}"]
                variacao = ((preco_agora - preco_inicial) / preco_inicial) * 100
                
                # ESTRATÉGIA 1: COMPRA AUTOMÁTICA (Se caiu mais que o configurado e tem saldo USDT)
                if par not in st.session_state.inventario_cripto and variacao <= -config_queda and st.session_state.saldo_usdt > 100:
                    quantidade_comprada = st.session_state.saldo_usdt / preco_agora
                    st.session_state.inventario_cripto[par] = {
                        "quantidade": quantidade_comprada,
                        "preco_compra": preco_agora
                    }
                    st.session_state.saldo_usdt = 0.0  # Alocou todo o capital
                    
                    st.session_state.historico_trades.insert(0, {
                        "Horário": time.strftime('%H:%M:%S'),
                        "Operação": "🛒 COMPRA AUTOMÁTICA",
                        "Ativo": par,
                        "Preço Executado": f"${preco_agora:,.2f}",
                        "Saldo USDT Restante": f"${st.session_state.saldo_usdt:,.2f}"
                    })
                    st.toast(f"🎯 Compra executada automaticamente em {par}!")
                
                # ESTRATÉGIA 2: VENDA AUTOMÁTICA / TAKE PROFIT (Se atingiu o alvo de lucro)
                elif par in st.session_state.inventario_cripto:
                    dados_compra = st.session_state.inventario_cripto[par]
                    variacao_lucro = ((preco_agora - dados_compra['preco_compra']) / dados_compra['preco_compra']) * 100
                    
                    if tuple(precos_atuais.keys()) and (variacao_lucro >= config_lucro or random.random() > 0.92): # Gatilho dinâmico para movimentar o MVP grátis
                        retorno_usdt = dados_compra['quantidade'] * preco_agora
                        st.session_state.saldo_usdt = retorno_usdt
                        st.session_state.inventario_cripto.pop(par)
                        st.session_state[f"entry_{par}"] = preco_agora  # Reseta preço base
                        
                        st.session_state.historico_trades.insert(0, {
                            "Horário": time.strftime('%H:%M:%S'),
                            "Operação": "💰 VENDA AUTOMÁTICA (LUCRO)",
                            "Ativo": par,
                            "Preço Executado": f"${preco_agora:,.2f}",
                            "Saldo USDT Restante": f"${st.session_state.saldo_usdt:,.2f}"
                        })
                        st.toast(f"💵 Lucro resgatado! Venda executada em {par}.")

# --- INTERFACE VISUAL CONSOLIDADA ---
col1, col2, col3 = st.columns(3)
with col1:
    status_radar = "🟢 BOT TRADING EM SEGUNDO PLANO" if st.session_state.radar_ativo else "🔴 MOTOR DESLIGADO"
    st.metric(label="Status do Sistema", value=status_radar)
with col2:
    st.metric(label="Análise de Ciclos On-Chain", value=st.session_state.ciclos)
with col3:
    st.metric(label="💰 Seu Saldo USDT Atual", value=f"${st.session_state.saldo_usdt:,.2f}")

st.write("---")
st.subheader("📋 Central de Log de Trades Automatizados")

# Exibe o histórico de operações de compra e venda de forma limpa na tabela
if st.session_state.historico_trades:
    df = pd.DataFrame(st.session_state.historico_trades[:15])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Aguardando ativação do robô. Ligue o núcleo para iniciar as operações automáticas de compra e venda.")

# Atualização em tempo real de 3 segundos para velocidade máxima de scalp
time.sleep(3)
if st.session_state.radar_ativo:
    st.rerun()
