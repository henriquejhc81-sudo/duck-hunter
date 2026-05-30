import os
import streamlit as st
from google import generativeai as gemini
from groq import Groq
from openai import OpenAI

class OrquestradorMaster:
    def __init__(self):
        # O Streamlit Cloud buscará essas chaves nos "Secrets" do painel
        self.gemini_key = st.secrets.get("GEMINI_API_KEY")
        self.groq_key = st.secrets.get("GROQ_API_KEY")
        self.openai_key = st.secrets.get("OPENAI_API_KEY")
        
        if self.gemini_key: gemini.configure(api_key=self.gemini_key)
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None

    def executar_consenso_hidra(self, questao: str, dados: str) -> str:
        prompt = f"Usuário: {questao}\nDados: {dados}\nResponda como AETHER-HYDRA:"
        if self.groq_client:
            return self.groq_client.chat.completions.create(
                messages=[{"role":"user","content":prompt}], 
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content
        return "Sistemas sobrecarregados."
