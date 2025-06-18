# 🌍 Climate & Air Quality Analytics

Um sistema avançado de análise de dados sobre **mudanças climáticas e qualidade do ar** com integração de IA, APIs meteorológicas e dashboard interativo.

## 🎯 Objetivo

Desenvolver uma plataforma completa para:
- Monitorar dados meteorológicos e de qualidade do ar em tempo real
- Analisar tendências climáticas históricas e correlações complexas
- Fazer previsões usando Machine Learning e análise estatística
- Sistema de alertas inteligentes para condições críticas
- Visualizar dados através de dashboard interativo avançado
- Gerar relatórios automáticos detalhados

## 🚀 Funcionalidades

### 📊 Análise de Dados Avançada
- Coleta automática de dados via APIs (OpenWeatherMap, AirVisual)
- Sistema de cache inteligente para otimização de performance
- Análise exploratória com correlações e clustering
- Identificação de padrões temporais e anomalias estatísticas

### � Inteligência Artificial e Análise
- **Sistema de Alertas Inteligentes**: Detecta condições críticas e anomalias
- **Análise de Correlações Avançada**: Identifica relações entre variáveis climáticas
- **Índice de Saúde Ambiental**: Métrica personalizada para qualidade ambiental
- **Clustering de Condições**: Identifica perfis de condições ambientais
- **Análise de Componentes Principais (PCA)**: Redução dimensional e insights

### 📈 Dashboard Interativo Premium
- Interface web responsiva com Streamlit
- **5 Abas Especializadas**: Dashboard Principal, Análise Climática, Qualidade do Ar, Previsões IA, Análise Avançada
- Mapas interativos com dados geoespaciais
- Gráficos dinâmicos e métricas em tempo real
- Sistema de alertas visuais integrado

### 📄 Sistema de Relatórios Automáticos
- **Relatórios Diários**: Resumos executivos automáticos
- **Relatórios Semanais**: Análises de tendências e correlações
- **Relatórios Mensais**: Análises aprofundadas com estatísticas completas
- **Múltiplos Formatos**: HTML, JSON, Markdown
- **Recomendações Inteligentes**: Sugestões baseadas nos dados

### ⚡ Automação Completa
- **Agendamento Inteligente**: Coleta automática e análises programadas
- **Sistema de Notificações**: Email e webhook para alertas críticos
- **Manutenção Automática**: Limpeza de cache e otimização do banco
- **Monitoramento Contínuo**: Verificação de alertas em tempo real

## 🛠️ Tecnologias

- **Python 3.8+**: Linguagem principal
- **Streamlit**: Dashboard e interface web interativa
- **Pandas/NumPy**: Manipulação e análise de dados
- **Scikit-learn**: Machine Learning e análise estatística
- **SciPy**: Análise estatística avançada
- **Plotly**: Visualizações interativas e responsivas
- **SQLite**: Banco de dados local otimizado
- **APIs**: OpenWeatherMap, AirVisual, NASA APIs

## 🏗️ Estrutura do Projeto

```
climate-analytics/
├── 📊 data/                     # Dados coletados e processados
├── 🔧 src/                      # Código fonte principal
│   ├── 🌐 api/                  # Integrações com APIs
│   ├── 🤖 models/               # Modelos de ML
│   ├── 🔍 analysis/             # Sistema de análises avançadas
│   │   ├── alert_system.py      # Sistema de alertas inteligentes
│   │   └── correlation_analyzer.py # Análise de correlações
│   ├── 📱 dashboard/            # Interface Streamlit
│   │   ├── app.py              # Aplicação principal
│   │   └── advanced_components.py # Componentes avançados
│   ├── 📄 reports/             # Sistema de relatórios
│   │   └── report_generator.py # Gerador automático de relatórios
│   └── ⚡ utils/               # Utilitários
│       └── cache_system.py    # Sistema de cache inteligente
├── 📓 notebooks/               # Jupyter notebooks para exploração
├── 🧪 tests/                   # Testes automatizados
├── ⚙️ config/                 # Configurações e credenciais
├── 📋 reports/                # Relatórios gerados
├── 🔄 automation.py           # Sistema de automação
├── 📊 climate_analyzer.py     # Análise automatizada
└── 📦 data_collector.py       # Coletor de dados
```

## 🚀 Como Executar

### Configuração Rápida (Dados de Demonstração)

```bash
# 1. Clone o repositório
git clone https://github.com/Adriano-Lengruber/climate-analytics.git
cd climate-analytics

# 2. Instale dependências
pip install -r requirements.txt

# 3. Gere dados de demonstração
python generate_sample_data.py

# 4. Execute o dashboard
streamlit run src/dashboard/app.py

# 5. Acesse: http://localhost:8501
```

### Configuração Completa (APIs Reais)

```bash
# 1. Configure credenciais (interativo)
python setup_credentials.py

# 2. Inicie coleta de dados
python data_collector.py

# 3. Execute análise completa
python climate_analyzer.py --all

# 4. Configure automação (opcional)
python automation.py --create-config
python automation.py start
```

### 🤖 Comandos de Análise Avançada

```bash
# Análise completa com todos os recursos
python climate_analyzer.py --all

# Apenas alertas críticos
python climate_analyzer.py --alerts

# Análise de correlações (30 dias)
python climate_analyzer.py --correlations -d 30

# Geração de relatórios
python climate_analyzer.py --reports

# Limpeza e otimização
python climate_analyzer.py --clear-cache --optimize-cache

# Análise forçada com poucos dados
python climate_analyzer.py --all --force
```

### ⚡ Sistema de Automação

```bash
# Criar configuração personalizada
python automation.py --create-config

# Iniciar sistema completo
python automation.py start

# Executar tarefas específicas
python automation.py --run-once data_collection
python automation.py --run-once daily_analysis
python automation.py --run-once alert_check

# Verificar status
python automation.py status
```

### Tarefas Disponíveis (VS Code)

- **🌍 Run Climate Analytics Dashboard**: Inicia o dashboard interativo
- **📊 Collect Climate Data**: Executa coleta de dados
- **📓 Open Jupyter Notebook**: Abre ambiente de análise
- **🔧 Install Dependencies**: Instala todas as dependências

## 🌟 Recursos Premium

### 🚨 Sistema de Alertas Inteligentes
- **Detecção Automática**: Identifica condições críticas em tempo real
- **Múltiplos Níveis**: Info, Warning, Critical, Emergency
- **Recomendações Personalizadas**: Sugestões específicas por tipo de alerta
- **Análise de Tendências**: Detecta deterioração gradual da qualidade

### 🔗 Análise de Correlações Avançada
- **Matriz de Correlação**: Visualização interativa de relações
- **Clustering Inteligente**: Identifica perfis de condições ambientais
- **PCA**: Análise de componentes principais para insights ocultos
- **Padrões Temporais**: Análise horária, semanal e de tendências

### 🌿 Índice de Saúde Ambiental (ISA)
- **Métrica Personalizada**: Combina temperatura, umidade, pressão, vento e qualidade do ar
- **Classificação Intuitiva**: Excelente, Bom, Regular, Ruim, Crítico
- **Visualização Gauge**: Interface gráfica clara e informativa
- **Componentes Detalhados**: Análise individual de cada fator

### 📊 Previsões Inteligentes
- **Baseadas em Tendências**: Análise estatística dos últimos 7 dias
- **Múltiplas Variáveis**: Temperatura, umidade e qualidade do ar
- **Visualização Temporal**: Gráficos históricos + previsões
- **Alertas Preventivos**: Avisos sobre condições futuras

### 📄 Relatórios Automáticos Premium
- **HTML Profissional**: Relatórios visuais com gráficos e estatísticas
- **Análise Estatística**: Correlações, outliers, tendências significativas
- **Recomendações IA**: Sugestões automáticas baseadas nos dados
- **Múltiplos Períodos**: Diário, semanal, mensal

## 🎯 Casos de Uso

### Para Pesquisadores
- Análise de correlações entre variáveis climáticas
- Identificação de padrões e anomalias
- Geração de relatórios científicos automáticos
- Monitoramento de tendências de longo prazo

### Para Ambientalistas
- Sistema de alertas para qualidade do ar
- Monitoramento de condições ambientais críticas
- Índice de saúde ambiental personalizado
- Relatórios para conscientização pública

### Para Tomadores de Decisão
- Dashboard executivo com métricas principais
- Alertas automáticos para condições extremas
- Relatórios mensais com recomendações
- Previsões para planejamento

### Para Desenvolvedores
- API estruturada para integração
- Sistema de cache para performance
- Arquitetura modular e extensível
- Documentação completa

## 📈 Métricas e KPIs

### Qualidade dos Dados
- **Completude**: % de dados sem valores faltantes
- **Cobertura Temporal**: Densidade de registros por período
- **Consistência**: Validação automática de valores

### Performance do Sistema
- **Cache Hit Rate**: Eficiência do sistema de cache
- **Tempo de Resposta**: Latência das análises
- **Throughput**: Registros processados por minuto

### Alertas e Insights
- **Precision**: Relevância dos alertas gerados
- **Cobertura**: % de condições críticas detectadas
- **Tempo de Detecção**: Velocidade de identificação de anomalias

## 🔧 Configuração Avançada

### Cache Inteligente
```python
# Configuração de cache personalizada
cache_config = {
    "memory_ttl": 1800,    # 30 minutos
    "disk_ttl": 7200,      # 2 horas
    "auto_cleanup": True,
    "max_memory_entries": 1000
}
```

### Sistema de Alertas
```python
# Thresholds personalizados
alert_thresholds = {
    "aqi_critical": 150,
    "temp_extreme_high": 38,
    "humidity_very_low": 15,
    "wind_extreme": 20
}
```

### Automação
```json
{
  "data_collection": {
    "frequency": "hourly",
    "locations": ["São Paulo", "Rio de Janeiro"]
  },
  "analysis": {
    "daily_reports": true,
    "alert_checks": "every_hour",
    "correlation_analysis": "weekly"
  }
}
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/Adriano-Lengruber/climate-analytics/issues)
- **Documentação**: Wiki do projeto
- **Email**: adrianolengruber@hotmail.com

## 🌟 Roadmap

### Versão 2.0 (Planejada)
- [ ] Integração com mais APIs meteorológicas
- [ ] Machine Learning para previsões avançadas
- [ ] Sistema de usuários e permissões
- [ ] API REST para integração externa
- [ ] Dashboard mobile responsivo
- [ ] Integração com IoT sensors
- [ ] Análise de imagens de satélite
- [ ] Sistema de backup automático

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!**

[![GitHub stars](https://img.shields.io/github/stars/Adriano-Lengruber/climate-analytics?style=social)](https://github.com/Adriano-Lengruber/climate-analytics/stargazers)

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
