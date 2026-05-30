import streamlit as st
import ccxt
from orquestrador import OrquestradorMaster

def main():
    st.title("AETHER-HYDRA: QUANTUM SENTINEL")
    hydra = OrquestradorMaster()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        comando = st.text_input("Comando de Execução (Ex: Analisar BTC):")
    
    if st.button("DISPARAR HIDRA"):
        with st.spinner("Analisando mercado via consenso quádruplo..."):
            # Exemplo de lógica de mercado (CCXT)
            exchange = ccxt.kucoin()
            ticker = exchange.fetch_ticker('BTC/USDT')
            market_data = f"BTC: {ticker['last']}"
            
            # Aqui a Hidra decide
            resposta = hydra.executar_consenso_hidra(comando, market_data)
            st.write(resposta)

if __name__ == "__main__":
    main()
