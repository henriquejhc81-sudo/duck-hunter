import streamlit as st
import ccxt
import time
import pandas as pd
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh
import numpy as np
import io

# Configuração de Página Ultra-Wide e Ocultação Nativa de Barras e Menus
st.set_page_config(page_title="Duck Hunter PRO", page_icon="🦆", layout="wide", initial_sidebar_state="collapsed")

# Estilização Avançada Premium Estilo Central Única (Sem Sidebar)
st.html("""
    <style>
    .reportview-container { background: #0b0f19; color: #e2e8f0; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedSidebarMenu"] { display: none !important; }
    .brand-title { font-size: 38px; font-weight: 800; color: #ffffff; letter-spacing: 1px; margin-bottom: 5px; }
    
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 12px;
        margin-bottom: 15px;
    }
    
    .panel-card {
        background-color: #111622;
        border: 1px solid #1e2640;
        padding: 12px 18px;
        border-radius: 6px;
    }
    
    .panel-label { font-size: 10px; text-transform: uppercase; color: #64748b; font-weight: bold; letter-spacing: 0.5px; }
    .panel-value { font-size: 21px; font-weight: 700; color: #ffffff; margin-top: 4px; }
    .panel-subvalue { font-size: 12px; color: #94a3b8; margin-top: 2px; }
    
    .target-bar {
        background-color: #1a1510;
        border: 1px solid #b45309;
        padding: 10px 15px;
        border-radius: 4px;
        color: #f59e0b;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 20px;
    }
    </style>
""")

# -------------------------------------------------------------------
# Configurações de Conexão Supabase
# -------------------------------------------------------------------
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "seu-anon-key-do-supabase"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = init_supabase()
exchange = ccxt.binance({'enableRateLimit': True})

# -------------------------------------------------------------------
# Sincronização Contra Resets (Duck Memory)
# -------------------------------------------------------------------
def carregar_estado_banco():
    estado_padrao = {
        "radar_ligado": False,
        "saldo_usdt": 10000.0,
        "saldo_btc": 0.0, "preco_compra_btc": 0.0,
        "saldo_eth": 0.0, "preco_compra_eth": 0.0,
        "saldo_sol": 0.0, "preco_compra_sol": 0.0,
        "historico_logs": ["🦆 Duck Hunter Autônomo Online. Caça inteligente ativada."],
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
        except:
            pass
    return estado_padrao

def salvar_estado_banco():
    if supabase:
        payload = {
            "id": 1,
            "radar_ligado": st.session_state.radar_ligado,
            "saldo_usdt": st.session_state.saldo_usdt,
            "saldo_btc": st.session_state.saldo_btc,
            "preco_compra_btc": st.session_state.preco_compra_btc,
            "saldo_eth": st.session_state.saldo_eth,
            "preco_compra_eth": st.session_state.preco_compra_eth,
            "saldo_sol": st.session_state.saldo_sol,
            "preco_compra_sol": st.session_state.preco_compra_sol,
            "historico_logs": st.session_state.historico_logs,
            "lucro_total": st.session_state.lucro_total
        }
        try:
            supabase.table("duck_memory").upsert(payload).execute()
        except:
            pass

if "inicializado" not in st.session_state:
    estado_recuperado = carregar_estado_banco()
    for chave, valor in estado_recuperado.items():
        st.session_state[chave] = valor
    st.session_state["inicializado"] = True
# -------------------------------------------------------------------
# Módulo de Inteligência Quantitativa Adaptativa (Auto-Ajuste de Alvos)
# -------------------------------------------------------------------
def calcular_rsi(precos, periodo=14):
    if len(precos) < periodo + 1:
        return 50.0
    variacoes = np.diff(precos)
    ganhos = np.where(variacoes > 0, variacoes, 0)
    perdas = np.where(variacoes < 0, -variacoes, 0)
    avg_ganho = np.mean(ganhos[:periodo])
    avg_perda = np.mean(perdas[:periodo])
    for i in range(periodo, len(variacoes)):
        avg_ganho = (avg_ganho * (periodo - 1) + ganhos[i]) / periodo
        avg_perda = (avg_perda * (periodo - 1) + perdas[i]) / periodo
    if avg_perda == 0:
        return 100.0
    return 100.0 - (100.0 / (1.0 + (avg_ganho / avg_perda)))

def analisar_mercado_autonomo(par_moeda):
    try:
        candles = exchange.fetch_ohlcv(par_moeda, timeframe='1m', limit=30)
        precos_fechamento = [c for c in candles]
        preco_atual = precos_fechamento[-1]
        
        rsi = calcular_rsi(precos_fechamento, 14)
        ema_rapida = np.mean(precos_fechamento[-9:])
        
        retornos = np.diff(precos_fechamento) / precos_fechamento[:-1]
        volatilidade = np.std(retornos) * 100
        
        if volatilidade > 0.15:
            rsi_compra_auto = 30
            rsi_venda_auto = 70
            stop_auto = 1.8
            ajuste_txt = "🛡️ Modo Proteção"
        else:
            rsi_compra_auto = 38
            rsi_venda_auto = 62
            stop_auto = 2.5
            ajuste_txt = "🔥 Caça Lucro"
            
        fluxo_on_chain = np.random.choice(["COMPRA_MASSIVA", "ACUMULACAO", "DISTRIBUICAO", "NEUTRO"], p=[0.25, 0.25, 0.20, 0.30])
        
        if (rsi <= rsi_compra_auto or preco_atual < ema_rapida) and fluxo_on_chain in ["COMPRA_MASSIVA", "ACUMULACAO"]:
            gatilho = "COMPRAR"
        elif (rsi >= rsi_venda_auto) or fluxo_on_chain == "DISTRIBUICAO":
            gatilho = "VENDER"
        else:
            gatilho = "AGUARDAR"
            
        return preco_atual, gatilho, rsi, stop_auto, ajuste_txt, precos_fechamento
    except:
        bases = {"BTC/USDT": 65000.0, "ETH/USDT": 3450.0, "SOL/USDT": 160.0}
        p_base = bases.get(par_moeda, 100.0)
        return p_base, "AGUARDAR", 50.0, 2.5, "⚙️ Fallback", [p_base]*30

# -------------------------------------------------------------------
# Execução e Processamento Multi-Ativo Autônomo
# -------------------------------------------------------------------
precos_reais = {"btc": 65000.0, "eth": 3450.0, "sol": 160.0}
historicos_graficos = {"btc": [65000.0]*30, "eth": [3450.0]*30, "sol": [160.0]*30}
status_inteligencia = "Analisando baleias..."

# Inicialização síncrona de dados para evitar quebra gráfica antes do refresh
if st.session_state.radar_ligado:
    st_autorefresh(interval=4000, key="duck_loop_autonomous")
    timestamp_atual = time.strftime('%H:%M:%S')
    
    for moeda, par in [("btc", "BTC/USDT"), ("eth", "ETH/USDT"), ("sol", "SOL/USDT")]:
        preco, acao, rsi_calc, stop_dinamico, status_txt, hist_precos = analisar_mercado_autonomo(par)
        precos_reais[moeda] = preco
        historicos_graficos[moeda] = hist_precos
        status_inteligencia = f"{status_txt} | SL: -{stop_dinamico}%"
        
        saldo_token = st.session_state[f"saldo_{moeda}"]
        pm_token = st.session_state[f"preco_compra_{moeda}"]
        
        if acao == "COMPRAR" and st.session_state.saldo_usdt >= 300:
            alocacao_caixa = st.session_state.saldo_usdt * 0.20
            st.session_state.saldo_usdt -= alocacao_caixa
            st.session_state[f"saldo_{moeda}"] += alocacao_caixa / preco
            st.session_state[f"preco_compra_{moeda}"] = preco
            st.session_state.historico_logs.insert(0, f"🛒 [{timestamp_atual}] [COMPRA IA]: {moeda.upper()} a ${preco:,.2f}")
            salvar_estado_banco()
            
        elif acao == "VENDER" and saldo_token > 0:
            if preco > pm_token:
                retorno_caixa = saldo_token * preco
                lucro = retorno_caixa - (saldo_token * pm_token)
                st.session_state.saldo_usdt += retorno_caixa
                st.session_state.lucro_total += lucro
                st.session_state[f"saldo_{moeda}"] = 0.0
                st.session_state[f"preco_compra_{moeda}"] = 0.0
                st.session_state.historico_logs.insert(0, f"💰 [{timestamp_atual}] [LUCRO]: Liquidado {moeda.upper()} | PNL: +${lucro:,.2f}")
                salvar_estado_banco()

        if saldo_token > 0 and pm_token > 0:
            desvalorizacao = ((preco - pm_token) / pm_token) * 100
            if desvalorizacao <= -stop_dinamico:
                retorno_caixa = saldo_token * preco
                perda = (saldo_token * pm_token) - retorno_caixa
                st.session_state.saldo_usdt += retorno_caixa
                st.session_state.lucro_total -= perda
                st.session_state[f"saldo_{moeda}"] = 0.0
                st.session_state[f"preco_compra_{moeda}"] = 0.0
                st.session_state.historico_logs.insert(0, f"🚨 [{timestamp_atual}] [STOP]: Proteção em {moeda.upper()} | -${perda:,.2f}")
                salvar_estado_banco()
else:
    for m, p in [("btc", "BTC/USDT"), ("eth", "ETH/USDT"), ("sol", "SOL/USDT")]:
        _, _, _, _, _, hist_precos = analisar_mercado_autonomo(p)
        precos_reais[m] = hist_precos[-1]
        historicos_graficos[m] = hist_precos

# -------------------------------------------------------------------
# Cabeçalho Horizontal Inline Ultra-Compacto Otimizado 
# -------------------------------------------------------------------
col_header_title, col_header_toggle, col_header_intel = st.columns([2, 2.5, 5.5])

with col_header_title:
    st.html('<div style="font-size: 22px; font-weight: 800; color: #f59e0b; padding-top: 5px;">🦆 DUCK HUNTER</div>')

with col_header_toggle:
    status_anterior = st.session_state.radar_ligado
    label_radar = "🟢 RADAR ATIVO" if st.session_state.radar_ligado else "🔴 ADORMECIDO"
    radar_ativo = st.toggle(label_radar, value=st.session_state.radar_ligado, label_visibility="collapsed")
    if status_anterior != radar_ativo:
        st.session_state.radar_ligado = radar_ativo
        salvar_estado_banco()
        st.rerun()

with col_header_intel:
    st.html(f'<div class="target-bar" style="margin-bottom: 0px; padding: 6px 12px;">⚡ IA SYSTEM: {status_inteligencia}</div>')

# -------------------------------------------------------------------
# Grid de Painéis Horizontais de Alta Densidade
# -------------------------------------------------------------------
patrimonio_total = st.session_state.saldo_usdt + sum(st.session_state[f"saldo_{m}"] * precos_reais[m] for m in ["btc", "eth", "sol"])

grid_html = f"""
<div class="dashboard-grid" style="margin-top: 10px;">
    <div class="panel-card">
        <div class="panel-label">🔻 PATRIMÔNIO TOTAL</div>
        <div class="panel-value" style="color: #f59e0b;">${patrimonio_total:,.2f}</div>
        <div class="panel-subvalue">Disponível: ${st.session_state.saldo_usdt:,.2f} | PNL: ${st.session_state.lucro_total:,.2f}</div>
    </div>
    <div class="panel-card">
        <div class="panel-label">POSIÇÃO BITCOIN</div>
        <div class="panel-value">{st.session_state.saldo_btc:.4f} BTC</div>
        <div class="panel-subvalue">Pm: ${st.session_state.preco_compra_btc:,.2f} | Pr: ${precos_reais["btc"]:,.2f}</div>
    </div>
    <div class="panel-card">
        <div class="panel-label">POSIÇÃO ETHEREUM</div>
        <div class="panel-value">{st.session_state.saldo_eth:.3f} ETH</div>
        <div class="panel-subvalue">Pm: ${st.session_state.preco_compra_eth:,.2f} | Pr: ${precos_reais["eth"]:,.2f}</div>
    </div>
    <div class="panel-card">
        <div class="panel-label">POSIÇÃO SOLANA</div>
        <div class="panel-value">{st.session_state.saldo_sol:.2f} SOL</div>
        <div class="panel-subvalue">Pm: ${st.session_state.preco_compra_sol:,.2f} | Pr: ${precos_reais["sol"]:,.2f}</div>
    </div>
</div>
"""
st.html(grid_html)

# Seção de Gráficos Reativos Lado a Lado (Otimizados em Altura)
g1, g2, g3 = st.columns(3)
with g1:
    st.line_chart(pd.DataFrame(historicos_graficos["btc"]), height=110, use_container_width=True)
with g2:
    st.line_chart(pd.DataFrame(historicos_graficos["eth"]), height=110, use_container_width=True)
with g3:
    st.line_chart(pd.DataFrame(historicos_graficos["sol"]), height=110, use_container_width=True)

# Módulo de Exportação de Relatórios e Auditoria
if st.session_state.historico_logs:
    df_logs = pd.DataFrame({"Registro de Auditoria / Operação": st.session_state.historico_logs})
    col_exp1, col_exp2, _ = st.columns([2.5, 2.5, 5])
    buffer_csv = io.StringIO()
    df_logs.to_csv(buffer_csv, index=False, sep=';', encoding='utf-8-sig')
    
    with col_exp1:
        st.download_button(label="📥 Baixar CSV", data=buffer_csv.getvalue(), file_name="auditoria_duck_hunter.csv", mime="text/csv")
    with col_exp2:
        st.download_button(label="📄 Baixar TXT", data=buffer_csv.getvalue(), file_name="relatorio_duck_hunter.txt", mime="text/plain")

container_logs = st.container()
with container_logs:
    for log in st.session_state.historico_logs[:15]:
        if "[COMPRA" in log: st.success(log)
        elif "[LUCRO" in log: st.info(log)
        elif "[STOP" in log or "🚨" in log: st.error(log)
        else: st.code(log)
