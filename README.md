# 🤖 SmartFinance Agent

Um assistente financeiro inteligente construído no Azure AI Foundry que ajuda no gerenciamento de finanças pessoais através de análise de transações e insights financeiros.

## 🚀 Funcionalidades

- **📊 Análise de Transações**: Acessa banco de dados em tempo real
- **💰 Gestão de Gastos**: Monitora despesas por categoria
- **📈 Insights Financeiros**: Oferece dicas personalizadas
- **🔍 Pesquisa Web**: Busca informações financeiras atualizadas
- **💬 Interface Natural**: Conversa em linguagem cotidiana

## 🛠️ Arquitetura

```mermaid
graph TB
    A[Usuário] --> B[AI Foundry Agent]
    B --> C[Azure AI Search]
    B --> D[Web Search]
    C --> E[SQL Database]
    E --> F[Transações]

## 📋 Tecnologias
- Azure AI Foundry - Plataforma do agente

- Azure SQL Database - Armazenamento de transações

- Azure AI Search - Indexação e busca de dados

- Python - Azure Functions (histórico)

## Como usar
```"mostre minhas transações recentes"
"quanto gastei com alimentação?"
"qual meu saldo atual?"
"dicas para economizar dinheiro"
"melhores investimentos para 2024"
```
## 🔧 Configuração
Agent: SmartFinance
Tools:
- Azure AI Search (transactions-index)
- Web Search Preview
- Model: GPT-4.1-mini

### System Prompt:
```
Você é um assistente financeiro inteligente. Use as ferramentas disponíveis para:

📊 PARA SEUS DADOS PESSOAIS (transações, gastos, saldo):
- Use "Azure AI Search" para acessar seu banco de dados pessoal
- Isso mostra suas transações reais do SQL Database

🔍 PARA INFORMAÇÕES GERAIS (dicas, notícias, conceitos):
- Use "Web Search" para buscar informações atualizadas
- Isso busca na internet por dicas e notícias

EXEMPLOS:
"mostre minhas transações" → Azure AI Search
"quanto gastei com alimentação?" → Azure AI Search  
"dicas para economizar" → Web Search
"melhores investimentos 2024" → Web Search

Seja útil e direto nas respostas!
```

### 📊 Dados de Exemplo
O banco inclui transações realistas cobrindo:

💰 Receitas: Salários (R$ 3.500), freelances (R$ 450)

📉 Despesas:

Alimentação: mercado, ifood, restaurantes

Transporte: Uber, combustível, manutenção

Moradia: aluguel, condomínio, contas

Lazer: cinema, streaming, shopping

Saúde: farmácia, consultas, academia

📅 Período: Últimos 30 dias

🎯 Saldo: R$ 1.467,75 positivo

## 🚀 Deployment
### Azure Resources Utilizados:
- Resource Group: rg-azure-foundry
- AI Foundry Project: smartfinance
- SQL Database: finance-db em smartfinance-server
- AI Search: transactions-index
- Azure Functions: mcp-smartfinance (para integrações futuras)

### Configuração do Ambiente:
- Azure AI Foundry: Crie um novo projeto

- SQL Database: Configure com as credenciais apropriadas

- AI Search: Indexe a tabela de transações

- Agent: Configure com as tools de search e web search