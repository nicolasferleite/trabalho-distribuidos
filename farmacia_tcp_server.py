import socket
from farmacia_streams import MedicamentoStreamReader, MedicamentoStreamWriter
from farmacia_pojo import MedicamentoComum
from farmacia_service import Farmacia
import threading

# Instancia o serviço de gestão da farmácia
farmacia_db = Farmacia()
farmacia_db.adicionar_item(
    MedicamentoComum(codigo=0, nome="Dipirona Servidor", preco=5.50, estoque=100)
)
# Lock para proteger o acesso à farmacia_db por múltiplas threads
db_lock = threading.Lock()

# Configurações do servidor
HOST = '127.0.0.1'
PORT = 65432

def handle_client(conn, addr):
    """Função para cuidar de uma conexão de cliente (multi-threaded)."""
    print(f"Conectado por {addr}")
    try:
        with conn:
            # "Embrulha" o socket 'conn' em objetos do tipo arquivo
            file_reader = conn.makefile('rb')
            file_writer = conn.makefile('wb')

            # 1. Servidor desempacota request
            print(f"Servidor [{addr}]: Aguardando dados do cliente...")
            reader = MedicamentoStreamReader(file_reader)
            itens_recebidos = reader.read_itens()
            
            print(f"Servidor [{addr}]: {len(itens_recebidos)} item(ns) recebido(s):")
            
            # Protege o acesso ao "banco de dados"
            with db_lock:
                for item in itens_recebidos:
                    print(f"  - [RECEBIDO DE {addr}] {item}")
                    farmacia_db.adicionar_item(item)
                
                print(f"Servidor: Total de itens únicos agora: {len(farmacia_db.itens_estoque)}")
                # Pega a lista atualizada para enviar de volta
                lista_completa_atualizada = farmacia_db.get_todos_itens()

            # 2. Servidor empacota reply
            print(f"Servidor [{addr}]: Enviando lista atualizada de volta...")
            writer = MedicamentoStreamWriter(file_writer)
            writer.write_itens(lista_completa_atualizada)
            print(f"Servidor [{addr}]: Resposta enviada.")
            
    except Exception as e:
        print(f"Erro ao lidar com cliente {addr}: {e}")

def start_server():
    """Inicia o loop principal do servidor TCP."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor da Farmácia ouvindo em {HOST}:{PORT}")
        
        while True:
            try:
                conn, addr = s.accept()
                
                # Cria e inicia uma nova thread para cuidar do cliente
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.daemon = True 
                client_thread.start()
                
            except KeyboardInterrupt:
                print("\nServidor encerrando por comando...")
                break
            except Exception as e:
                print(f"Erro no loop principal do servidor: {e}")

if __name__ == "__main__":
    start_server()