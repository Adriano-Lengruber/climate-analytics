"""
Página de boas-vindas moderna e intuitiva para o Climate Analytics.
Interface visual completa sem necessidade de conhecimento técnico.
"""
import streamlit as st
import requests
import os

def show_welcome_page() -> bool:
    """Página de boas-vindas moderna e funcional."""
    
    # CSS avançado para interface moderna
    st.markdown("""
    <style>
        /* Reset e configurações globais */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Header principal com gradiente animado */
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 400% 400%;
            animation: gradientShift 8s ease infinite;
            color: white;
            padding: 4rem 2rem;
            border-radius: 25px;
            text-align: center;
            margin-bottom: 3rem;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .hero-section::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        @keyframes float {
            0%, 100% { transform: translate(-50%, -50%) rotate(0deg); }
            50% { transform: translate(-50%, -60%) rotate(180deg); }
        }
        
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }
        
        .hero-subtitle {
            font-size: 1.5rem;
            opacity: 0.95;
            margin: 0;
            position: relative;
            z-index: 1;
        }
        
        /* Cards de funcionalidades */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }
        
        .feature-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 20px;
            border: 2px solid transparent;
            background-clip: padding-box;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
            border-radius: 20px 20px 0 0;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
            border-color: #667eea;
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
        }
        
        .feature-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        
        .feature-description {
            color: #6c757d;
            line-height: 1.6;
        }
        
        /* Seção de configuração */
        .config-section {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            padding: 3rem;
            border-radius: 25px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.1);
            margin: 3rem 0;
            border: 2px solid #e9ecef;
        }
        
        .config-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        
        .config-subtitle {
            text-align: center;
            color: #6c757d;
            font-size: 1.2rem;
            margin-bottom: 3rem;
        }
        
        /* Cards de API */
        .api-card {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin: 2rem 0;
            border-left: 6px solid #667eea;
            transition: all 0.3s ease;
        }
        
        .api-card:hover {
            transform: translateX(10px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
        }
        
        .api-header {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .api-icon {
            font-size: 2.5rem;
            margin-right: 1rem;
        }
        
        .api-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #2c3e50;
            margin: 0;
        }
        
        .api-description {
            color: #6c757d;
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }
        
        .benefits-list {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
        }
        
        .benefits-list ul {
            margin: 0;
            padding-left: 1.5rem;
        }
        
        .benefits-list li {
            color: #495057;
            margin: 0.5rem 0;
        }
        
        /* Formulário moderno */
        .form-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem;
            border-radius: 25px;
            margin: 3rem 0;
            color: white;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        }
        
        .form-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        /* Botões modernos */
        .stButton > button {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 15px;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(40, 167, 69, 0.4);
            background: linear-gradient(135deg, #218838 0%, #1abc9c 100%);
        }
        
        /* Alertas modernos */
        .success-alert {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            font-weight: 600;
            box-shadow: 0 10px 30px rgba(40, 167, 69, 0.3);
            animation: slideInFromTop 0.5s ease;
        }
        
        .error-alert {
            background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            font-weight: 600;
            box-shadow: 0 10px 30px rgba(220, 53, 69, 0.3);
        }
        
        @keyframes slideInFromTop {
            0% {
                transform: translateY(-20px);
                opacity: 0;
            }
            100% {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.5rem;
            }
            
            .hero-subtitle {
                font-size: 1.2rem;
            }
            
            .config-section {
                padding: 2rem;
                margin: 2rem 0;
            }
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
      # Grid de funcionalidades
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin: 10px 0;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">📊</div>
            <h3 style="color: #2c3e50; margin: 10px 0;">Dashboard Inteligente</h3>
            <p style="color: #6c757d; font-size: 0.9rem;">Visualize dados climáticos em tempo real com gráficos interativos</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin: 10px 0;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">🚨</div>
            <h3 style="color: #2c3e50; margin: 10px 0;">Alertas Inteligentes</h3>
            <p style="color: #6c757d; font-size: 0.9rem;">Notificações automáticas sobre condições críticas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin: 10px 0;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">🤖</div>
            <h3 style="color: #2c3e50; margin: 10px 0;">Previsões com IA</h3>
            <p style="color: #6c757d; font-size: 0.9rem;">Algoritmos avançados de machine learning</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin: 10px 0;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">�</div>
            <h3 style="color: #2c3e50; margin: 10px 0;">Análise Avançada</h3>
            <p style="color: #6c757d; font-size: 0.9rem;">Correlações e tendências históricas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin: 10px 0;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">�</div>
            <h3 style="color: #2c3e50; margin: 10px 0;">Qualidade do Ar</h3>
            <p style="color: #6c757d; font-size: 0.9rem;">Monitoramento completo de poluentes</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin: 10px 0;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">📧</div>
            <h3 style="color: #2c3e50; margin: 10px 0;">Relatórios Automáticos</h3>
            <p style="color: #6c757d; font-size: 0.9rem;">Geração automática de relatórios</p>
        </div>
        """, unsafe_allow_html=True)
      # Seção de configuração
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h2 style="color: #2c3e50; font-size: 2.5rem; margin-bottom: 10px;">🚀 Vamos Começar!</h2>
        <p style="color: #6c757d; font-size: 1.2rem;">Configure suas credenciais de API gratuitamente e comece a usar em minutos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Informações sobre as APIs - Visual e não técnico
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 5px solid #667eea;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 2.5rem; margin-right: 15px;">🌤️</span>
                <h3 style="color: #2c3e50; margin: 0;">OpenWeatherMap</h3>
            </div>
            <p style="color: #6c757d; margin-bottom: 15px;">
                Dados meteorológicos globais em tempo real, incluindo temperatura, umidade, 
                pressão atmosférica e previsões detalhadas.
            </p>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px;">
                <h4 style="color: #667eea; margin-bottom: 10px;">✨ Benefícios Gratuitos:</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>1.000.000 consultas por mês</li>
                    <li>Dados de 200.000+ cidades</li>
                    <li>Previsões de 5 dias</li>
                    <li>Cobertura global completa</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 5px solid #667eea;">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 2.5rem; margin-right: 15px;">💨</span>
                <h3 style="color: #2c3e50; margin: 0;">AirVisual</h3>
            </div>
            <p style="color: #6c757d; margin-bottom: 15px;">
                Informações precisas sobre qualidade do ar, poluentes atmosféricos 
                e índices de saúde ambiental.
            </p>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px;">
                <h4 style="color: #667eea; margin-bottom: 10px;">✨ Benefícios Gratuitos:</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>10.000 consultas por mês</li>
                    <li>Dados de 10.000+ estações</li>
                    <li>Índices AQI em tempo real</li>
                    <li>Histórico de poluentes</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
      
    # Formulário principal
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h2 style="color: #2c3e50; font-size: 2rem;">🔑 Configure Suas Credenciais</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar se já há configurações salvas
    api_configured = _check_existing_credentials()
    
    if api_configured:
        st.success("🎉 **Suas credenciais já estão configuradas!** O sistema está pronto para uso.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🌍 **Acessar Dashboard**", type="primary", use_container_width=True):
                return True
        
        with col2:
            if st.button("🔄 Reconfigurar APIs", use_container_width=True):
                _clear_credentials()
                st.rerun()
        
        with col3:
            if st.button("🧪 Testar Conexões", use_container_width=True):
                _test_all_connections()
        
        return True
    
    # Formulário de configuração
    st.info("📋 **Preencha os campos abaixo para começar a usar o Climate Analytics**")
    
    with st.form("api_credentials", clear_on_submit=False):
        
        # OpenWeatherMap
        st.markdown("### 🌤️ OpenWeatherMap")
        st.markdown("**📝 Passo 1:** [Clique aqui para criar sua conta gratuita](https://openweathermap.org/api)")
        st.markdown("**📝 Passo 2:** Após confirmar seu email, copie sua chave de API e cole abaixo:")
        
        openweather_key = st.text_input(
            "Sua chave OpenWeatherMap:",
            type="password",
            placeholder="Cole sua chave aqui...",
            help="Encontre sua chave em 'My API Keys' no site do OpenWeatherMap"
        )
        
        st.markdown("---")
        
        # AirVisual
        st.markdown("### 💨 AirVisual")
        st.markdown("**📝 Passo 1:** [Clique aqui para solicitar sua chave gratuita](https://www.airvisual.com/api)")
        st.markdown("**📝 Passo 2:** Após aprovação por email, copie sua chave e cole abaixo:")
        
        airvisual_key = st.text_input(
            "Sua chave AirVisual:",
            type="password",
            placeholder="Cole sua chave aqui...",
            help="Você receberá a chave por email após solicitar no site do AirVisual"
        )
        
        st.markdown("---")
        
        # Botões do formulário
        col1, col2 = st.columns(2)
        
        with col1:
            submit_button = st.form_submit_button("💾 **Salvar e Acessar Dashboard**", type="primary", use_container_width=True)
        
        with col2:
            test_button = st.form_submit_button("🧪 **Testar Credenciais**", use_container_width=True)
        
        # Processamento do formulário
        if submit_button:
            if openweather_key and airvisual_key:
                # Testar as chaves primeiro
                with st.spinner("🔍 Validando suas credenciais..."):
                    weather_valid, weather_msg = _test_openweather_api(openweather_key)
                    air_valid, air_msg = _test_airvisual_api(airvisual_key)
                
                if weather_valid and air_valid:
                    # Salvar as credenciais
                    success = _save_credentials_securely(openweather_key, airvisual_key)
                    
                    if success:
                        st.markdown("""
                        <div class="success-alert">
                            🎉 Credenciais salvas com sucesso! Redirecionando para o dashboard...
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Pequena pausa para mostrar a mensagem
                        import time
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.markdown("""
                        <div class="error-alert">
                            ❌ Erro ao salvar credenciais. Tente novamente.
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Mostrar erros específicos
                    if not weather_valid:
                        st.markdown(f"""
                        <div class="error-alert">
                            ❌ OpenWeatherMap: {weather_msg}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if not air_valid:
                        st.markdown(f"""
                        <div class="error-alert">
                            ❌ AirVisual: {air_msg}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="error-alert">
                    ⚠️ Por favor, preencha ambas as chaves de API para continuar.
                </div>
                """, unsafe_allow_html=True)
        
        elif test_button:
            if openweather_key or airvisual_key:
                st.markdown("### 🧪 Resultados dos Testes:")
                
                if openweather_key:
                    with st.spinner("Testando OpenWeatherMap..."):
                        valid, msg = _test_openweather_api(openweather_key)
                        if valid:
                            st.success(f"✅ OpenWeatherMap: {msg}")
                        else:
                            st.error(f"❌ OpenWeatherMap: {msg}")
                
                if airvisual_key:
                    with st.spinner("Testando AirVisual..."):
                        valid, msg = _test_airvisual_api(airvisual_key)
                        if valid:
                            st.success(f"✅ AirVisual: {msg}")
                        else:
                            st.error(f"❌ AirVisual: {msg}")
            else:                st.warning("⚠️ Insira pelo menos uma chave para testar.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Se chegou até aqui sem credenciais configuradas, continua mostrando a página
    return False  # Retorna False para continuar mostrando a página de boas-vindas


def _check_existing_credentials() -> bool:
    """Verifica se já existem credenciais salvas."""
    env_file = os.path.join('.env')
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
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
            
            st.markdown("### 🧪 Testando Conexões:")
            
            if openweather_key:
                with st.spinner("Testando OpenWeatherMap..."):
                    valid, msg = _test_openweather_api(openweather_key)
                    if valid:
                        st.success(f"✅ OpenWeatherMap: {msg}")
                    else:
                        st.error(f"❌ OpenWeatherMap: {msg}")
            
            if airvisual_key:
                with st.spinner("Testando AirVisual..."):
                    valid, msg = _test_airvisual_api(airvisual_key)
                    if valid:
                        st.success(f"✅ AirVisual: {msg}")
                    else:
                        st.error(f"❌ AirVisual: {msg}")
                        
        except Exception as e:
            st.error(f"Erro ao testar conexões: {e}")


if __name__ == "__main__":
    show_welcome_page()
