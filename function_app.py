import azure.functions as func
import pyodbc
import json
import logging

app = func.FunctionApp()

@app.function_name(name="ProcessTransaction")
@app.route(route="transactions", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def process_transaction(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        # Get transaction data from request body
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

        # Your SQL Database credentials
        server = "smartfinance-server.database.windows.net"
        database = "finance-db" 
        username = "smartfinance"
        password = "DBpassword123"

        # Connection string
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

        # Connect to database and insert transaction
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # Create transactions table if not exists - COM TODAS AS COLUNAS CORRETAS
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
                
                # Insert transaction - APENAS COM COLUNAS QUE EXISTEM
                cursor.execute("""
                    INSERT INTO transactions (amount, description, type, category, merchant_name)
                    VALUES (?, ?, ?, ?, ?)
                """,  
                req_body["amount"], 
                req_body["description"], 
                req_body["type"],
                req_body.get("category"),  # .get() para campos opcionais
                req_body.get("merchant_name")  # .get() para campos opcionais
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
        # Your SQL Database credentials
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

        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                # SELECT com as colunas CORRETAS - usando 'date' em vez de 'created_at'
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