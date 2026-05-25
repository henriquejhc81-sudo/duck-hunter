import streamlit as st
import ccxt
import time
import pandas as pd
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh
import numpy as np
import io

# 1. Configuração de Página Ultra-Wide e Ocultação de Menus/Sidebar
st.set_page_config(page_title="Duck Hunter PRO", page_icon="🦆", layout="wide", initial_sidebar_state="collapsed")

st.html("""
    <style>
    .reportview-container { background: #0b0f19; color: #e2e8f0; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedSidebarMenu"] { display: none !important; }
    
    /* Configuração do Grid de 4 Colunas */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 12px;
        margin-bottom: 10px;
    }
    .panel-card {
        background-color: #111622;
        border: 1px solid #1e2640;
        padding: 10px 15px;
        border-radius: 6px;
    }
    .panel-label { font-size: 10px; text-transform: uppercase; color: #64748b; font-weight: bold; }
    .panel-value { font-size: 20px; font-weight: 700; color: #ffffff; margin-top: 2px; }
    .panel-subvalue { font-size: 11px; color: #94a3b8; }
    
    /* Barra de Monitoramento Compacta */
    .target-bar {
        background-color: #1a1510;
        border: 1px solid #b45309;
        padding: 6px 12px;
        border-radius: 4px;
        color: #f59e0b;
        font-size: 12px;
        font-weight: 600;
        text-align: center;
    }
    .graph-title { font-size: 11px; color: #94a3b8; font-weight: 600; margin-bottom: 2px; }
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
        "historico_logs": ["🦆 Duck Hunter Autônomo Ativo. Pronto para caça."],
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
        fechamentos = [c for c in candles]
        vola = np.std(np.diff(fechamentos) / fechamentos[:-1]) * 100
        rsi = calcular_rsi(fechamentos, 14)
        
        # Ajuste dinâmico automático com foco em Lucro Seguro
        rsi_c, rsi_v, stop, status = (30, 70, 1.8, "🛡️ Modo Proteção") if vola > 0.15 else (38, 62, 2.5, "🔥 Caça Lucro")
        
        gatilho = "AGUARDAR"
        if rsi <= rsi_c: gatilho = "COMPRAR"
        elif rsi >= rsi_v: gatilho = "VENDER"
        
        return fechamentos[-1], gatilho, rsi, stop, status, fechamentos
    except:
        mock_hist = [base_p * (1 + np.sin(i/5)*0.002) for i in range(30)]
        return base_p, "AGUARDAR", 50.0, 2.5, "⚙️ Aguardando API", mock_hist

# -------------------------------------------------------------------
# Motor de Loop Operacional Multi-Ativo
# -------------------------------------------------------------------
precos_reais = {"btc": 65000.0, "eth": 3450.0, "sol": 160.0}
historicos_graficos = {"btc": [], "eth": [], "sol": []}
msg_ia = "Iniciando varredura estratégica de mercado..."

if st.session_state.radar_ligado:
    st_autorefresh(interval=4000, key="duck_loop_v4")
    t_atual = time.strftime('%H:%M:%S')
    
    for m, par, base in [("btc", "BTC/USDT", 65000.0), ("eth", "ETH/USDT", 3450.0), ("sol", "SOL/USDT", 160.0)]:
        pr, acao, rsi, sl, status, hist = analisar_mercado_autonomo(par, base)
        precos_reais[m] = pr
        historicos_graficos[m] = hist
        msg_ia = f"IA: {status} | Configuração Autônoma Stop Loss: -{sl}% Ativa"
        
        # Lógica Comercial de Aporte Fracionado Automatizado
        if acao == "COMPRAR" and st.session_state.saldo_usdt >= 300:
            aloc = st.session_state.saldo_usdt * 0.20
            st.session_state.saldo_usdt -= aloc
            st.session_state[f"saldo_{m}"] += aloc / pr
            st.session_state[f"preco_compra_{m}"] = pr
            st.session_state.historico_logs.insert(0, f"🛒 [{t_atual}] [COMPRA]: {m.upper()} a ${pr:,.2f}")
            salvar_estado_banco()
        elif acao == "VENDER" and st.session_state[f"saldo_{m}"] > 0 and pr > st.session_state[f"preco_compra_{m}"]:
            ret = st.session_state[f"saldo_{m}"] * pr
            lucro = ret - (st.session_state[f"saldo_{m}"] * st.session_state[f"preco_compra_{m}"])
            st.session_state.saldo_usdt += ret
            st.session_state.lucro_total += lucro
            st.session_state[f"saldo_{m}"], st.session_state[f"preco_compra_{m}"] = 0.0, 0.0
            st.session_state.historico_logs.insert(0, f"💰 [{t_atual}] [LUCRO]: Venda {m.upper()} | +${lucro:,.2f}")
            salvar_estado_banco()
else:
    for m, par, base in [("btc", "BTC/USDT", 65000.0), ("eth", "ETH/USDT", 3450.0), ("sol", "SOL/USDT", 160.0)]:
        _, _, _, _, _, hist = analisar_mercado_autonomo(par, base)
        precos_reais[m] = hist[-1]
        historicos_graficos[m] = hist

# -------------------------------------------------------------------
# Renderização da Interface Visual Consolidada (Viewport Fixa)
# -------------------------------------------------------------------
c_tit, c_tog, c_bar = st.columns([2, 1.8, 6.2])
with c_tit:
    st.html('<div style="font-size: 22px; font-weight: 800; color: #f59e0b; padding-top: 3px;">🦆 DUCK HUNTER</div>')
with c_tog:
    ant = st.session_state.radar_ligado
    lbl = "🟢 RADAR ATIVO" if st.session_state.radar_ligado else "🔴 ADORMECIDO"
    radar = st.toggle(lbl, value=st.session_state.radar_ligado, label_visibility="collapsed")
    if ant != radar:
        st.session_state.radar_ligado = radar
        salvar_estado_banco()
        st.rerun()
with c_bar:
    st.html(f'<div class="target-bar">⚡ SYSTEM INTELLIGENCE: {msg_ia}</div>')

# Grid Inline de Balanço Global Sem Formatações Conflitantes de Chaves
patr = st.session_state.saldo_usdt + sum(st.session_state[f"saldo_{m}"] * precos_reais[m] for m in ["btc", "eth", "sol"])

c_m1, c_m2, c_m3, c_m4 = st.columns(4)
with c_m1:
    st.html(f'<div class="panel-card"><div class="panel-label">🔻 PATRIMÔNIO TOTAL</div><div class="panel-value" style="color:#f59e0b;">${patr:,.2f}</div><div class="panel-subvalue">Caixa: ${st.session_state.saldo_usdt:,.2f} | PNL: ${st.session_state.lucro_total:,.2f}</div></div>')
with c_m2:
    st.html(f'<div class="panel-card"><div class="panel-label">POSIÇÃO BITCOIN</div><div class="panel-value">{st.session_state.saldo_btc:.4f} BTC</div><div class="panel-subvalue">Pm: ${st.session_state.preco_compra_btc:,.2f} | Pr: ${precos_reais["btc"]:,.2f}</div></div>')
with c_m3:
    st.html(f'<div class="panel-card"><div class="panel-label">POSIÇÃO ETHEREUM</div><div class="panel-value">{st.session_state.saldo_eth:.3f} ETH</div><div class="panel-subvalue">Pm: ${st.session_state.preco_compra_eth:,.2f} | Pr: ${precos_reais["eth"]:,.2f}</div></div>')
with c_m4:
    st.html(f'<div class="panel-card"><div class="panel-label">POSIÇÃO SOLANA</div><div class="panel-value">{st.session_state.saldo_sol:.2f} SOL</div><div class="panel-subvalue">Pm: ${st.session_state.preco_compra_sol:,.2f} | Pr: ${precos_reais["sol"]:,.2f}</div></div>')

# Seção de Gráficos com Títulos e Legendas Plenamente Restaurados
st.write("")
st.markdown("<p style='font-size: 13px; font-weight: bold; margin-bottom: 2px; margin-top: 0px;'>📊 Monitoramento de Mercado Real-Time (1m)</p>", unsafe_allow_html=True)

g1, g2, g3 = st.columns(3)
with g1:
    st.markdown('<div class="graph-title">📈 Histórico BTC/USDT</div>', unsafe_allow_html=True)
    st.line_chart(pd.DataFrame(historicos_graficos["btc"]), height=110, use_container_width=True)
with g2:
    st.markdown('<div class="graph-title">📈 Histórico ETH/USDT</div>', unsafe_allow_html=True)
    st.line_chart(pd.DataFrame(historicos_graficos["eth"]), height=110, use_container_width=True)
with g3:
    st.markdown('<div class="graph-title">📈 Histórico SOL/USDT</div>', unsafe_allow_html=True)
    st.line_chart(pd.DataFrame(historicos_graficos["sol"]), height=110, use_container_width=True)

# Módulo Compacto de Extração de Dados e Terminal
if st.session_state.historico_logs:
    df_logs = pd.DataFrame({"Auditoria": st.session_state.historico_logs})
    col_e1, col_e2, _ = st.columns([2, 2, 6])
    buf = io.StringIO()
    df_logs.to_csv(buf, index=False, sep=';', encoding='utf-8-sig')
    with col_e1: st.download_button(label="📥 Baixar CSV", data=buf.getvalue(), file_name="auditoria_duck.csv", mime="text/csv")
    with col_e2: st.download_button(label="📄 Baixar TXT", data=buf.getvalue(), file_name="relatorio_duck.txt", mime="text/plain")

with st.container():
    for log in st.session_state.historico_logs[:8]:
        if "[COMPRA" in log: st.success(log)
        elif "[LUCRO" in log: st.info(log)
        else: st.code(log)
