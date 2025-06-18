"""
Página de boas-vindas limpa e funcional para o Climate Analytics.
Interface moderna sem problemas de renderização.
"""
import streamlit as st
import requests
import os

def show_welcome_page() -> bool:
    """Página de boas-vindas moderna e funcional."""
    
    # CSS limpo e eficiente
    st.markdown("""
    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            opacity: 0.95;
            margin: 0;
        }
        
        .feature-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin: 0.5rem 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .api-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
            margin: 1rem 0;
        }
        
        .success-box {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
        }
        
        .info-box {
            background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🌍 Climate Analytics</h1>
        <p class="hero-subtitle">Sua plataforma inteligente para monitoramento climático e qualidade do ar</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Funcionalidades em colunas
    st.markdown("### ✨ Funcionalidades Principais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">📊</div>
            <h4>Dashboard Inteligente</h4>
            <p>Visualize dados climáticos em tempo real</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">🚨</div>
            <h4>Alertas Inteligentes</h4>
            <p>Notificações sobre condições críticas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">🤖</div>
            <h4>Previsões com IA</h4>
            <p>Machine learning para previsões precisas</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">📈</div>
            <h4>Análise Avançada</h4>
            <p>Correlações e tendências históricas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">💨</div>
            <h4>Qualidade do Ar</h4>
            <p>Monitoramento completo de poluentes</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">📧</div>
            <h4>Relatórios Automáticos</h4>
            <p>Geração automática de relatórios</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Separador
    st.markdown("---")
    
    # Seção de configuração
    st.markdown("## 🚀 Vamos Começar!")
    st.markdown("Configure suas credenciais de API **gratuitamente** e comece a usar em minutos")
    
    # Verificar se já há credenciais
    if _check_existing_credentials():
        st.markdown("""
        <div class="success-box">
            <h3>🎉 Credenciais Configuradas!</h3>
            <p>Suas credenciais estão prontas. Você pode acessar o dashboard agora!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🌍 **Acessar Dashboard**", type="primary", use_container_width=True):
                return True
        
        with col2:
            if st.button("🔄 Reconfigurar", use_container_width=True):
                _clear_credentials()
                st.rerun()
        
        with col3:
            if st.button("🧪 Testar APIs", use_container_width=True):
                _test_all_connections()
        
        return True
    
    # Informações sobre as APIs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="api-card">
            <h4>🌤️ OpenWeatherMap</h4>
            <p><strong>Dados meteorológicos globais</strong></p>
            <ul>
                <li>✅ 1.000.000 consultas/mês GRÁTIS</li>
                <li>✅ 200.000+ cidades</li>
                <li>✅ Previsões de 5 dias</li>
                <li>✅ Cobertura mundial</li>
            </ul>
            <p><a href="https://openweathermap.org/api" target="_blank">📎 Criar conta gratuita</a></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="api-card">
            <h4>💨 AirVisual</h4>
            <p><strong>Qualidade do ar em tempo real</strong></p>
            <ul>
                <li>✅ 10.000 consultas/mês GRÁTIS</li>
                <li>✅ 10.000+ estações</li>
                <li>✅ Índices AQI em tempo real</li>
                <li>✅ Histórico de poluentes</li>
            </ul>
            <p><a href="https://www.airvisual.com/api" target="_blank">📎 Solicitar chave gratuita</a></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Formulário de credenciais
    st.markdown("### 🔑 Configure Suas Credenciais")
    
    st.markdown("""
    <div class="info-box">
        <p><strong>📋 Instruções:</strong></p>
        <p>1. Clique nos links acima para criar suas contas gratuitas</p>
        <p>2. Copie suas chaves de API e cole nos campos abaixo</p>
        <p>3. Clique em "Salvar e Continuar" para acessar o dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulário
    with st.form("api_credentials", clear_on_submit=False):
        st.subheader("🌤️ OpenWeatherMap")
        openweather_key = st.text_input(
            "Sua chave OpenWeatherMap:",
            type="password",
            placeholder="Cole sua chave da API aqui...",
            help="Você encontra sua chave em 'My API Keys' após fazer login"
        )
        
        st.subheader("💨 AirVisual")
        airvisual_key = st.text_input(
            "Sua chave AirVisual:",
            type="password", 
            placeholder="Cole sua chave da API aqui...",
            help="Você receberá a chave por email após solicitação"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit_button = st.form_submit_button(
                "💾 **Salvar e Continuar**", 
                type="primary", 
                use_container_width=True
            )
        
        with col2:
            test_button = st.form_submit_button(
                "🧪 Testar Apenas", 
                use_container_width=True
            )
    
    # Processar formulário
    if submit_button:
        if openweather_key and airvisual_key:
            with st.spinner("🔍 Validando suas credenciais..."):
                weather_valid, weather_msg = _test_openweather_api(openweather_key)
                air_valid, air_msg = _test_airvisual_api(airvisual_key)
            
            if weather_valid and air_valid:
                if _save_credentials_securely(openweather_key, airvisual_key):
                    st.success("🎉 **Credenciais salvas com sucesso!** Redirecionando...")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar credenciais. Tente novamente.")
            else:
                if not weather_valid:
                    st.error(f"❌ **OpenWeatherMap:** {weather_msg}")
                if not air_valid:
                    st.error(f"❌ **AirVisual:** {air_msg}")
        else:
            st.warning("⚠️ **Por favor, preencha ambas as chaves de API para continuar.**")
    
    elif test_button:
        if openweather_key or airvisual_key:
            st.info("🧪 **Testando suas credenciais...**")
            
            if openweather_key:
                with st.spinner("Testando OpenWeatherMap..."):
                    valid, msg = _test_openweather_api(openweather_key)
                    if valid:
                        st.success(f"✅ **OpenWeatherMap:** {msg}")
                    else:
                        st.error(f"❌ **OpenWeatherMap:** {msg}")
            
            if airvisual_key:
                with st.spinner("Testando AirVisual..."):
                    valid, msg = _test_airvisual_api(airvisual_key)
                    if valid:
                        st.success(f"✅ **AirVisual:** {msg}")
                    else:
                        st.error(f"❌ **AirVisual:** {msg}")
        else:
            st.warning("⚠️ **Insira pelo menos uma chave para testar.**")
    
    return False


def _check_existing_credentials() -> bool:
    """Verifica se já existem credenciais salvas."""
    if os.path.exists('.env'):
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                has_openweather = 'OPENWEATHER_API_KEY=' in content and len(content.split('OPENWEATHER_API_KEY=')[1].split('\n')[0].strip()) > 10
                has_airvisual = 'AIRVISUAL_API_KEY=' in content and len(content.split('AIRVISUAL_API_KEY=')[1].split('\n')[0].strip()) > 10
                return has_openweather and has_airvisual
        except:
            return False
    return False


def _save_credentials_securely(openweather_key: str, airvisual_key: str) -> bool:
    """Salva as credenciais de forma segura no arquivo .env."""
    try:
        env_content = f"""# Climate Analytics - Credenciais de API
# Gerado automaticamente pela interface de configuração
OPENWEATHER_API_KEY={openweather_key}
AIRVISUAL_API_KEY={airvisual_key}
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        # Salvar também na sessão para uso imediato
        st.session_state.openweather_api_key = openweather_key
        st.session_state.airvisual_api_key = airvisual_key
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False


def _test_openweather_api(api_key: str) -> tuple:
    """Testa a chave da API OpenWeatherMap."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return True, "Conexão estabelecida com sucesso!"
        elif response.status_code == 401:
            return False, "Chave de API inválida ou expirada"
        elif response.status_code == 429:
            return False, "Limite de chamadas excedido"
        else:
            return False, f"Erro de conexão (código: {response.status_code})"
    except Exception as e:
        return False, f"Erro de rede: {str(e)}"


def _test_airvisual_api(api_key: str) -> tuple:
    """Testa a chave da API AirVisual."""
    try:
        url = f"http://api.airvisual.com/v2/countries?key={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return True, "Conexão estabelecida com sucesso!"
        elif response.status_code == 401:
            return False, "Chave de API inválida ou expirada"
        elif response.status_code == 403:
            return False, "Acesso negado - verifique sua chave"
        elif response.status_code == 429:
            return False, "Limite de chamadas excedido"
        else:
            return False, f"Erro de conexão (código: {response.status_code})"
    except Exception as e:
        return False, f"Erro de rede: {str(e)}"


def _clear_credentials():
    """Limpa as credenciais salvas."""
    try:
        if os.path.exists('.env'):
            os.remove('.env')
        
        if 'openweather_api_key' in st.session_state:
            del st.session_state.openweather_api_key
        if 'airvisual_api_key' in st.session_state:
            del st.session_state.airvisual_api_key
            
    except Exception as e:
        st.error(f"Erro ao limpar credenciais: {e}")


def _test_all_connections():
    """Testa todas as conexões configuradas."""
    if _check_existing_credentials():
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extrair chaves
            openweather_key = ""
            airvisual_key = ""
            
            for line in content.split('\n'):
                if line.startswith('OPENWEATHER_API_KEY='):
                    openweather_key = line.split('=')[1].strip()
                elif line.startswith('AIRVISUAL_API_KEY='):
                    airvisual_key = line.split('=')[1].strip()
            
            st.info("🧪 **Testando conexões salvas...**")
            
            if openweather_key:
                with st.spinner("Testando OpenWeatherMap..."):
                    valid, msg = _test_openweather_api(openweather_key)
                    if valid:
                        st.success(f"✅ **OpenWeatherMap:** {msg}")
                    else:
                        st.error(f"❌ **OpenWeatherMap:** {msg}")
            
            if airvisual_key:
                with st.spinner("Testando AirVisual..."):
                    valid, msg = _test_airvisual_api(airvisual_key)
                    if valid:
                        st.success(f"✅ **AirVisual:** {msg}")
                    else:
                        st.error(f"❌ **AirVisual:** {msg}")
                        
        except Exception as e:
            st.error(f"Erro ao testar conexões: {e}")


if __name__ == "__main__":
    show_welcome_page()
