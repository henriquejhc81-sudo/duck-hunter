import streamlit as st
import requests
import time

# Configuração visual Cyberpunk do Duck Hunter
st.set_page_config(page_title="Duck Hunter - Volume Tracker", page_icon="🦆", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #060913; color: #ffffff; }
    h1 { color: #ffcc00 !important; text-align: center; font-family: 'Courier New', monospace; }
    .baleia-detectada { background-color: #111827; padding: 15px; border-radius: 8px; border-left: 5px solid #00ffcc; margin-bottom: 10px; border-right: 5px solid #00ffcc; }
    </style>
""", unsafe_allow_html=True)

st.title("🦆 DUCK HUNTER — WHALE TRACKER V2")
st.write("### 📡 Scanner de Volume das Baleias (100% Gratuito - Sem chaves)")

# Painel Lateral de Controle
st.sidebar.header("🕹️ CONFIGURAÇÕES DO RADAR")
moedas_para_rastrear = st.sidebar.multiselect(
    "Escolha as moedas para caçar:",
    ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT'],
    default=['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
)

# Filtro de volume agressivo
volume_gatilho = st.sidebar.slider("Volume Mínimo nas últimas 24h (Milhões de USD)", 10, 500, 50)

if 'radar_ativo' not in st.session_state:
    st.session_state.radar_ativo = False
    st.session_state.alertas_baleias = []

if st.sidebar.button("⚡ LIGAR / DESLIGAR RADAR"):
    st.session_state.radar_ativo = not st.session_state.radar_ativo

# Estatísticas na tela principal
col1, col2 = st.columns(2)
with col1:
    status = "🟢 RADAR CAÇANDO BALEIAS..." if st.session_state.radar_ativo else "🔴 RADAR DESLIGADO"
    st.metric(label="Status do Sistema", value=status)
with col2:
    st.metric(label="Anomalias Detectadas", value=len(st.session_state.alertas_baleias))

st.write("---")
st.write("### 🌊 Movimentações Suspeitas do Mercado (Direto da Binance)")

# Função para ler os dados da API pública e grátis da Binance
def escanear_binance():
    url = "https://binance.com"
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            return resposta.json()
    except:
        return []
    return []

if st.session_state.radar_ativo:
    st.toast("🔍 Vasculhando o livro de ordens da Binance...")
    dados_mercado = escanear_binance()
    
    for ativo in dados_mercado:
        par_moeda = ativo.get('symbol')
        
        # Filtra apenas as moedas que você escolheu na barra lateral
        if par_moeda in moedas_para_rastrear:
            preco_atual = float(ativo.get('lastPrice', 0))
            volume_financeiro = float(ativo.get('quoteVolume', 0)) # Volume em dólares
            variacao_preco = float(ativo.get('priceChangePercent', 0))
            
            volume_em_milhoes = volume_financeiro / 1_000_000
            
            # Se o volume da moeda ultrapassar o que você configurou, gera o alerta
            if volume_em_milhoes >= volume_gatilho:
                alerta_id = f"{par_moeda}-{time.time()}"
                
                # Evita duplicar alertas muito rápido na tela
                if not any(a['moeda'] == par_moeda for a in st.session_state.alertas_baleias[:3]):
                    novo_alerta = {
                        "moeda": par_moeda,
                        "preco": preco_atual,
                        "volume": volume_em_milhoes,
                        "variacao": variacao_preco
                    }
                    st.session_state.alertas_baleias.insert(0, novo_alerta)
                    st.toast(f"🚨 MOVIMENTAÇÃO FORTE EM {par_moeda}!")

# Mostrar os resultados na tela com estilo Hacker
if st.session_state.alertas_baleias:
    for alerta in st.session_state.alertas_baleias[:15]: # Mostra as últimas 15 movimentações
        cor_variacao = "🟢" if alerta['variacao'] >= 0 else "🔴"
        
        st.markdown(f"""
            <div class="baleia-detectada">
                <h4>🪙 PAR DE TRADING: {alerta['moeda']}</h4>
                <p><b>Preço Atual:</b> ${alerta['preco']:,.2f} | Variação nas últimas 24h: {cor_variacao} {alerta['variacao']:.2f}%</p>
                <p style="color: #ffcc00;"><b>🐋 Volume Injetado pelas Baleias: ${alerta['volume']:,.2f} MILHÕES DE DÓLARES</b></p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("🦆 O radar está monitorando os dados públicos... Ligue o radar para caçar o volume das baleias.")

# Sistema de recarregamento automático a cada 5 segundos
time.sleep(5)
if st.session_state.radar_ativo:
    st.rerun()
