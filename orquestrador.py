import os
import time
import streamlit as st
from google import generativeai as gemini
from groq import Groq
from openai import OpenAI

class OrquestradorMaster:
    def __init__(self):
        self.gemini_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        self.groq_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
        self.openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
        self.openrouter_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
        
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None
        self.openai_client = OpenAI(api_key=self.openai_key) if self.openai_key else None
        self.openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.openrouter_key) if self.openrouter_key else None
        if self.gemini_key: gemini.configure(api_key=self.gemini_key)

    def executar_consenso_hidra(self, questao_usuario: str, dados_da_internet: str) -> str:
        prompt = f"Usuário: {questao_usuario}\nContexto: {dados_da_internet}\nResponda como AETHER-HYDRA (IA de Elite):"
        
        # Tentativa Groq
        if self.groq_client:
            try: return self.groq_client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile").choices[0].message.content
            except: pass
        # Tentativa Gemini
        if self.gemini_key:
            try: return gemini.GenerativeModel("gemini-2.0-flash").generate_content(prompt).text
            except: pass
        # Tentativa OpenAI
        if self.openai_client:
            try: return self.openai_client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="gpt-4o-mini").choices[0].message.content
            except: pass
            
        return "Sistemas sobrecarregados. A Hidra está em reinicialização."
