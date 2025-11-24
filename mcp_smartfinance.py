import requests
import json

# URL da sua API
API_URL = "https://mcp-smartfinance-axfmb5eaehhpfkab.canadacentral-01.azurewebsites.net/api/transactions"

def add_transaction(amount, description, type, category="geral"):
    """Adiciona uma transação financeira via API"""
    data = {
        "amount": float(amount),
        "description": description,
        "type": type,
        "category": category
    }
    
    try:
        response = requests.post(API_URL, json=data, timeout=10)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_transactions():
    """Busca todas as transações"""
    try:
        response = requests.get(API_URL, timeout=10)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_balance():
    """Calcula o saldo total"""
    try:
        transactions = get_transactions()
        if transactions["status"] != "success":
            return transactions
            
        balance = 0
        for transaction in transactions["transactions"]:
            if transaction["type"] == "receita":
                balance += transaction["amount"]
            else:
                balance -= transaction["amount"]
                
        return {
            "status": "success", 
            "balance": balance,
            "message": f"Saldo atual: R$ {balance:.2f}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Teste rápido das funções
if __name__ == "__main__":
    print("=== TESTANDO FUNÇÕES ===")
    
    # Teste adicionar
    result = add_transaction(75.50, "Teste MCP", "despesa", "teste")
    print("Adicionar:", result)
    
    # Teste listar
    result = get_transactions()
    print("Listar:", result)
    
    # Teste saldo
    result = get_balance()
    print("Saldo:", result)