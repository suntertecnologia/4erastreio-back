
import http.server
import socketserver
import json
import sqlite3

# --- Configurações ---
DB_NAME = "entregas.db"
PORT = 8000

# ==============================================================================
# PASSO 1: CONFIGURAÇÃO DO BANCO DE DADOS SQLITE
# ==============================================================================
def setup_database():
    """Cria e configura o banco de dados e as tabelas se não existirem."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --- Tabela para as informações gerais da entrega ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entregas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transportadora TEXT,
        codigo_rastreio TEXT UNIQUE,
        numero_nf TEXT,
        previsao_entrega TEXT,
        data_postagem TEXT,
        remetente_nome TEXT,
        remetente_cnpj TEXT,
        destinatario_nome TEXT,
        destinatario_cnpj TEXT,
        erro TEXT
    )
    """)

    # --- Tabela para o histórico de ocorrências ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico_entregas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entrega_id INTEGER,
        timestamp TEXT,
        status TEXT,
        cidade TEXT,
        estado TEXT,
        detalhes TEXT,
        FOREIGN KEY (entrega_id) REFERENCES entregas (id)
    )
    """)

    conn.commit()
    conn.close()
    print(f"Banco de dados '{DB_NAME}' configurado com sucesso.")

# ==============================================================================
# PASSO 2: O SERVIDOR HTTP PARA RECEBER OS DADOS
# ==============================================================================
class JSONRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    RequestHandler customizado para processar requisições POST com JSON.
    """
    def do_POST(self):
        """
        Processa uma requisição POST, lê o JSON e o insere no banco de dados.
        """
        if self.path == '/receber_json':
            try:
                # --- Lê o corpo da requisição ---
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                # --- Insere os dados no banco ---
                self.insert_data(data)

                # --- Responde com sucesso ---
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "sucesso", "mensagem": "Dados recebidos e salvos."}).encode())

            except json.JSONDecodeError:
                self.send_error(400, "Erro: JSON inválido.")
            except Exception as e:
                self.send_error(500, f"Erro interno do servidor: {e}")
        else:
            self.send_error(404, "Endpoint não encontrado. Use /receber_json")

    def insert_data(self, data):
        """
        Insere os dados do JSON nas tabelas do banco de dados.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # --- Insere na tabela 'entregas' ---
        info = data.get("informacoes_gerais", {})
        remetente = info.get("remetente", {})
        destinatario = info.get("destinatario", {})
        
        cursor.execute("""
            INSERT OR REPLACE INTO entregas (
                transportadora, codigo_rastreio, numero_nf, previsao_entrega, data_postagem,
                remetente_nome, remetente_cnpj, destinatario_nome, destinatario_cnpj, erro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            info.get("transportadora"), info.get("codigo_rastreio"), info.get("numero_nf"),
            info.get("previsao_entrega"), info.get("data_postagem"),
            remetente.get("nome"), remetente.get("cnpj"),
            destinatario.get("nome"), destinatario.get("cnpj"),
            data.get("erro")
        ))
        
        entrega_id = cursor.lastrowid

        # --- Deleta o histórico antigo para evitar duplicatas ---
        cursor.execute("DELETE FROM historico_entregas WHERE entrega_id = ?", (entrega_id,))

        # --- Insere na tabela 'historico_entregas' ---
        historico = data.get("historico", [])
        for item in historico:
            local = item.get("local", {})
            cursor.execute("""
                INSERT INTO historico_entregas (
                    entrega_id, timestamp, status, cidade, estado, detalhes
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                entrega_id, item.get("timestamp"), item.get("status"),
                local.get("cidade"), local.get("estado"), item.get("detalhes")
            ))

        conn.commit()
        conn.close()
        print(f"Dados para o código de rastreio '{info.get('codigo_rastreio')}' foram salvos no banco.")

# ==============================================================================
# PASSO 3: INICIALIZAÇÃO DO SERVIDOR
# ==============================================================================
if __name__ == "__main__":
    # --- Garante que o banco e as tabelas existam ---
    setup_database()

    # --- Inicia o servidor HTTP ---
    with socketserver.TCPServer(("", PORT), JSONRequestHandler) as httpd:
        print(f"Servidor iniciado na porta {PORT}. Aguardando requisições POST em /receber_json...")
        httpd.serve_forever()
