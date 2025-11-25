# MCP — Passos de Configuração

## 1️⃣ Criar o Azure Functions (mcp-smartfinance)
Você desenvolveu os métodos no `function_app.py` e fez deploy no Azure.

Functions incluídas:
- ProcessTransaction
- GetTransactions
- AgentWebhook
- HealthCheck
- MCPMetadata

## 2️⃣ Configurar o API Management
### ✔ Criar API Management
- No menu do Function App → Gerenciamento de API
- Clique em “Criar novo serviço de API Management”.
- Nome sugerido: `mcp-smartfinance-api`

### ✔ Importar as Functions para o APIM
- No APIM: `APIs` → `+ Add API` → `Azure Function App` → selecione `mcp-smartfinance`
- Todas as Functions aparecerão como endpoints REST.

## 3️⃣ Criar o Servidor MCP dentro do API Management
- No menu lateral do APIM → `MCP Servers`
- Clique em “Criar servidor”
    - Nome: `mcp-sf`
    - Selecione todas as functions como ferramentas MCP
    - Salvar

Resultado: você receberá um endpoint do MCP server, por exemplo:
```
https://mcp-smartfinance-api.azure-api.net/mcp-sf
```
⚠️ Guarde este link — ele será usado no AI Foundry.

## 4️⃣ Conectar o Servidor MCP ao Agente no AI Foundry
- No AI Foundry → `Ferramentas` → `MCP Server`
    - Nome: `mcp-sf`
    - URL: cole o endpoint acima
    - Autenticação: `API Key`
    - Chave: (ver próximo passo)
    - Header name: `Ocp-Apim-Subscription-Key`

## 5️⃣ Obter a chave para o MCP funcionar
- No API Management → `Subscriptions` (Assinaturas)
- Use a `Built-in all-access key` → `Primary key`
- Cole essa chave no AI Foundry no campo **Chave**.

⚠️ Mantenha essa chave segura — ela dá acesso às APIs do APIM.

## 6️⃣ Ajustar o servidor MCP para NÃO exigir aprovação
Por padrão, o APIM define:
```json
"authorization": "required"
```
Isso faz o agente:
- ✅ pedir aprovação manual
- ❌ exibir o código da chamada
- ❌ travar operações sem aprovação

Para corrigir:
- Caminho no APIM:
    - `MCP Servers` → `mcp-sf` → `Tools` → selecione uma Function → editar → `Authorization: None`
- Repita para todas as functions MCP.

Depois disso:
- ✅ O agente chamará automaticamente
- ✅ Sem prompts de aprovação
- ✅ Sem expor código no chat

---

Sugestão de verificação:
- Teste o endpoint do `HealthCheck`
- Valide chamadas automáticas do agente ao atingir as functions
- Garanta que a subscription key esteja configurada corretamente no AI Foundry
