# SmartFinance — Guia Completo Passo a Passo

> Este README documenta todo o processo de criação do SmartFinance — um agente financeiro inteligente utilizando Azure AI Foundry, MCP Server (API Management), Azure SQL, Azure Functions e Azure Cognitive Search.

---

## 📌 Sumário
1. Visão geral da arquitetura  
2. Pré-requisitos  
3. Tutorial passo a passo (com prints)  
4. Prints de execução  
5. Troubleshooting  
6. Referências oficiais  

---

## 🧠 Visão Geral

O **SmartFinance** é um agente integrado com backend real, capaz de:

- Registrar e consultar gastos no banco de dados
- Calcular categorias de despesas
- Executar chamadas MCP
- Buscar em Azure AI Search

Fluxo completo:


---

## ✔️ Pré-requisitos

- Conta Azure (aqui usamos a conta trial, uma vez que a de estudante não habilitava o deploy do modelo que usamos)
- Azure AI Foundry habilitado
- Acesso ao Portal Azure
- VS Code (para deploy Functions)

---

---

# PASSO A PASSO

---

## 1️⃣ Criar Resource Group

Portal Azure → **Resource Groups → Create**

- Nome: `rg-azure-foundry`
- Região: US East 2

**Print:**
![/imagens/resourcegroup]()

---

## 2️⃣ Criar Azure SQL Database

Portal → **Azure SQL → Single database**

- Server: `smartfinance-server`
- Database: `finance-db`
- Firewall: habilitar *Allow Azure services* + *Adicionar o endereço0 de IPv4 do cliente*

**Print:**
![passos/imagens/azuresqldatabase-1.png]()
![passos/imagens/azuresqldatabase-2.png]()
![passos/imagens/azuresqldatabase-3.png]()
---

## 3️⃣ Criar Storage Account

Usado pelo Function App:

Portal → **Storage Account → Create**

**Print:**
![screenshot-03-storage]()

---

## 4️⃣ Criar Function App e publicar as funções

Portal → Function App → **Create**

- Runtime: Python
- Name: `mcp-smartfinance`

Deploy do código (`function_app.py`) via VS Code.

Funções criadas:

- `processTransaction`
- `getTransactions`
- `whatsappWebhook`
- `MCPMetadata`

**Print:**
![screenshot-04-function-app]()

---

## 5️⃣ Criar Azure Cognitive Search

Portal → Cognitive Search → Create

### Criar Index
Campos sugeridos:

- id (key)
- description
- amount
- category
- type
- date

**Print:**
![screenshot-05-search-index]()

### Criar Data Source
Tipo: `azuresql` apontando para `finance-db`.

### Criar Indexer
Relacionando datasource → index.

---

## 6️⃣ Criar API Management e importar Function App

Portal → **API Management → Create**

Depois:

API Management → **APIs → Add API → Function App**

**Print:**
![screenshot-06-apim-import]()

### Ajustes importantes da API

Desativar subscription para permitir chamadas MCP automáticas:

- API → Settings → `Subscription required = Off`

---

## 7️⃣ Criar MCP Server no APIM

API Management → **MCP Servers → Create**

- Nome: `mcp-sf`
- Selecionar todas as funções

Copiar o endpoint MCP gerado:

Exemplo:

**Print:**
![screenshot-07-apim-mcp]()

---

## 8️⃣ Criar o Agente no Azure AI Foundry

AI Foundry → **Projects → Create project**

Depois:

Project → **Agents → Create Agent**

Selecionar modelo (ex.: `gpt-4.1-mini`)

### Adicionar ferramentas ao agente:

Tools → Add tool:

- Azure AI Search → index `transactions-index`
- MCP Server → cole o endpoint do APIM

**Print:**
![screenshot-08-foundry-add-tools]()

---

---

# 🧪 Testando no Playground

Exemplo:

> “Gastei 40 reais no supermercado hoje”

Retorno:


**Print:**
![screenshot-09-test-execution]()

Consulta:

> “Quais são meus gastos recentes?”

---

---

# 🧷 Troubleshooting

### 🟥 Agent pede aprovação ou chave
- Verificar API Management → API → Subscription required = off
- Em Agent Settings desativar:
  - “Require approval”
  - “Show tool payloads”

### 🟥 Indexer falha
- Verificar tipos (usar Edm.String)
- Recriar indexer se necessário

### 🟥 Funções não conectam ao SQL
- Verificar connection string
- Firewall do SQL liberado


