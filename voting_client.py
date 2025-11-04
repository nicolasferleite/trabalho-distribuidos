import socket
import threading
import json
import sys
import struct # Para setup do multicast

# --- Configurações ---
SERVER_HOST = '127.0.0.1' # IP do servidor TCP
SERVER_PORT = 50007       # Porta do servidor TCP

MCAST_GROUP = '224.1.1.1' # Mesmo grupo multicast do servidor
MCAST_PORT = 50008        # Mesma porta multicast do servidor

# --- Thread para Ouvir UDP Multicast ---
def listen_for_multicast_notes():
    """Thread que ouve passivamente por notas do admin via UDP. """
    # Cria um socket UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        try:
            # Permite que múltiplos sockets na mesma máquina ouçam o mesmo grupo
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Vincula o socket à porta multicast, em TODAS as interfaces ('0.0.0.0')
            sock.bind(('', MCAST_PORT))
            
            # Prepara a estrutura 'mreq' para se juntar ao grupo multicast
            # 1. IP do grupo multicast
            # 2. IP da interface local (INADDR_ANY = qualquer uma)
            mreq = struct.pack("4sl", socket.inet_aton(MCAST_GROUP), socket.INADDR_ANY)
            
            # Pede ao kernel para adicionar este socket ao grupo multicast
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            print(f"[Multicast] Ouvindo notas em {MCAST_GROUP}:{MCAST_PORT}...")
            
            # Loop infinito para receber mensagens
            while True:
                data, addr = sock.recvfrom(1024)
                print(f"\n--- [NOTA MULTICAST] ---")
                print(f"{data.decode('utf-8')}")
                print("--------------------------")
                print("> ", end="", flush=True) # Re-imprime o prompt do usuário
                
        except Exception as e:
            print(f"\n[Multicast] Erro: {e}. Thread encerrada.")

# --- Funções Auxiliares (Comunicação TCP) ---

def send_request(sock: socket.socket, request: dict) -> dict:
    """Envia um dicionário (JSON) e retorna a resposta (dicionário)."""
    try:
        # Envia a requisição
        sock.sendall(json.dumps(request).encode('utf-8'))
        # Recebe a resposta
        response_data = sock.recv(2048)
        # Decodifica e retorna
        return json.loads(response_data.decode('utf-8'))
    except (ConnectionResetError, BrokenPipeError):
        print("\nErro: Conexão com o servidor perdida.")
        sys.exit(1) # Encerra o cliente
    except json.JSONDecodeError:
        print(f"\nErro: Resposta inválida do servidor: {response_data.decode('utf-8')}")
        return {"status": "erro", "msg": "Resposta corrompida do servidor"}

def login(sock: socket.socket) -> bool:
    """Tenta autenticar o usuário via TCP. Retorna True se for um votante."""
    print("--- Login de Votante ---")
    usuario = input("Usuário (votante1, votante2): ")
    senha = input("Senha (123, abc): ")
    
    req = {"acao": "login", "usuario": usuario, "senha": senha}
    resp = send_request(sock, req)
    
    print(f"Servidor: {resp.get('msg')}")
    
    if resp.get('status') == 'ok' and resp.get('tipo') == 'voter':
        return True
    
    return False

# --- Loop Principal (Main) do Cliente ---
def main():
    # 1. Inicia a thread de escuta Multicast (UDP)
    # 'daemon=True' faz a thread fechar quando o programa principal fechar
    mcast_thread = threading.Thread(target=listen_for_multicast_notes, daemon=True)
    mcast_thread.start()

    # 2. Conecta ao Servidor (TCP)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((SERVER_HOST, SERVER_PORT))
            print(f"Conectado ao servidor TCP em {SERVER_HOST}:{SERVER_PORT}")
            
            # 3. Tenta fazer o Login
            if not login(sock):
                print("Login falhou ou não é um votante. Encerrando.")
                return

            # 4. Loop do Menu Principal (Votante)
            while True:
                print("\n--- Menu do Votante ---")
                print("1. Ver candidatos")
                print("2. Votar")
                print("3. Sair")
                escolha = input("> ")

                # Opção 1: Ver Candidatos
                if escolha == '1':
                    req = {"acao": "get_candidatos"}
                    resp = send_request(sock, req)
                    if resp.get('status') == 'ok':
                        print("--- Lista de Candidatos ---")
                        for id_cand, info in resp.get('candidatos', {}).items():
                            print(f"  ID: {id_cand} - Nome: {info['nome']}")
                    else:
                        print(f"Erro: {resp.get('msg')}")
                
                # Opção 2: Votar
                elif escolha == '2':
                    try:
                        id_voto = int(input("Digite o ID do candidato: "))
                        req = {"acao": "votar", "id_candidato": id_voto}
                        resp = send_request(sock, req)
                        print(f"Resposta do Servidor: {resp.get('msg')}")
                    except ValueError:
                        print("ID inválido. Deve ser um número.")
                
                # Opção 3: Sair
                elif escolha == '3':
                    print("Desconectando...")
                    break # Quebra o loop
                
                else:
                    print("Opção inválida.")
                    
    except ConnectionRefusedError:
        print(f"Erro: Não foi possível conectar ao servidor em {SERVER_HOST}:{SERVER_PORT}")
        print("Verifique se 'voting_server.py' está em execução.")

if __name__ == "__main__":
    main()