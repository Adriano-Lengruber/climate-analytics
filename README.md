# 🌍 Climate & Air Quality Analytics

Um sistema avançado de análise de dados sobre **mudanças climáticas e qualidade do ar** com integração de IA, APIs meteorológicas e dashboard interativo.

## 🎯 Objetivo

Desenvolver uma plataforma completa para:
- Monitorar dados meteorológicos e de qualidade do ar em tempo real
- Analisar tendências climáticas históricas
- Fazer previsões usando Machine Learning
- Alertar sobre condições críticas de qualidade do ar
- Visualizar dados através de dashboard interativo

## 🚀 Funcionalidades

### 📊 Análise de Dados
- Coleta automática de dados via APIs (OpenWeatherMap, AirVisual)
- Análise exploratória de dados históricos
- Identificação de padrões e tendências climáticas

### 🤖 Inteligência Artificial
- Modelos de ML para previsão de qualidade do ar
- Algoritmos de detecção de anomalias climáticas
- Sistema de alertas inteligentes

### 📈 Dashboard Interativo
- Interface web responsiva com Streamlit
- Mapas interativos com dados geoespaciais
- Gráficos dinâmicos e relatórios personalizáveis

## 🛠️ Tecnologias

- **Python**: Linguagem principal
- **Streamlit**: Dashboard e interface web
- **Pandas/NumPy**: Manipulação e análise de dados
- **Scikit-learn/TensorFlow**: Machine Learning
- **Plotly/Folium**: Visualizações interativas
- **APIs**: OpenWeatherMap, AirVisual, NASA APIs

## 🏗️ Estrutura do Projeto

```
climate-analytics/
├── data/                   # Dados coletados e processados
├── src/                    # Código fonte principal
│   ├── api/               # Integrações com APIs
│   ├── models/            # Modelos de ML
│   ├── analysis/          # Scripts de análise
│   └── dashboard/         # Interface Streamlit
├── notebooks/             # Jupyter notebooks para exploração
├── tests/                 # Testes automatizados
└── config/               # Configurações e credenciais
```

## 🚀 Como Executar

### Configuração Rápida (Dados de Demonstração)

1. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Gerar dados de demonstração**:
   ```bash
   python generate_sample_data.py
   ```

3. **Executar o dashboard**:
   ```bash
   streamlit run src/dashboard/app.py
   ```

4. **Abrir no navegador**: http://localhost:8501

### Configuração Completa (APIs Reais)

1. **Configurar variáveis de ambiente**:
   - Copie `.env.example` para `.env`
   - Adicione suas chaves de API reais

2. **Executar coleta de dados reais**:
   ```bash
   python data_collector.py
   ```

3. **Explorar análises no Jupyter**:
   ```bash
   jupyter notebook notebooks/climate_analysis.ipynb
   ```

### Tarefas Disponíveis

Use `Ctrl+Shift+P` > "Run Task" para executar:
- 🌍 **Run Climate Analytics Dashboard**
- 📊 **Collect Climate Data** 
- 📓 **Open Jupyter Notebook**
- 🔧 **Install Dependencies**

## 📊 Fontes de Dados

- **OpenWeatherMap**: Dados meteorológicos globais
- **AirVisual**: Índices de qualidade do ar
- **NASA**: Dados de satélites climáticos
- **NOAA**: Dados históricos de clima

## 🔑 APIs Necessárias

Para utilizar o projeto, você precisará obter chaves gratuitas de:
1. [OpenWeatherMap](https://openweathermap.org/api)
2. [AirVisual](https://www.airvisual.com/api)

## 📈 Impacto Esperado

Este projeto visa contribuir para:
- Conscientização sobre mudanças climáticas
- Monitoramento da qualidade do ar urbano
- Tomada de decisões baseada em dados
- Educação ambiental através de visualizações

## 🤝 Contribuições

Contribuições são bem-vindas! Este é um projeto de impacto social focado em questões ambientais críticas.

## 📄 Licença

MIT License - Sinta-se livre para usar e modificar.

---

**Desenvolvido com 💚 para um futuro mais sustentável**
