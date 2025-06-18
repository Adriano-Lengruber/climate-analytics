#!/usr/bin/env python3
"""
Teste da página de boas-vindas isolada.
"""
import streamlit as st
import sys
import os

# Adicionar o path do projeto
sys.path.append('.')

from src.dashboard.welcome_simple import show_welcome_page

st.set_page_config(
    page_title="Climate Analytics - Boas-vindas",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Executar apenas a página de boas-vindas
if __name__ == "__main__":
    show_welcome_page()
