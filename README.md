# HelpLink Dashboard 🌟

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.38+-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

## 📋 Sobre o Projeto

**HelpLink** é uma plataforma inovadora de gestão e monitoramento de doações para instituições e ONGs, desenvolvida como parte do **Global Solution 2025 - O Futuro do Trabalho** da FIAP. O sistema oferece um dashboard interativo e inteligente que facilita a conexão entre doadores e instituições beneficentes, promovendo transparência e eficiência no processo de doações.

### 🎯 Principais Funcionalidades

- **Dashboard Interativo**: Visualização em tempo real de métricas e indicadores-chave
- **Análise Inteligente**: Sistema de IA para classificação automática do estado de conservação de itens
- **Gestão Completa**: Controle de usuários, instituições, itens e doações
- **Relatórios Visuais**: Gráficos dinâmicos e heatmaps para análise de tendências
- **Modo Demo**: Dados simulados para demonstração e testes

## 🚀 Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **Streamlit**: Framework para desenvolvimento do dashboard web
- **Pandas**: Manipulação e análise de dados
- **Plotly**: Visualizações interativas e gráficos
- **NumPy**: Computação numérica
- **Hugging Face API**: Integração com modelo de IA para classificação de imagens
- **Pillow**: Processamento de imagens

## 📦 Estrutura do Projeto
```
helplink/
│
├── .devcontainer/          # Configuração do ambiente de desenvolvimento
├── .streamlit/             # Configurações do Streamlit
│   └── secrets.toml        # Tokens e credenciais (não versionado)
├── .vscode/                # Configurações do VS Code
├── .gitignore             # Arquivos ignorados pelo Git
├── helplink_dashboard.py   # Aplicação principal
├── mock_data.py           # Dados de exemplo para testes
├── requirements.txt       # Dependências do projeto
└── README.md             # Este arquivo
```

## 🔧 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Conta no Hugging Face (para uso da IA)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd helplink
```

2. **Crie um ambiente virtual (recomendado)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as credenciais**

Crie o arquivo `.streamlit/secrets.toml` com seu token do Hugging Face:
```toml
HF_TOKEN = "seu_token_aqui"
```

> ⚠️ **Importante**: Nunca compartilhe seu token publicamente. O arquivo `secrets.toml` já está no `.gitignore`.

5. **Execute a aplicação**
```bash
streamlit run helplink_dashboard.py
```

A aplicação estará disponível em `http://localhost:8501`

## 📊 Funcionalidades Detalhadas

### Dashboard Principal

O dashboard oferece uma visão completa do sistema através de:

#### 📌 Indicadores Gerais
- Total de usuários cadastrados
- Número de instituições parceiras
- Itens disponíveis para doação
- Doações no período selecionado
- Taxa de conclusão de doações
- Média de itens por doação

#### 📈 Visualizações Analíticas

1. **Doações por Status**
   - Gráfico de barras mostrando distribuição por status (Aberta, Em Andamento, Concluída, Cancelada)
   - Gráfico de pizza para visão proporcional

2. **Evolução Temporal**
   - Linha do tempo mostrando tendências de doações
   - Identificação de picos e períodos de baixa

3. **Top Instituições**
   - Ranking das instituições que mais recebem doações
   - Visualização horizontal para fácil comparação

4. **Itens Mais Doados**
   - Categorias mais populares de doações
   - Quantidades totais por tipo de item

5. **Heatmap de Horários**
   - Identificação de horários de pico para doações
   - Análise por dia da semana e hora do dia

### 🤖 Módulo de Inteligência Artificial

O sistema integra um modelo de IA do Hugging Face (`google/vit-base-patch16-224`) para classificação automática do estado de conservação de itens:

- **BOM**: Confiança ≥ 75%
- **REGULAR**: Confiança entre 45% e 75%
- **RUIM**: Confiança < 45%

**Como usar:**
1. Navegue até a seção "IA – Análise do Estado de Conservação"
2. Faça upload de uma imagem do item (JPG, JPEG ou PNG)
3. Aguarde a análise automática
4. Visualize o resultado com a classificação e nível de confiança

### 🔍 Filtros Avançados

O sidebar oferece múltiplas opções de filtragem:

- **Período de Doações**: Selecione intervalo de datas
- **Status**: Filtre por status específicos
- **Instituição**: Visualize dados de uma instituição específica

### 📑 Dados Detalhados

Acesse tabelas completas através das abas:
- Usuários cadastrados
- Instituições parceiras
- Itens disponíveis
- Histórico de doações
- Itens por doação
- Registros de impacto

## 🎨 Interface e Design

O dashboard utiliza um tema dark moderno com:
- Paleta de cores escuras (#05070b, #111827)
- Gráficos interativos do Plotly com template dark
- Layout responsivo e organizado
- Ícones intuitivos para cada seção
- Gradientes personalizados no heatmap

## 🔐 Segurança e Privacidade

- Senhas são ocultadas na visualização de usuários
- Tokens e credenciais armazenados em arquivo separado
- Configuração para não versionamento de dados sensíveis
- Sistema de cache para otimização de performance

## 📈 Modo Demo

O sistema inclui um gerador de dados simulados completo com:
- 150 usuários fictícios
- 15 instituições realistas
- 200 itens de diversos tipos
- 300 doações com status variados
- Histórico de 90 dias de operações
- Distribuição estatística realista

Ideal para:
- Demonstrações e apresentações
- Testes de funcionalidades
- Treinamento de usuários
- Desenvolvimento e homologação

## 👥 Autores

**FIAP - Turma 2TDSPW**

- **Arthur Ramos dos Santos** - RM558798
- **Felipe Melo de Sousa** - RM556099
- **Robert Daniel da Silva Coimbra** - RM555881

## 🎓 Contexto Acadêmico

Projeto desenvolvido para o evento **Global Solution 2025 - O Futuro do Trabalho** da FIAP, explorando como a tecnologia pode transformar o trabalho solidário e facilitar a conexão entre doadores e instituições beneficentes.

## 🚀 Deploy

O projeto está preparado para deploy no Streamlit Cloud:

1. Faça fork do repositório
2. Conecte sua conta do GitHub ao Streamlit Cloud
3. Configure o token do Hugging Face nos secrets
4. Deploy automático!

## 📝 Licença

Este projeto é desenvolvido para fins educacionais como parte do programa da FIAP.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Melhorar a documentação
- Enviar pull requests

## 📧 Contato

Para dúvidas ou sugestões sobre o projeto, entre em contato através dos emails institucionais dos autores.

---

<p align="center">
  Desenvolvido com ❤️ por estudantes FIAP | Global Solution 2025
</p>