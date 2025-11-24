import asyncio
import requests

def test_finance_api():
    """Testa a API diretamente"""
    base_url = "https://mcp-smartfinance-axfmb5eaehhpfkab.canadacentral-01.azurewebsites.net"
    
    print("=== TESTE FINAL DA API ===")
    
    # Adicionar transação
    print("Adicionando transação...")
    response = requests.post(f"{base_url}/api/transactions", json={
        "amount": 500.00,
        "description": "Teste Final MCP",
        "type": "receita", 
        "category": "teste",
        "merchant_name": "AI Foundry"
    })
    print("POST:", response.json())
    
    # Listar transações
    print("\nListando transações...")
    response = requests.get(f"{base_url}/api/transactions")
    print("GET:", response.json())
    
    return response.json()

if __name__ == "__main__":
    test_finance_api()