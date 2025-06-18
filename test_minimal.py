"""
Versão mínima de teste para identificar o problema do loop.
"""
import streamlit as st
import os

st.set_page_config(
    page_title="Climate Analytics - Teste",
    page_icon="🌍",
    layout="wide"
)

def main():
    st.title("🔧 Teste de Loop - Climate Analytics")
    
    # Verificar credenciais
    has_credentials = False
    if os.path.exists('.env'):
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                has_openweather = 'OPENWEATHER_API_KEY=' in content
                has_airvisual = 'AIRVISUAL_API_KEY=' in content
                has_credentials = has_openweather and has_airvisual
        except Exception as e:
            st.error(f"Erro ao verificar credenciais: {e}")
            has_credentials = False
    
    # Mostrar status
    st.write(f"**Arquivo .env existe:** {os.path.exists('.env')}")
    st.write(f"**Tem credenciais:** {has_credentials}")
    
    if has_credentials:
        st.success("✅ Credenciais encontradas! Dashboard funcionando.")
        st.write("Se você está vendo esta mensagem sem loop infinito, o problema foi resolvido.")
    else:
        st.warning("⚠️ Credenciais não encontradas.")
        st.write("Configure suas credenciais de API:")
        
        with st.form("credentials_form"):
            openweather_key = st.text_input("OpenWeather API Key", type="password")
            airvisual_key = st.text_input("AirVisual API Key", type="password")
            
            if st.form_submit_button("Salvar Credenciais"):
                if openweather_key and airvisual_key:
                    try:
                        env_content = f"""OPENWEATHER_API_KEY={openweather_key}
AIRVISUAL_API_KEY={airvisual_key}
"""
                        with open('.env', 'w', encoding='utf-8') as f:
                            f.write(env_content)
                        
                        st.success("✅ Credenciais salvas! Recarregue a página.")
                        
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")
                else:
                    st.error("Por favor, preencha ambas as chaves.")

if __name__ == "__main__":
    main()
