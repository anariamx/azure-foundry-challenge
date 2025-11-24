from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

class FinanceClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def add_transaction(self, amount: float, description: str, type: str, category: str = "general", merchant_name: str = None):
        """Adiciona uma transação financeira"""
        data = {
            "amount": amount,
            "description": description,
            "type": type,
            "category": category
        }
        
        if merchant_name:
            data["merchant_name"] = merchant_name
        
        try:
            response = requests.post(f"{self.base_url}/api/transactions", json=data, timeout=10)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": f"API call failed: {str(e)}"}
    
    def get_transactions(self):
        """Obtém todas as transações"""
        try:
            response = requests.get(f"{self.base_url}/api/transactions", timeout=10)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": f"API call failed: {str(e)}"}
    
    def get_balance(self):
        """Calcula o saldo atual"""
        try:
            transactions_data = self.get_transactions()
            if transactions_data["status"] == "success":
                balance = 0
                for transaction in transactions_data["transactions"]:
                    if transaction["type"] in ["receita", "income"]:
                        balance += transaction["amount"]
                    else:
                        balance -= transaction["amount"]
                return {
                    "status": "success", 
                    "balance": round(balance, 2),
                    "transactions_count": len(transactions_data["transactions"])
                }
            return transactions_data
        except Exception as e:
            return {"status": "error", "message": f"Balance calculation failed: {str(e)}"}

# Criar cliente
finance_client = FinanceClient("https://mcp-smartfinance-axfmb5eaehhpfkab.canadacentral-01.azurewebsites.net")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Finance MCP Server running"})

@app.route('/tools', methods=['GET'])
def list_tools():
    """Lista as ferramentas disponíveis"""
    tools = [
        {
            "name": "add_transaction",
            "description": "Adiciona uma transação financeira. Use 'receita' para entradas e 'despesa' para saídas",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Valor (ex: 150.50)"},
                    "description": {"type": "string", "description": "Descrição (ex: 'Salário', 'Aluguel')"},
                    "type": {"type": "string", "enum": ["receita", "despesa"], "description": "Tipo: receita ou despesa"},
                    "category": {"type": "string", "description": "Categoria (ex: 'salário', 'alimentação')"},
                    "merchant_name": {"type": "string", "description": "Estabelecimento (opcional)"}
                },
                "required": ["amount", "description", "type"]
            }
        },
        {
            "name": "get_transactions",
            "description": "Lista todas as transações em ordem decrescente de data",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_balance",
            "description": "Calcula o saldo atual (receitas - despesas)",
            "inputSchema": {
                "type": "object", 
                "properties": {}
            }
        }
    ]
    return jsonify({"tools": tools})

@app.route('/tools/<tool_name>', methods=['POST'])
def call_tool(tool_name):
    """Executa uma ferramenta"""
    data = request.json
    arguments = data.get('arguments', {})
    
    if tool_name == "add_transaction":
        result = finance_client.add_transaction(
            arguments["amount"],
            arguments["description"],
            arguments["type"],
            arguments.get("category", "general"),
            arguments.get("merchant_name")
        )
    elif tool_name == "get_transactions":
        result = finance_client.get_transactions()
    elif tool_name == "get_balance":
        result = finance_client.get_balance()
    else:
        result = {"status": "error", "message": f"Ferramenta desconhecida: {tool_name}"}
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)