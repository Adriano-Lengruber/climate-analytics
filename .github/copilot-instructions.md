<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Instruções para GitHub Copilot - Projeto Climate Analytics

Este é um projeto Python focado em análise de dados sobre mudanças climáticas e qualidade do ar.

## Contexto do Projeto
- **Objetivo**: Sistema de monitoramento e análise de mudanças climáticas e qualidade do ar
- **Tecnologias principais**: Python, Streamlit, Machine Learning, APIs meteorológicas
- **Público-alvo**: Pesquisadores, ambientalistas, tomadores de decisão

## Diretrizes de Código

### Estrutura e Organização
- Mantenha separação clara entre coleta de dados, análise e visualização
- Use padrões de design adequados para integração com APIs
- Implemente logging apropriado para monitoramento
- Siga princípios de código limpo e documentação clara

### APIs e Dados
- Priorize APIs gratuitas e confiáveis (OpenWeatherMap, AirVisual)
- Implemente tratamento de erros robusto para chamadas de API
- Use cache local quando apropriado para reduzir chamadas
- Valide e limpe dados antes do processamento

### Machine Learning
- Use bibliotecas estabelecidas (scikit-learn, TensorFlow)
- Implemente validação cruzada e métricas de avaliação
- Documente claramente os modelos e suas limitações
- Considere interpretabilidade dos modelos para contexto ambiental

### Dashboard e Visualização
- Priorize clareza e usabilidade no Streamlit
- Use cores e layouts apropriados para dados ambientais
- Implemente responsividade para diferentes dispositivos
- Inclua tooltips e explicações para métricas complexas

### Sustentabilidade e Ética
- Otimize código para eficiência energética
- Considere impacto ambiental das decisões de design
- Mantenha transparência sobre limitações dos dados
- Priorize acessibilidade e inclusão

## Padrões Específicos
- Use type hints em Python
- Implemente testes unitários para funções críticas
- Mantenha configurações em arquivos separados
- Use variáveis de ambiente para credenciais
- Documente APIs e funções complexas com docstrings
