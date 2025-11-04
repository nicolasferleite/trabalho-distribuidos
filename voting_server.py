import socket
import threading
import json
import time
import struct # Necessário para o setup do multicast

# --- Configurações do Servidor ---
HOST_TCP = '0.0.0.0'  # Ouve em todas as interfaces
PORT_TCP = 50007      # Porta para TCP (Login, Votos)

# --- Configurações do Multicast (UDP) ---
MCAST_GROUP = '224.1.1.1' # Endereço de grupo multicast
MCAST_PORT = 50008        # Porta para UDP (Notas) 

# --- "Banco de Dados" Global (Simulado) ---
# Dicionário de candidatos: {id: {"nome": "Nome"}}
candidatos = {
    1: {"nome": "Candidato A"},
    2: {"nome": "Candidato B"}
}
# Dicionário para contar votos: {id_candidato: contagem}
votos = {1: 0, 2: 0}
# Usuários válidos: {username: {"senha": "123", "tipo": "voter" or "admin"}}
usuarios = {
    "votante1": {"senha": "123", "tipo": "voter"},
    "votante2": {"senha": "abc", "tipo": "voter"},
    "admin": {"senha": "admin123", "tipo": "admin"}
}
# Conjunto de usuários logados (para controle)
usuarios_logados = set()
# Flag para controlar o período de votação
votacao_aberta = True
# Lock para proteger o acesso às variáveis globais (necessário em ambiente multi-thread)
db_lock = threading.Lock()

# --- Funções do Servidor ---

def encerrar_votacao(tempo_limite_segundos: int):
    """
    Função (executada em uma thread) que age como um timer.
    Após o tempo, muda a flag 'votacao_aberta' e imprime os resultados.
    """
    global votacao_aberta
    print(f"[TIMER] Votação iniciada. Tempo limite: {tempo_limite_segundos} segundos.")
    time.sleep(tempo_limite_segundos)
    
    with db_lock:
        votacao_aberta = False
        print("\n--- [TIMER] VOTACÃO ENCERRADA ---")
        
        total_votos = sum(votos.values())
        print(f"Total de votos: {total_votos}")
        
        if total_votos == 0:
            print("Nenhum voto registrado.")
            return

        print("Resultados:")
        vencedor_nome = ""
        vencedor_votos = -1
        
        for id_cand, contagem in votos.items():
            nome_cand = candidatos.get(id_cand, {}).get("nome", f"ID {id_cand}")
            percentual = (contagem / total_votos) * 100
            print(f"  - {nome_cand}: {contagem} votos ({percentual:.2f}%)")
            
            if contagem > vencedor_votos:
                vencedor_votos = contagem
                vencedor_nome = nome_cand
            elif contagem == vencedor_votos:
                vencedor_nome += f" e {nome_cand}" # Empate

        print(f"Vencedor(es): {vencedor_nome}\n")
        
def enviar_nota_multicast(nota: str):
    """
    Envia uma nota informativa (string) via UDP Multicast.
    """
    print(f"[MULTICAST] Enviando nota: '{nota}'")
    
    # Cria um socket UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        # Define o Time-To-Live (TTL) para 1.
        # Isso impede que o pacote saia da rede local (default é 1).
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        
        # Envia a mensagem (codificada) para o GRUPO e PORTA multicast
        sock.sendto(nota.encode('utf-8'), (MCAST_GROUP, MCAST_PORT))
        

def handle_client_tcp(conn: socket.socket, addr):
    """
    Função (executada em uma thread) que cuida da comunicação
    TCP (JSON) com um cliente (Votante ou Admin).
    """
    print(f"[TCP] Nova conexão de {addr}")
    usuario_atual = None
    tipo_usuario = None
    
    try:
        while True:
            # Recebe dados (até 2048 bytes)
            data = conn.recv(2048)
            if not data:
                break # Cliente desconectou

            # Decodifica os bytes para string e depois para JSON (dicionário)
            try:
                req = json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                resp = {"status": "erro", "msg": "Requisição JSON inválida."}
                conn.sendall(json.dumps(resp).encode('utf-8'))
                continue
            
            acao = req.get("acao")
            resp = {} # Resposta padrão

            # --- Lógica de Ações ---

            # 1. Ação: Login
            if acao == "login":
                user = req.get("usuario")
                pwd = req.get("senha")
                
                with db_lock: # Protege 'usuarios' e 'usuarios_logados'
                    info_user = usuarios.get(user)
                    
                    if info_user and info_user["senha"] == pwd:
                        if user in usuarios_logados:
                            resp = {"status": "erro", "msg": "Usuário já está logado."}
                        else:
                            usuarios_logados.add(user)
                            usuario_atual = user
                            tipo_usuario = info_user["tipo"]
                            resp = {"status": "ok", "msg": f"Login como {tipo_usuario} bem-sucedido.", "tipo": tipo_usuario}
                    else:
                        resp = {"status": "erro", "msg": "Usuário ou senha inválidos."}

            # --- Ações que exigem login ---
            elif not usuario_atual:
                resp = {"status": "erro", "msg": "Acesso negado. Faça login primeiro."}
            
            # 2. Ação: Pegar Candidatos (Votante)
            elif acao == "get_candidatos" and tipo_usuario == "voter":
                with db_lock: # Protege 'candidatos'
                    resp = {"status": "ok", "candidatos": candidatos}
            
            # 3. Ação: Votar (Votante)
            elif acao == "votar" and tipo_usuario == "voter":
                with db_lock: # Protege 'votacao_aberta', 'votos', 'candidatos'
                    if not votacao_aberta:
                        resp = {"status": "erro", "msg": "Votação encerrada."}
                    else:
                        id_cand = req.get("id_candidato")
                        if id_cand in candidatos:
                            votos[id_cand] += 1
                            resp = {"status": "ok", "msg": f"Voto em '{candidatos[id_cand]['nome']}' registrado."}
                        else:
                            resp = {"status": "erro", "msg": "ID de candidato inválido."}

            # 4. Ação: Adicionar Candidato (Admin)
            elif acao == "add_candidato" and tipo_usuario == "admin":
                nome_cand = req.get("nome")
                if not nome_cand:
                    resp = {"status": "erro", "msg": "Nome do candidato não fornecido."}
                else:
                    with db_lock: # Protege 'candidatos' e 'votos'
                        novo_id = max(candidatos.keys() or [0]) + 1
                        candidatos[novo_id] = {"nome": nome_cand}
                        votos[novo_id] = 0 # Inicializa contagem de votos
                        resp = {"status": "ok", "msg": f"Candidato '{nome_cand}' (ID: {novo_id}) adicionado."}
            
            # 5. Ação: Enviar Nota (Admin)
            elif acao == "enviar_nota" and tipo_usuario == "admin":
                nota = req.get("nota")
                if not nota:
                    resp = {"status": "erro", "msg": "Nota não pode ser vazia."}
                else:
                    enviar_nota_multicast(f"[ADMIN-NOTA] {nota}")
                    resp = {"status": "ok", "msg": "Nota enviada para o multicast."}

            # Ação desconhecida
            else:
                resp = {"status": "erro", "msg": f"Ação '{acao}' desconhecida ou não permitida para o tipo '{tipo_usuario}'."}

            # Envia a resposta (JSON) de volta ao cliente
            conn.sendall(json.dumps(resp).encode('utf-8'))

    except (ConnectionResetError, BrokenPipeError):
        print(f"[TCP] Cliente {addr} desconectou abruptamente.")
    except Exception as e:
        print(f"[TCP] Erro com {addr}: {e}")
    finally:
        # Garante que o usuário seja "deslogado" se a conexão cair
        if usuario_atual:
            with db_lock:
                if usuario_atual in usuarios_logados:
                    usuarios_logados.remove(usuario_atual)
        conn.close()
        print(f"[TCP] Conexão com {addr} fechada.")

# --- Loop Principal (Main) do Servidor ---
def main():
    # 1. Inicia a thread do timer da votação
    # (Definido para 120 segundos = 2 minutos)
    timer_thread = threading.Thread(target=encerrar_votacao, args=(600,), daemon=True)
    timer_thread.start()

    # 2. Configura e inicia o servidor TCP
    # (Usamos o 'with' para garantir que o socket será fechado)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        # Permite que o servidor re-use o endereço imediatamente
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Vincula o socket ao host e porta TCP
        tcp_socket.bind((HOST_TCP, PORT_TCP))
        # Começa a escutar por conexões
        tcp_socket.listen()
        print(f"Servidor TCP (Votação) ouvindo em {HOST_TCP}:{PORT_TCP}")

        # 3. Loop principal para aceitar novas conexões TCP
        while True:
            try:
                # Aceita uma nova conexão
                conn, addr = tcp_socket.accept()
                # Cria uma nova thread para cuidar desse cliente
                client_thread = threading.Thread(target=handle_client_tcp, args=(conn, addr), daemon=True)
                # Inicia a thread
                client_thread.start()
            except KeyboardInterrupt:
                print("Servidor encerrando...")
                break # Sai do loop se (Ctrl+C) for pressionado
            except Exception as e:
                print(f"Erro ao aceitar conexão: {e}")

if __name__ == "__main__":
    main()