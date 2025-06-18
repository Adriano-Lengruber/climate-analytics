"""
Teste simples da página de boas-vindas
"""
import streamlit as st

def show_welcome_page() -> bool:
    """Função de teste para a página de boas-vindas."""
    st.title("🌍 Bem-vindo ao Climate Analytics")
    
    st.markdown("""
    ## Sistema de Monitoramento Climático
    
    Para usar esta aplicação, você precisa configurar suas chaves de API:
    
    ### APIs Necessárias:
    
    1. **OpenWeatherMap** - Para dados meteorológicos
       - Acesse: https://openweathermap.org/api
       - Crie uma conta gratuita
       - Obtenha sua chave de API
    
    2. **AirVisual** - Para dados de qualidade do ar
       - Acesse: https://www.airvisual.com/api
       - Crie uma conta gratuita
       - Obtenha sua chave de API
    
    ### Como configurar:
    
    1. Crie um arquivo `.env` na raiz do projeto
    2. Adicione suas chaves:
    ```
    OPENWEATHER_API_KEY=sua_chave_openweather
    AIRVISUAL_API_KEY=sua_chave_airvisual
    ```
    3. Reinicie a aplicação
    """)
    
    # Formulário simples para testar
    with st.form("api_config"):
        st.subheader("Configurar APIs")
        
        openweather_key = st.text_input("Chave OpenWeatherMap:", type="password")
        airvisual_key = st.text_input("Chave AirVisual:", type="password")
        
        if st.form_submit_button("Salvar"):
            if openweather_key and airvisual_key:
                # Salvar no arquivo .env
                try:
                    with open('.env', 'w') as f:
                        f.write(f"OPENWEATHER_API_KEY={openweather_key}\n")
                        f.write(f"AIRVISUAL_API_KEY={airvisual_key}\n")
                    
                    st.success("✅ Configurações salvas! Reinicie a aplicação.")
                    return True
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.error("Por favor, preencha ambas as chaves.")
    
    return False

if __name__ == "__main__":
    show_welcome_page()
