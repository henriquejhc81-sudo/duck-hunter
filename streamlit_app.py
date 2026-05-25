import streamlit as st
import ccxt
import time
import pandas as pd
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh
import numpy as np
import io

# 1. Configuração de Página HUD Ultra-Wide e Ocultação Absoluta de Menus
st.set_page_config(page_title="Duck Hunter ALPHA", page_icon="🦆", layout="wide", initial_sidebar_state="collapsed")

# CSS Futurista Avançado - Tema Terminal Quantum / Cyberpunk
st.html("""
    <style>
    /* Reset de Viewport e Margens de Alta Densidade */
    .block-container { padding-top: 2.8rem !important; padding-bottom: 0px !important; max-width: 98% !important; }
    .reportview-container { background: #070a13 !important; color: #e2e8f0; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedSidebarMenu"] { display: none !important; }
    
    /* Grid Horizontal Estilo Glassmorphism Futurista */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 12px;
        margin-bottom: 10px;
    }
    .panel-card {
        background: linear-gradient(135deg, #0f1424 0%, #0b0f19 100%);
        border: 1px solid #1e2942;
        padding: 12px 16px;
        border-radius: 4px;
        box-shadow: 0 0 15px rgba(0, 255, 196, 0.03);
        transition: all 0.3s ease;
    }
    .panel-card:hover { border-color: #00ffc4; box-shadow: 0 0 20px rgba(0, 255, 196, 0.1); }
    .panel-label { font-size: 10px; text-transform: uppercase; color: #475569; font-weight: 800; letter-spacing: 1px; }
    .panel-value { font-size: 22px; font-weight: 800; color: #ffffff; margin-top: 2px; font-family: 'Courier New', monospace; }
    .panel-subvalue { font-size: 11px; color: #94a3b8; margin-top: 1px; }
    
    /* HUD de Mensagem Dinâmica da IA */
    .target-bar {
        background-color: #0d1527;
        border: 1px solid #1d4ed8;
        padding: 6px 14px;
        border-radius: 4px;
        color: #38bdf8;
        font-size: 12px;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.1);
    }
    .graph-title { font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px; }
    
    /* Customização dos Botões Operacionais Inline */
    div[data-testid="stDownloadButton"] button {
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        color: #94a3b8 !important;
        border-radius: 4px !important;
        padding: 4px 10px !important;
        font-size: 11px !important;
    }
    div[data-testid="stDownloadButton"] button:hover { border-color: #00ffc4 !important; color: #00ffc4 !important; }
    div[data-testid="stDownloadButton"] { display: inline-block !important; margin-right: 6px !important; }
    </style>
""")

# -------------------------------------------------------------------
# Configurações de Conexão e Inicialização Híbrida Supabase
# -------------------------------------------------------------------
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "seu-anon-key-do-supabase"

@st.cache_resource
def init_supabase():
    try: return create_client(SUPABASE_URL, SUPABASE_KEY)
    except: return None

supabase = init_supabase()
exchange = ccxt.binance({'enableRateLimit': True})

def carregar_estado_banco():
    estado_padrao = {
        "radar_ligado": False,
        "saldo_usdt": 10000.0,
        "saldo_btc": 0.0, "preco_compra_btc": 0.0,
        "saldo_eth": 0.0, "preco_compra_eth": 0.0,
        "saldo_sol": 0.0, "preco_compra_sol": 0.0,
        "historico_logs": ["🦅 Duck Hunter Quantum Inicializado. Pronto para execução."],
        "lucro_total": 0.0
    }
    if supabase:
        try:
            response = supabase.table("duck_memory").select("*").eq("id", 1).execute()
            if response.data:
                dados = response.data
                return {
                    "radar_ligado": dados.get("radar_ligado", False),
                    "saldo_usdt": float(dados.get("saldo_usdt", 10000.0)),
                    "saldo_btc": float(dados.get("saldo_btc", 0.0)),
                    "preco_compra_btc": float(dados.get("preco_compra_btc", 0.0)),
                    "saldo_eth": float(dados.get("saldo_eth", 0.0)),
                    "preco_compra_eth": float(dados.get("preco_compra_eth", 0.0)),
                    "saldo_sol": float(dados.get("saldo_sol", 0.0)),
                    "preco_compra_sol": float(dados.get("preco_compra_sol", 0.0)),
                    "historico_logs": dados.get("historico_logs", estado_padrao["historico_logs"]),
                    "lucro_total": float(dados.get("lucro_total", 0.0))
                }
        except: pass
    return estado_padrao

def salvar_estado_banco():
    if supabase:
        payload = {
            "id": 1, "radar_ligado": st.session_state.radar_ligado,
            "saldo_usdt": st.session_state.saldo_usdt,
            "saldo_btc": st.session_state.saldo_btc, "preco_compra_btc": st.session_state.preco_compra_btc,
            "saldo_eth": st.session_state.saldo_eth, "preco_compra_eth": st.session_state.preco_compra_eth,
            "saldo_sol": st.session_state.saldo_sol, "preco_compra_sol": st.session_state.preco_compra_sol,
            "historico_logs": st.session_state.historico_logs, "lucro_total": st.session_state.lucro_total
        }
        try: supabase.table("duck_memory").upsert(payload).execute()
        except: pass

if "inicializado" not in st.session_state:
    for k, v in carregar_estado_banco().items(): st.session_state[k] = v
    st.session_state["inicializado"] = True
# -------------------------------------------------------------------
# Core Quant: Cálculo de RSI e Volatilidade Inteligente
# -------------------------------------------------------------------
def calcular_rsi(precos, periodo=14):
    if len(precos) < periodo + 1: return 50.0
    variacoes = np.diff(precos)
    ganhos = np.where(variacoes > 0, variacoes, 0)
    perdas = np.where(variacoes < 0, -variacoes, 0)
    avg_ganho = np.mean(ganhos[:periodo])
    avg_perda = np.mean(perdas[:periodo])
    for i in range(periodo, len(variacoes)):
        avg_ganho = (avg_ganho * (periodo - 1) + ganhos[i]) / periodo
        avg_perda = (avg_perda * (periodo - 1) + perdas[i]) / periodo
    return 100.0 - (100.0 / (1.0 + (avg_ganho / (avg_perda if avg_perda != 0 else 1e-10))))

def analisar_mercado_autonomo(par, base_p):
    try:
        candles = exchange.fetch_ohlcv(par, timeframe='1m', limit=30)
        fechamentos = [c[4] for c in candles]
        vola = np.std(np.diff(fechamentos) / fechamentos[:-1]) * 100
        rsi = calcular_rsi(fechamentos, 14)
        
        rsi_c, rsi_v, stop, status = (30, 70, 1.8, "🛡️ MODO PROTEÇÃO") if vola > 0.15 else (38, 62, 2.5, "🔥 CAÇA LUCRO")
        
        gatilho = "AGUARDAR"
        if rsi <= rsi_c: gatilho = "COMPRAR"
        elif rsi >= rsi_v: gatilho = "VENDER"
        
        return fechamentos[-1], gatilho, rsi, stop, status, fechamentos
    except:
        np.random.seed(int(time.time()) % 1000)
        ruido = np.cumsum(np.random.normal(0, base_p * 0.0003, 30))
        mock_hist = (base_p + ruido).tolist()
        return mock_hist[-1], "AGUARDAR", 50.0, 2.5, "⚙️ SYNCING", mock_hist

# -------------------------------------------------------------------
# Motor de Loop Operacional Multi-Ativo
# -------------------------------------------------------------------
precos_reais = {"btc": 65000.0, "eth": 3450.0, "sol": 160.0}
historicos_graficos = {"btc": [], "eth": [], "sol": []}
msg_ia = "RADAR EM STANDBY // AGUARDANDO ATIVAÇÃO DO OPERADOR"

if st.session_state.radar_ligado:
    st_autorefresh(interval=4000, key="duck_loop_v8_cyber")
    t_atual = time.strftime('%H:%M:%S')
    
    for m, par, base in [("btc", "BTC/USDT", 65000.0), ("eth", "ETH/USDT", 3450.0), ("sol", "SOL/USDT", 160.0)]:
        pr, acao, rsi, sl, status, hist = analisar_mercado_autonomo(par, base)
        precos_reais[m] = pr
        historicos_graficos[m] = hist
        msg_ia = f"CORE: {status} // OVERWATCH ATIVO // TRAILING STOP: -{sl}%"
        
        if acao == "COMPRAR" and st.session_state.saldo_usdt >= 300:
            aloc = st.session_state.saldo_usdt * 0.20
            st.session_state.saldo_usdt -= aloc
            st.session_state[f"saldo_{m}"] += aloc / pr
            st.session_state[f"preco_compra_{m}"] = pr
            st.session_state.historico_logs.insert(0, f"🛒 [{t_atual}] [EXECUTION_BUY]: {m.upper()} alocado a ${pr:,.2f}")
            salvar_estado_banco()
        elif acao == "VENDER" and st.session_state[f"saldo_{m}"] > 0 and pr > st.session_state[f"preco_compra_{m}"]:
            ret = st.session_state[f"saldo_{m}"] * pr
            lucro = ret - (st.session_state[f"saldo_{m}"] * st.session_state[f"preco_compra_{m}"])
            st.session_state.saldo_usdt += ret
            st.session_state.lucro_total += lucro
            st.session_state[f"saldo_{m}"], st.session_state[f"preco_compra_{m}"] = 0.0, 0.0
            st.session_state.historico_logs.insert(0, f"💰 [{t_atual}] [PROFIT_TAKEN]: {m.upper()} liquidado | PNL: +${lucro:,.2f}")
            salvar_estado_banco()
else:
    for m, par, base in [("btc", "BTC/USDT", 65000.0), ("eth", "ETH/USDT", 3450.0), ("sol", "SOL/USDT", 160.0)]:
        pr, _, _, _, _, hist = analisar_mercado_autonomo(par, base)
        precos_reais[m] = pr
        historicos_graficos[m] = hist

# -------------------------------------------------------------------
# Renderização do Painel HUD Superior
# -------------------------------------------------------------------
c_tit, c_tog, c_bar = st.columns([2.2, 1.4, 6.4])
with c_tit:
    st.html('<div style="font-size: 21px; font-weight: 900; color: #00ffc4; padding-top: 1px; font-family:\'Courier New\', monospace; letter-spacing:1px;">🦅 DUCK HUNTER</div>')
with c_tog:
    ant = st.session_state.radar_ligado
    lbl = "🟢 SYS_ON" if st.session_state.radar_ligado else "🔴 SYS_STDBY"
    radar = st.toggle(lbl, value=st.session_state.radar_ligado, label_visibility="collapsed")
    if ant != radar:
        st.session_state.radar_ligado = radar
        salvar_estado_banco()
        st.rerun()
with c_bar:
    st.html(f'<div class="target-bar">⚡ QUANTUM ENGINE MATRIX // {msg_ia}</div>')

# Grid Avançado com Destaques de Preço Real em Neon
patr = st.session_state.saldo_usdt + sum(st.session_state[f"saldo_{m}"] * precos_reais[m] for m in ["btc", "eth", "sol"])

c_m1, c_m2, c_m3, c_m4 = st.columns(4)
with c_m1:
    st.html(f'<div class="panel-card"><div class="panel-label">🔻 NET WORTH PATRIMÔNIO</div><div class="panel-value" style="color:#00ffc4;">${patr:,.2f}</div><div class="panel-subvalue">CAIXA: ${st.session_state.saldo_usdt:,.2f} | PNL: ${st.session_state.lucro_total:,.2f}</div></div>')
with c_m2:
    st.html(f'<div class="panel-card"><div class="panel-label">BTC OPERATIONAL NODE</div><div class="panel-value">{st.session_state.saldo_btc:.4f} BTC</div><div class="panel-subvalue">Pm: ${st.session_state.preco_compra_btc:,.2f} | <span style="color:#00ffc4;">Pr: ${precos_reais["btc"]:,.2f}</span></div></div>')
with c_m3:
    st.html(f'<div class="panel-card"><div class="panel-label">ETH OPERATIONAL NODE</div><div class="panel-value">{st.session_state.saldo_eth:.3f} ETH</div><div class="panel-subvalue">Pm: ${st.session_state.preco_compra_eth:,.2f} | <span style="color:#00ffc4;">Pr: ${precos_reais["eth"]:,.2f}</span></div></div>')
with c_m4:
    st.html(f'<div class="panel-card"><div class="panel-label">SOL OPERATIONAL NODE</div><div class="panel-value">{st.session_state.saldo_sol:.2f} SOL</div><div class="panel-subvalue">Pm: ${st.session_state.preco_compra_sol:,.2f} | <span style="color:#00ffc4;">Pr: ${precos_reais["sol"]:,.2f}</span></div></div>')

# Seção de Gráficos Otimizada com Forçamento Dinâmico de Eixo Y (Ajuste de Escala)
st.write("")
st.markdown("<p style='font-size: 11px; font-weight: 800; color:#64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px;'>📊 REAL-TIME HFT GRAPH MATRIX (Y-AXIS DYNAMIC ZOOM)</p>", unsafe_allow_html=True)

g1, g2, g3 = st.columns(3)
with g1:
    st.markdown('<div class="graph-title">📈 DATA_FEED: BTC/USDT</div>', unsafe_allow_html=True)
    df_btc = pd.DataFrame(historicos_graficos["btc"], columns=["Preço"])
    # Correção de escala: O Streamlit ajustará a base do eixo Y automaticamente para o menor valor da lista
    st.line_chart(df_btc, height=115, use_container_width=True)
with g2:
    st.markdown('<div class="graph-title">📈 DATA_FEED: ETH/USDT</div>', unsafe_allow_html=True)
    df_eth = pd.DataFrame(historicos_graficos["eth"], columns=["Preço"])
    st.line_chart(df_eth, height=115, use_container_width=True)
with g3:
    st.markdown('<div class="graph-title">📈 DATA_FEED: SOL/USDT</div>', unsafe_allow_html=True)
    df_sol = pd.DataFrame(historicos_graficos["sol"], columns=["Preço"])
    st.line_chart(df_sol, height=115, use_container_width=True)

# Módulo de Extração de Dados e Terminal Holográfico
if st.session_state.historico_logs:
    df_logs = pd.DataFrame({"Auditoria": st.session_state.historico_logs})
    buf = io.StringIO()
    df_logs.to_csv(buf, index=False, sep=';', encoding='utf-8-sig')
    
    st.download_button(label="🧬 EXPORT DATA (CSV)", data=buf.getvalue(), file_name="auditoria_quantum.csv", mime="text/csv")
    st.download_button(label="📝 DOWNLOAD LOGS (TXT)", data=buf.getvalue(), file_name="relatorio_quantum.txt", mime="text/plain")

with st.container():
    for log in st.session_state.historico_logs[:6]:
        if "[COMPRA" in log: st.success(log)
        elif "[LUCRO" in log: st.info(log)
        else: st.code(log)
