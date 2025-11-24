import azure.functions as func
import pyodbc
import json
import logging
import requests
import os
import re
from keys import AGENT_ENDPOINT, AGENT_API_KEY, AGENT_ID

app = func.FunctionApp()

def call_agent(user_message):
    """Chama o Agent do AI Foundry"""
    try:
        headers = {
            "Content-Type": "application/json",
            "api-key": AGENT_API_KEY
        }
        
        data = {
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 1000
        }
        
        url = f"{AGENT_ENDPOINT}/openai/deployments/{AGENT_ID}/chat/completions?api-version=2024-02-01"
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        return response.json()
        
    except Exception as e:
        return {"error": str(e)}

def extract_transaction_data(message):
    """Extrai dados de transação de mensagens naturais em português"""
    message_lower = message.lower()
    
    # Padrões para extrair valor
    amount_pattern = r'(\d+[.,]?\d*)\s*(reais|real|r\$)'
    amount_simple = r'(\d+[.,]?\d*)'
    
    # Determinar tipo
    transaction_type = "despesa" if any(word in message_lower for word in ['gastei', 'paguei', 'comprei', 'gasto', 'despesa']) else "receita"
    
    # Extrair valor
    amount_match = re.search(amount_pattern, message_lower)
    if not amount_match:
        amount_match = re.search(amount_simple, message_lower)
    
    amount = float(amount_match.group(1).replace(',', '.')) if amount_match else None
    
    # Extrair descrição (remove números e palavras comuns)
    description = re.sub(r'\d+[.,]?\d*\s*(reais|real|r\$)?', '', message)
    description = re.sub(r'\b(gastei|paguei|recebi|comprei|no|na|de|por)\b', '', description, flags=re.IGNORECASE)
    description = description.strip()
    
    # Categoria padrão baseada em palavras-chave
    category = "outros"
    if any(word in message_lower for word in ['comida', 'restaurante', 'ifood', 'mercado', 'alimentação', 'alimento']):
        category = "alimentação"
    elif any(word in message_lower for word in ['uber', 'táxi', 'transporte', 'gasolina', 'ônibus']):
        category = "transporte"
    elif any(word in message_lower for word in ['aluguel', 'condomínio', 'casa', 'moradia']):
        category = "moradia"
    elif any(word in message_lower for word in ['salário', 'pagamento', 'receita']):
        category = "salário"
    
    return {
        "amount": amount,
        "description": description if description else "Transação",
        "type": transaction_type,
        "category": category
    }

def get_db_connection():
    """Retorna conexão com o banco de dados"""
    server = "smartfinance-server.database.windows.net"
    database = "finance-db" 
    username = "smartfinance"
    password = "DBpassword123"

    connection_string = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={server};"
        f"Database={database};"
        f"Uid={username};"
        f"Pwd={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    return pyodbc.connect(connection_string)

@app.function_name(name="ProcessTransaction")
@app.route(route="transactions", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def process_transaction(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        req_body = req.get_json()
        logging.info(f'Received data: {req_body}')
        
        # Validate required fields
        required_fields = ["amount", "description", "type"]
        for field in required_fields:
            if field not in req_body:
                return func.HttpResponse(
                    json.dumps({"status": "error", "message": f"Missing field: {field}"}),
                    status_code=400,
                    mimetype="application/json"
                )

        # Connect to database and insert transaction
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Create transactions table if not exists
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='transactions' AND xtype='U')
                    CREATE TABLE transactions (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        amount DECIMAL(10,2) NOT NULL,
                        description NVARCHAR(255) NOT NULL,
                        type NVARCHAR(50) NOT NULL,
                        category NVARCHAR(100),
                        merchant_name NVARCHAR(100),
                        date DATETIME DEFAULT GETDATE()
                    )
                """)
                
                # Insert transaction
                cursor.execute("""
                    INSERT INTO transactions (amount, description, type, category, merchant_name)
                    VALUES (?, ?, ?, ?, ?)
                """,  
                req_body["amount"], 
                req_body["description"], 
                req_body["type"],
                req_body.get("category"),
                req_body.get("merchant_name")
                )
                
                conn.commit()

        return func.HttpResponse(
            json.dumps({
                "status": "success", 
                "message": "Transaction processed successfully",
                "transaction": req_body
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.function_name(name="GetTransactions")
@app.route(route="transactions", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_transactions(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a GET request.')
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, amount, description, type, category, merchant_name, date FROM transactions ORDER BY date DESC")
                rows = cursor.fetchall()
                
                transactions = []
                for row in rows:
                    transactions.append({
                        "id": row[0],
                        "amount": float(row[1]),
                        "description": row[2],
                        "type": row[3],
                        "category": row[4],
                        "merchant_name": row[5],
                        "date": row[6].isoformat() if row[6] else None
                    })

        return func.HttpResponse(
            json.dumps({"status": "success", "transactions": transactions}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.function_name(name="AgentWebhook")
@app.route(route="agent-webhook", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def agent_webhook(req: func.HttpRequest) -> func.HttpResponse:
    """Webhook que o Agent chama quando precisa executar ações"""
    try:
        req_body = req.get_json()
        user_message = req_body.get("message", "")
        
        logging.info(f"Agent webhook received: {user_message}")
        
        # Analisar a mensagem do usuário para determinar a ação
        if any(word in user_message.lower() for word in ['gastei', 'paguei', 'recebi', 'comprei']):
            # Extrair dados da mensagem natural
            transaction_data = extract_transaction_data(user_message)
            
            if not transaction_data["amount"]:
                return func.HttpResponse(
                    json.dumps({
                        "status": "error", 
                        "message": "Não consegui identificar o valor da transação. Formato esperado: 'gastei 50 no ifood'"
                    }),
                    status_code=400,
                    mimetype="application/json"
                )
            
            # Processar transação com dados extraídos
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO transactions (amount, description, type, category)
                        VALUES (?, ?, ?, ?)
                    """,  
                    transaction_data["amount"], 
                    transaction_data["description"], 
                    transaction_data["type"],
                    transaction_data["category"]
                    )
                    conn.commit()
            
            response_data = {
                "status": "success",
                "action": "transaction_added", 
                "message": f"Transação de {transaction_data['type']} no valor de R$ {transaction_data['amount']} adicionada com sucesso!",
                "transaction": transaction_data
            }
            
        elif any(word in user_message.lower() for word in ['saldo', 'transações', 'extrato', 'histórico']):
            # Buscar transações do banco
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT amount, type FROM transactions ORDER BY date DESC LIMIT 20")
                    rows = cursor.fetchall()
                    
                    transactions = []
                    balance = 0
                    for row in rows:
                        amount = float(row[0])
                        trans_type = row[1]
                        
                        if trans_type == "receita":
                            balance += amount
                        else:
                            balance -= amount
                        
                        transactions.append({
                            "amount": amount,
                            "type": trans_type
                        })
            
            response_data = {
                "status": "success", 
                "action": "transactions_retrieved",
                "message": f"Saldo atual: R$ {balance:.2f}",
                "balance": balance,
                "transactions_count": len(transactions)
            }
        else:
            response_data = {
                "status": "info",
                "message": "Comando não reconhecido. Use: 'gastei X no Y', 'recebi X de Y' ou 'qual meu saldo?'"
            }

        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f'Webhook error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.function_name(name="HealthCheck")
@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint de health check"""
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "SmartFinance API",
            "endpoints": {
                "POST /api/transactions": "Adicionar transação",
                "GET /api/transactions": "Listar transações", 
                "POST /api/agent-webhook": "Webhook para agentes",
                "GET /api/health": "Health check"
            }
        }),
        status_code=200,
        mimetype="application/json"
    )