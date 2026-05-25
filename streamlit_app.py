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

# CSS Premium Terminal Quantum - Margens Fixas e Visual HFT
st.html("""
    <style>
    .block-container { 
        padding-top: 4.5rem !important; 
        padding-bottom: 2rem !important; 
        max-width: 96% !important;
    }
    .reportview-container { background: #060913 !important; color: #e2e8f0; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedSidebarMenu"] { display: none !important; }
    
    /* Cabeçalho Limpo Corporativo */
    .brand-header {
        font-size: 21px; 
        font-weight: 900; 
        color: #00ffc4; 
        font-family: 'Courier New', monospace; 
        letter-spacing: 2px;
        text-shadow: 0 0 12px rgba(0, 255, 196, 0.4);
    }
    
    /* Grid de Painéis Horizontais */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 14px;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .panel-card {
        background: #0b0f19;
        border: 1px solid #1e293b;
        padding: 14px 18px;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .panel-label { font-size: 10px; text-transform: uppercase; color: #475569; font-weight: 800; letter-spacing: 1px; }
    .panel-value { font-size: 23px; font-weight: bold; color: #ffffff; margin-top: 2px; font-family: 'Courier New', monospace; }
    .panel-subvalue { font-size: 11px; color: #94a3b8; margin-top: 2px; }
    
    /* HUD de Mensagens da IA */
    .target-bar {
        background-color: #0c1524;
        border: 1px solid #1d4ed8;
        padding: 6px 14px;
        border-radius: 4px;
        color: #38bdf8;
        font-size: 11.5px;
        font-weight: 700;
        text-align: center;
        letter-spacing: 0.5px;
    }
    
    /* Caixa do Terminal Limpa */
    .terminal-box {
        background: #03050a !important;
        border: 1px solid #1e293b !important;
        border-left: 3px solid #00ffc4 !important;
        padding: 15px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 12.5px;
        min-height: 220px;
        max-height: 350px;
        overflow-y: auto;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.6);
    }
    
    /* Central de Exportação Inline */
    div[data-testid="stDownloadButton"] button {
        background-color: #0c1524 !important;
        border: 1px solid #00ffc4 !important;
        color: #00ffc4 !important;
        padding: 6px 18px !important;
        font-size: 12px !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        width: 100% !important;
    }
    div[data-testid="stDownloadButton"] button:hover { background-color: #00ffc4 !important; color: #060913 !important; }
    </style>
""")

# -------------------------------------------------------------------
# Inicialização Isolada de Memória Local
# -------------------------------------------------------------------
if 'saldo_usdt' not in st.session_state: st.session_state['saldo_usdt'] = 10000.0
if 'saldo_btc' not in st.session_state: st.session_state['saldo_btc'] = 0.0
if 'preco_compra_btc' not in st.session_state: st.session_state['preco_compra_btc'] = 0.0
if 'saldo_eth' not in st.session_state: st.session_state['saldo_eth'] = 0.0
if 'preco_compra_eth' not in st.session_state: st.session_state['preco_compra_eth'] = 0.0
if 'saldo_sol' not in st.session_state: st.session_state['saldo_sol'] = 0.0
if 'preco_compra_sol' not in st.session_state: st.session_state['preco_compra_sol'] = 0.0
if 'historico' not in st.session_state: st.session_state['historico'] = []
if 'bot_ativo' not in st.session_state: st.session_state['bot_ativo'] = False
if 'lucro_total' not in st.session_state: st.session_state['lucro_total'] = 0.0
if 'db_sincronizado' not in st.session_state: st.session_state['db_sincronizado'] = False

# -------------------------------------------------------------------
# Conexão de Dados e Sincronização Unidirecional Inicial
# -------------------------------------------------------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or st.secrets.get("supabase_url")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or st.secrets.get("supabase_key")

@st.cache_resource
def init_supabase():
    try: return create_client(SUPABASE_URL, SUPABASE_KEY)
    except: return None

db_client = init_supabase()
exchange = ccxt.binance({'enableRateLimit': True})

if db_client and not st.session_state['db_sincronizado']:
    try:
        res = db_client.table("duck_memory").select("*").eq("id", 1).execute()
        if res.data and len(res.data) > 0:
            dados = res.data[0]
            st.session_state['bot_ativo'] = dados.get('bot_ativo', False)
            st.session_state['saldo_usdt'] = float(dados.get('saldo_usdt', 10000.0))
            st.session_state['saldo_btc'] = float(dados.get('saldo_btc', 0.0))
            st.session_state['preco_compra_btc'] = float(dados.get('preco_compra_btc', 0.0))
            st.session_state['saldo_eth'] = float(dados.get('saldo_eth', 0.0))
            st.session_state['preco_compra_eth'] = float(dados.get('preco_compra_eth', 0.0))
            st.session_state['saldo_sol'] = float(dados.get('saldo_sol', 0.0))
            st.session_state['preco_compra_sol'] = float(dados.get('preco_compra_sol', 0.0))
            st.session_state['historico'] = dados.get('historico_logs', [])
            st.session_state['lucro_total'] = float(dados.get('lucro_total', 0.0))
            st.session_state['db_sincronizado'] = True
    except: pass

def salvar_na_nuvem_background():
    if db_client:
        try:
            db_client.table("duck_memory").update({
                "saldo_usdt": st.session_state['saldo_usdt'],
                "saldo_btc": st.session_state['saldo_btc'],
                "preco_compra_btc": st.session_state['preco_compra_btc'],
                "saldo_eth": st.session_state['saldo_eth'],
                "preco_compra_eth": st.session_state['preco_compra_eth'],
                "saldo_sol": st.session_state['saldo_sol'],
                "preco_compra_sol": st.session_state['preco_compra_sol'],
                "historico_logs": st.session_state['historico'][-25:],
                "bot_ativo": st.session_state['bot_ativo'],
                "lucro_total": st.session_state['lucro_total']
            }).eq("id", 1).execute()
        except: pass
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
        
        rsi_c, rsi_v, stop, status = (32, 68, 1.8, "🛡️ MODO PROTEÇÃO") if vola > 0.15 else (40, 60, 2.5, "🔥 CAÇA LUCRO")
        
        gatilho = "AGUARDAR"
        if rsi <= rsi_c: gatilho = "COMPRAR"
        elif rsi >= rsi_v: gatilho = "VENDER"
        
        return fechamentos[-1], gatilho, rsi, stop, status
    except:
        return base_p, "AGUARDAR", 50.0, 2.5, "⚙️ SYNCING"

# -------------------------------------------------------------------
# Motor de Loop Operacional Multi-Ativo e Definição de Mensagens
# -------------------------------------------------------------------
precos_reais = {"btc": 65000.0, "eth": 3450.0, "sol": 160.0}

if st.session_state['bot_ativo']:
    st_autorefresh(interval=4000, key="duck_hunter_heartbeat_v16")
    t_atual = time.strftime('%H:%M:%S')
    
    for m, par, base in [("btc", "BTC/USDT", 65000.0), ("eth", "ETH/USDT", 3450.0), ("sol", "SOL/USDT", 160.0)]:
        pr, acao, rsi, sl, status = analisar_mercado_autonomo(par, base)
        precos_reais[m] = pr
        msg_ia = f"🦅 CAÇANDO ATIVOS INTEGRADOS // {status} // TRAILING STOP: -{sl}%"
        
        saldo_token = st.session_state[f"saldo_{m}"]
        pm_token = st.session_state[f"preco_compra_{m}"]
        
        if acao == "COMPRAR" and st.session_state['saldo_usdt'] >= 300:
            aloc = st.session_state['saldo_usdt'] * 0.20
            st.session_state['saldo_usdt'] -= aloc
            st.session_state[f"saldo_{m}"] += aloc / pr
            st.session_state[f"preco_compra_{m}"] = pr
            st.session_state['historico'].insert(0, f"🛒 [{t_atual}] [EXEC_BUY]: {m.upper()} alocado a ${pr:,.2f} // RSI: {rsi:.1f}")
            salvar_na_nuvem_background()
            
        elif acao == "VENDER" and saldo_token > 0 and pr > pm_token:
            ret = saldo_token * pr
            lucro = ret - (saldo_token * pm_token)
            st.session_state['saldo_usdt'] += ret
            st.session_state['lucro_total'] += lucro
            st.session_state[f"saldo_{m}"], st.session_state[f"preco_compra_{m}"] = 0.0, 0.0
            st.session_state['historico'].insert(0, f"💰 [{t_atual}] [PROFIT]: {m.upper()} liquidado | Lucro: +${lucro:,.2f}")
            salvar_na_nuvem_background()

        if saldo_token > 0 and pm_token > 0:
            desvalorizacao = ((pr - pm_token) / pm_token) * 100
            if desvalorizacao <= -sl:
                ret = saldo_token * pr
                perda = (saldo_token * pm_token) - ret
                st.session_state['saldo_usdt'] += ret
                st.session_state['lucro_total'] -= perda
                st.session_state[f"saldo_{m}"], st.session_state[f"preco_compra_{m}"] = 0.0, 0.0
                st.session_state['historico'].insert(0, f"🚨 [{t_atual}] [STOP]: Proteção em {m.upper()} | -${perda:,.2f}")
                salvar_na_nuvem_background()
else:
    msg_ia = "RADAR EM STANDBY // MOTOR INTEGRADO"
    for m, par, base in [("btc", "BTC/USDT", 65000.0), ("eth", "ETH/USDT", 3450.0), ("sol", "SOL/USDT", 160.0)]:
        try:
            ticker = exchange.fetch_ticker(par)
            precos_reais[m] = ticker['last']
        except:
            precos_reais[m] = base

# -------------------------------------------------------------------
# Renderização da Interface Visual HUD Unificada (Premium)
# -------------------------------------------------------------------
c_tit, c_tog, c_bar = st.columns([2.0, 1.4, 6.6])
with c_tit:
    st.html('<div class="brand-header">DUCK HUNTER</div>')
with c_tog:
    # Função de callback direto linkada ao estado nativo para evitar resets
    def toggle_callback():
        st.session_state['bot_ativo'] = st.session_state['toggle_radar_key']
        salvar_na_nuvem_background()

    st.toggle(
        "Status", 
        value=st.session_state['bot_ativo'], 
        key="toggle_radar_key", 
        label_visibility="collapsed",
        on_change=toggle_callback
    )
with c_bar:
    st.html(f'<div class="target-bar">⚡ QUANTUM ENGINE MATRIX // {msg_ia}</div>')

# Balanço Global - Grid Premium de 4 Colunas Horizontais
patr = st.session_state['saldo_usdt'] + sum(st.session_state[f"saldo_{m}"] * precos_reais[m] for m in ["btc", "eth", "sol"])

c_m1, c_m2, c_m3, c_m4 = st.columns(4)
with c_m1:
    st.html(f'<div class="panel-card"><div class="panel-label">🔻 NET WORTH PATRIMÔNIO</div><div class="panel-value" style="color:#00ffc4;">${patr:,.2f}</div><div class="panel-subvalue">CAIXA: ${st.session_state["saldo_usdt"]:,.2f} | PNL: ${st.session_state["lucro_total"]:,.2f}</div></div>')
with c_m2:
    st.html(f'<div class="panel-card"><div class="panel-label">BTC OPERATIONAL NODE</div><div class="panel-value">{st.session_state["saldo_btc"]:.4f} BTC</div><div class="panel-subvalue">Pm: ${st.session_state["preco_compra_btc"]:,.2f} | <span style="color:#00ffc4;">Pr: ${precos_reais["btc"]:,.2f}</span></div></div>')
with c_m3:
    st.html(f'<div class="panel-card"><div class="panel-label">ETH OPERATIONAL NODE</div><div class="panel-value">{st.session_state["saldo_eth"]:.3f} ETH</div><div class="panel-subvalue">Pm: ${st.session_state["preco_compra_eth"]:,.2f} | <span style="color:#00ffc4;">Pr: ${precos_reais["eth"]:,.2f}</span></div></div>')
with c_m4:
    st.html(f'<div class="panel-card"><div class="panel-label">SOL OPERATIONAL NODE</div><div class="panel-value">{st.session_state["saldo_sol"]:.2f} SOL</div><div class="panel-subvalue">Pm: ${st.session_state["preco_compra_sol"]:,.2f} | <span style="color:#00ffc4;">Pr: ${precos_reais["sol"]:,.2f}</span></div></div>')

st.write("")

# -------------------------------------------------------------------
# Central Única de Exportação Inline (Alinhada na Frente)
# -------------------------------------------------------------------
st.markdown("<p style='font-size: 11px; font-weight: 800; color:#475569; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; margin-bottom: 2px;'>📋 CENTRAL DE EXPORTAÇÃO E AUDITORIA DE OPERAÇÕES</p>", unsafe_allow_html=True)

df_logs = pd.DataFrame({"Registro de Auditoria": st.session_state['historico'] if st.session_state['historico'] else ["Nenhum registro ainda."]})

c_sel, c_btn, _ = st.columns([4.0, 3.0, 3.0])
with c_sel:
    formato = st.selectbox(
        "Selecione o formato de saída do documento", 
        ["Planilha Excel (.csv)", "Bloco de Notas (.txt)", "Relatório Comercial (.pdf)"],
        label_visibility="collapsed"
    )
    
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
    buf_dados = io.StringIO()
    buf_dados.write("==================================================\n")
    buf_dados.write("            DUCK HUNTER EXECUTIVE REPORT          \n")
    buf_dados.write("==================================================\n\n")
    for log in st.session_state['historico']:
        buf_dados.write(f"- {log}\n")
    nome_arquivo = "report_duck.pdf"
    tipo_mime = "application/pdf"
    label_btn = "🖨️ GERAR DOCUMENTO PDF"

with c_btn:
    st.download_button(label=label_btn, data=buf_dados.getvalue(), file_name=nome_arquivo, mime=tipo_mime)

# Terminal Reativo Limpo
st.markdown("<p style='font-size: 11px; font-weight: 800; color:#475569; text-transform: uppercase; letter-spacing: 1px; margin-top: 15px; margin-bottom: 2px;'>DUCK HUNTER CAÇADOR DE OPORTUNIDADES INICIALIZADO</p>", unsafe_allow_html=True)

terminal_content = ""
if st.session_state['historico']:
    for log in st.session_state['historico'][:20]:
        if "[EXEC_" in log or "[COMPRA" in log:
            terminal_content += f"<div style='color: #00ffc4; font-weight: bold; margin-bottom: 4px;'>{log}</div>"
        elif "[PROFIT" in log or "[LUCRO" in log:
            terminal_content += f"<div style='color: #38bdf8; font-weight: bold; margin-bottom: 4px;'>{log}</div>"
        else:
            terminal_content += f"<div style='color: #64748b; margin-bottom: 4px;'>{log}</div>"

st.html(f'<div class="terminal-box">{terminal_content}</div>')
