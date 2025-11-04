import socket
import json
import sys

# --- Configurações ---
SERVER_HOST = '127.0.0.1' # IP do servidor TCP
SERVER_PORT = 50007       # Porta do servidor TCP

# --- Funções Auxiliares (Comunicação TCP) ---

def send_request(sock: socket.socket, request: dict) -> dict:
    """Envia um dicionário (JSON) e retorna a resposta (dicionário)."""
    try:
        sock.sendall(json.dumps(request).encode('utf-8'))
        response_data = sock.recv(2048)
        return json.loads(response_data.decode('utf-8'))
    except (ConnectionResetError, BrokenPipeError):
        print("Erro: Conexão com o servidor perdida.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Erro: Resposta inválida do servidor: {response_data.decode('utf-8')}")
        return {"status": "erro", "msg": "Resposta corrompida do servidor"}

def login(sock: socket.socket) -> bool:
    """Tenta autenticar o administrador via TCP. """
    print("--- Login do Administrador ---")
    usuario = input("Usuário (admin): ")
    senha = input("Senha (admin123): ")
    
    req = {"acao": "login", "usuario": usuario, "senha": senha}
    resp = send_request(sock, req)
    
    if resp.get('status') == 'ok' and resp.get('tipo') == 'admin':
        print("Login de admin realizado com sucesso.")
        return True
    
    print(f"Falha no login: {resp.get('msg')}")
    return False

# --- Loop Principal (Main) do Admin ---
def main():
    # Conecta ao Servidor (TCP)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((SERVER_HOST, SERVER_PORT))
            print(f"Conectado ao servidor TCP em {SERVER_HOST}:{SERVER_PORT}")
            
            # Tenta fazer o Login
            if not login(sock):
                print("Encerrando.")
                return

            # Loop do Menu Principal (Admin) 
            while True:
                print("\n--- Menu do Administrador ---")
                print("1. Adicionar candidato")
                print("2. Enviar nota informativa (Multicast)")
                print("3. Sair")
                escolha = input("> ")

                # Opção 1: Adicionar Candidato
                if escolha == '1':
                    nome_cand = input("Nome do novo candidato: ")
                    req = {"acao": "add_candidato", "nome": nome_cand}
                    resp = send_request(sock, req)
                    print(f"Resposta do Servidor: {resp.get('msg')}")
                
                # Opção 2: Enviar Nota (via TCP, que o servidor fará Multicast)
                elif escolha == '2':
                    nota = input("Mensagem da nota: ")
                    req = {"acao": "enviar_nota", "nota": nota}
                    resp = send_request(sock, req)
                    print(f"Resposta do Servidor: {resp.get('msg')}")
                
                # Opção 3: Sair
                elif escolha == '3':
                    print("Desconectando...")
                    break
                
                else:
                    print("Opção inválida.")
                    
    except ConnectionRefusedError:
        print(f"Erro: Não foi possível conectar ao servidor em {SERVER_HOST}:{SERVER_PORT}")
        print("Verifique se 'voting_server.py' está em execução.")

if __name__ == "__main__":
    main()