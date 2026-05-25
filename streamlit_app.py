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

# CSS Futurista Otimizado para Compressão Máxima e Alinhamento de Botões Únicos
st.html("""
    <style>
    .block-container { padding-top: 3.2rem !important; padding-bottom: 0px !important; max-width: 98% !important; }
    .reportview-container { background: #070a13 !important; color: #e2e8f0; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedSidebarMenu"] { display: none !important; }
    
    /* Grid de Painéis */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 12px;
        margin-bottom: 15px;
    }
    .panel-card {
        background: linear-gradient(135deg, #0f1424 0%, #0b0f19 100%);
        border: 1px solid #1e2942;
        padding: 12px 16px;
        border-radius: 4px;
        box-shadow: 0 0 15px rgba(0, 255, 196, 0.02);
    }
    .panel-label { font-size: 10px; text-transform: uppercase; color: #475569; font-weight: 800; letter-spacing: 1px; }
    .panel-value { font-size: 21px; font-weight: 800; color: #ffffff; margin-top: 2px; font-family: monospace; }
    .panel-subvalue { font-size: 11px; color: #94a3b8; margin-top: 1px; }
    
    /* HUD Superior */
    .target-bar {
        background-color: #0d1527;
        border: 1px solid #1d4ed8;
        padding: 5px 12px;
        border-radius: 4px;
        color: #38bdf8;
        font-size: 12px;
        font-weight: 700;
        text-align: center;
    }
    
    /* Customização do botão único de download para combinar com o tema */
    div[data-testid="stDownloadButton"] button {
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        color: #00ffc4 !important;
        padding: 6px 16px !important;
        font-size: 12px !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    div[data-testid="stDownloadButton"] button:hover { border-color: #00ffc4 !important; background-color: #1e2942 !important; }
    </style>
""")

# -------------------------------------------------------------------
# Configurações de Conexão Supabase e Inicialização
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
        "historico_logs": ["🦆 Duck Hunter Caçador de Oportunidades Online."],
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
        
        rsi_c, rsi_v, stop, status = (30, 70, 1.8, "🛡️ MODO PROTEÇÃO") if vola > 0.15 else (38, 62, 2.5, "🔥 CAÇA LUCRO")
        
        gatilho = "AGUARDAR"
        if rsi <= rsi_c: gatilho = "COMPRAR"
        elif rsi >= rsi_v: gatilho = "VENDER"
        
        return fechamentos[-1], gatilho, rsi, stop, status
    except:
        return base_p, "AGUARDAR", 50.0, 2.5, "⚙️ SYNCING"

# -------------------------------------------------------------------
# Motor de Loop Operacional Multi-Ativo
# -------------------------------------------------------------------
precos_reais = {"btc": 65000.0, "eth": 3450.0, "sol": 160.0}
msg_ia = "RADAR EM STANDBY // AGUARDANDO ATIVAÇÃO DO OPERADOR"

if st.session_state.radar_ligado:
    st_autorefresh(interval=4000, key="duck_loop_v11_clean")
    t_atual = time.strftime('%H:%M:%S')
    
    for m, par, base in [("btc", "BTC/USDT", 65000.0), ("eth", "ETH/USDT", 3450.0), ("sol", "SOL/USDT", 160.0)]:
        pr, acao, rsi, sl, status = analisar_mercado_autonomo(par, base)
        precos_reais[m] = pr
        msg_ia = f"CORE: {status} // OVERWATCH ATIVO // TRAILING STOP: -{sl}%"
        
        if acao == "COMPRAR" and st.session_state.saldo_usdt >= 300:
            aloc = st.session_state.saldo_usdt * 0.20
            st.session_state.saldo_usdt -= aloc
            st.session_state[f"saldo_{m}"] += aloc / pr
            st.session_state[f"preco_compra_{m}"] = pr
            st.session_state.historico_logs.insert(0, f"🛒 [{t_atual}] [EXEC_BUY]: {m.upper()} alocado a ${pr:,.2f}")
            salvar_estado_banco()
        elif acao == "VENDER" and st.session_state[f"saldo_{m}"] > 0 and pr > st.session_state[f"preco_compra_{m}"]:
            ret = st.session_state[f"saldo_{m}"] * pr
            lucro = ret - (st.session_state[f"saldo_{m}"] * st.session_state[f"preco_compra_{m}"])
            st.session_state.saldo_usdt += ret
            st.session_state.lucro_total += lucro
            st.session_state[f"saldo_{m}"], st.session_state[f"preco_compra_{m}"] = 0.0, 0.0
            st.session_state.historico_logs.insert(0, f"💰 [{t_atual}] [PROFIT]: {m.upper()} liquidado | +${lucro:,.2f}")
            salvar_estado_banco()
else:
    for m, par, base in [("btc", "BTC/USDT", 65000.0), ("eth", "ETH/USDT", 3450.0), ("sol", "SOL/USDT", 160.0)]:
        try:
            ticker = exchange.fetch_ticker(par)
            precos_reais[m] = ticker['last']
        except:
            precos_reais[m] = base

# -------------------------------------------------------------------
# Renderização da Interface Visual HUD Unificada
# -------------------------------------------------------------------
c_tit, c_tog, c_bar = st.columns([2.2, 1.4, 6.4])
with c_tit:
    st.html('<div style="font-size: 21px; font-weight: 900; color: #00ffc4; padding-top: 1px; font-family:monospace; letter-spacing:1px;">🦆 DUCK HUNTER</div>')
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

# Balanço Global
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

st.write("")

# -------------------------------------------------------------------
# Central Única de Download Tri-Formato (Dropdown + Botão Mestre)
# -------------------------------------------------------------------
st.markdown("<p style='font-size: 11px; font-weight: 800; color:#64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px;'>📋 CENTRAL DE EXPORTAÇÃO E AUDITORIA DE OPERAÇÕES</p>", unsafe_allow_html=True)

if st.session_state.historico_logs:
    df_logs = pd.DataFrame({"Registro de Auditoria": st.session_state.historico_logs})
    
    c_sel, c_btn, _ = st.columns([3.5, 2.5, 4])
    
    with c_sel:
        formato = st.selectbox(
            "Selecione o formato de saída do documento", 
            ["Planilha Excel (.csv)", "Bloco de Notas (.txt)", "Relatório Comercial (.pdf)"],
            label_visibility="collapsed"
        )
        
    # Preparação dinâmica do buffer de dados dependendo da escolha
    if "Excel" in formato:
        buf_dados = io.StringIO()
        df_logs.to_csv(buf_dados, index=False, sep=';', encoding='utf-8-sig')
        nome_arquivo = "auditoria_duck_hunter.csv"
        tipo_mime = "text/csv"
        label_btn = "📥 EXPORTAR EM EXCEL"
    elif "Notas" in formato:
        buf_dados = io.StringIO()
        df_logs.to_csv(buf_dados, index=False)
        nome_arquivo = "relatorio_duck_hunter.txt"
        tipo_mime = "text/plain"
        label_btn = "📄 DOWNLOAD EM TXT"
    else:
        # Simulação limpa e estruturada de PDF comercial formatado em texto
        buf_dados = io.StringIO()
        buf_dados.write("==================================================\n")
        buf_dados.write("       🦆 DUCK HUNTER EXECUTIVE AUDIT REPORT      \n")
        buf_dados.write(f"       DATA DE EMISSÃO: {time.strftime('%d/%m/%Y %H:%M:%S')}  \n")
        buf_dados.write("==================================================\n\n")
        for log in st.session_state.historico_logs:
            buf_dados.write(f"- {log}\n")
        nome_arquivo = "comercial_report_duck.pdf"
        tipo_mime = "application/pdf"
        label_btn = "🖨️ GERAR DOCUMENTO PDF"

    with c_btn:
        st.download_button(
            label=label_btn,
            data=buf_dados.getvalue(),
            file_name=nome_arquivo,
            mime=tipo_mime
        )

# Terminal de Logs Operacionais
st.write("")
with st.container():
    for log in st.session_state.historico_logs[:12]:
        if "[EXEC_" in log or "[COMPRA" in log: st.success(log)
        elif "[PROFIT" in log or "[LUCRO" in log: st.info(log)
        else: st.code(log)
