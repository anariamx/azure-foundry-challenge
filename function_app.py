import azure.functions as func
import pyodbc
import json
from datetime import datetime

app = func.FunctionApp()

@app.route(route="transactions", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def process_transaction(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get transaction data from request body
        req_body = req.get_json()
        
        # Validate required fields
        required_fields = ["amount", "description", "type"]  # type: 'income' or 'expense'
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
        password = "Dbpassword123"

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
                # Create transactions table if not exists
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='transactions' AND xtype='U')
                    CREATE TABLE transactions (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        amount DECIMAL(10,2) NOT NULL,
                        description NVARCHAR(255) NOT NULL,
                        type NVARCHAR(50) NOT NULL,
                        created_at DATETIME DEFAULT GETDATE()
                    )
                """)
                
                # Insert transaction
                cursor.execute("""
                    INSERT INTO transactions (amount, description, type)
                    VALUES (?, ?, ?)
                """, req_body["amount"], req_body["description"], req_body["type"])
                
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
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="transactions", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def get_transactions(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Your SQL Database credentials
        server = "smartfinance-server.database.windows.net"
        database = "finance-db"
        username = "smartfinance"
        password = "Dbpassword123"

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
                cursor.execute("SELECT * FROM transactions ORDER BY created_at DESC")
                rows = cursor.fetchall()
                
                transactions = []
                for row in rows:
                    transactions.append({
                        "id": row[0],
                        "amount": float(row[1]),
                        "description": row[2],
                        "type": row[3],
                        "created_at": row[4].isoformat() if row[4] else None
                    })

        return func.HttpResponse(
            json.dumps({"status": "success", "transactions": transactions}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )