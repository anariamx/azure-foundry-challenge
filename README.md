# SmartFinance – Agente Financeiro Autônomo

🧠 **Visão Geral**

O SmartFinance é um agente de IA integrado ao Azure AI Foundry capaz de:

- Registrar despesas e receitas
- Calcular gastos por categoria
- Buscar transações armazenadas no banco
- Organizar histórico financeiro do usuário
- Realizar consultas a partir de linguagem natural

O diferencial deste projeto é a arquitetura moderna usando um MCP Server dentro do Azure API Management que expõe as Azure Functions como ferramentas para o agente executar ações reais no backend.

---

🎯 **Objetivo**

Criar um agente inteligente para gestão de finanças pessoais com:

- ✔ Integração com banco de dados
- ✔ Funções que executam ações reais
- ✔ Busca inteligente com Azure AI Search
- ✔ Conversa natural utilizando IA

---

⚙️ **Arquitetura da Solução**

Usuário → Azure AI Foundry Agent → MCP Server (APIM)  
→ Azure Functions → Azure SQL Database → Azure AI Search

**Componentes utilizados**

| Serviço | Função |
| --- | --- |
| Azure AI Foundry | Agente principal |
| Azure API Management | MCP Server |
| Azure Functions | Ferramentas para escrita/leitura |
| Azure SQL Database | Armazenamento |
| Azure AI Search | Busca inteligente |
| Visual Studio Code | Deploy das Functions |

---

🚀 **Funcionalidades do Agente**

- ✓ Registrar transações no banco  
    Exemplo: “Gastei 50 reais no supermercado ontem”

- ✓ Consultar transações mais recentes  
    Exemplo: “Quais foram meus gastos recentes?”

- ✓ Calcular gastos por categoria  
    Exemplo: “Quanto gastei em supermercado?”

- ✓ Criar ações MCP (tools):
    - processTransaction
    - getTransactions
    - healthCheck

---

✨ **Resultado dentro do Foundry**

**Registro de transação**  
Entrada: “Gastei 40 reais no supermercado hoje.”  
Resposta do sistema: “A despesa foi registrada com sucesso!”

**Consulta ao histórico**  
Entrada: “Quais foram minhas últimas despesas?”  
Saída de exemplo:
- Supermercado: R$40  
- Transporte: R$12

---

🧩 **Fluxo de Execução do MCP Server**

1. O agente detecta a intenção do usuário.  
2. Chama o MCP Server (APIM) configurado como ferramenta.  
3. APIM aciona a Azure Function correspondente.  
4. A Function grava/consulta dados no Azure SQL e/ou atualiza índices do Azure AI Search.  
5. O agente retorna a resposta ao usuário.

---

🛠 **Configuração das Ferramentas**

1) **Azure Functions**  
- Deploy no Function App: `mcp-smartfinance`  
- Tools MCP:
    - `getTransactions`
    - `processTransaction`
    - `healthCheck`  

Exemplo de função (Python/Azure Functions):

```python
@app.route(route="processTransaction", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def process_transaction(req: func.HttpRequest) -> func.HttpResponse:
        # processa payload e grava no banco
```

2) **API Management como MCP Server**  
- Importar Function App no APIM:  
    Function App → API Management → Import as API  
- Criar MCP Server:  
    API Management → MCP Servers → Create server → `mcp-sf`  
- Regras de autorização desativadas (para permitir chamadas do agente):
    - Sem subscription key
    - Sem aprovação manual

3) **Agente no Azure AI Foundry**  
- Adicionar ferramenta MCP no agente:  
    Tools → Add tool → MCP Server → `mcp-smartfinance`

---

🧪 **Exemplo real de chamada funcional**

Entrada do usuário:  
> gastei 40 reais no supermercado hoje

Execução (chamada interna):
```json
processTransaction({ "amount": 40, "category": "supermercado" })
```

Resposta ao usuário:  
> Despesa registrada com sucesso!

---

🔧 **Requisitos para rodar**

- Conta Azure ativa  
- Azure AI Foundry habilitado  
- Function App configurado (`mcp-smartfinance`)  
- API Management criado e integrado  
- Azure SQL Database para armazenamento  
- Azure AI Search com index e datasource configurados

Para conferir como recriar, confira o [passo a passo](/passos/config)

---

📚 **Referências Oficiais**

- Azure AI Foundry — [Documentação do Azure AI Studio (Foundry)](https://learn.microsoft.com/azure/ai-studio/)
- MCP / Agents — [Guia de Agents e MCP no Azure AI Studio](https://learn.microsoft.com/azure/ai-studio/agents/)
- Azure API Management — [Documentação do Azure API Management](https://learn.microsoft.com/azure/api-management/)
- Azure Function Apps — [Documentação do Azure Functions](https://learn.microsoft.com/azure/azure-functions/)
- Azure SQL — [Documentação do Azure SQL](https://learn.microsoft.com/azure/azure-sql/)
- Azure AI Search — [Documentação do Azure AI Search (Cognitive Search)](https://learn.microsoft.com/azure/search/)

---

✔️ **O que já está funcional**

- Consultas de gastos via agente  
- Registros de transações no SQL  
- AI Search indexando os dados  
- MCP Server integrado com Functions  
- Agente responde a comandos e calcula valores

📌 **Próximos passos (opcionais)**

- Criar interface web ou integração com WhatsApp  
- Criar pipeline com Power Automate  
- Automatizar despesas recorrentes  
- Incluir notificações por push / e-mail

---

🏁 **Conclusão**

Este projeto demonstra uma aplicação completa de IA generativa integrada ao Azure, com capacidade real de leitura e escrita de dados através de um MCP Server exposto via API Management, Azure Functions, SQL e Azure AI Search — permitindo automação e conversas naturais úteis para gestão financeira pessoal.
