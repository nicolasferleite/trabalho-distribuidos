import socket
from farmacia_streams import MedicamentoStreamReader, MedicamentoStreamWriter
from farmacia_pojo import MedicamentoControlado, Cosmetico

# Configurações do servidor para o qual vamos conectar
HOST = '127.0.0.1'
PORT = 65432

# Cria os POJOs que o cliente quer enviar
item_novo_1 = MedicamentoControlado(
    codigo=0, nome="Rivotril Cliente", preco=25.75, estoque=50
)
item_novo_2 = Cosmetico(
    codigo=0, nome="Shampoo Cliente", preco=18.99, estoque=100, area_aplicacao="Cabelo"
)
lista_para_enviar = [item_novo_1, item_novo_2]

# Cria o objeto socket TCP/IP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        # Tenta se conectar ao endereço e porta do servidor
        s.connect((HOST, PORT))
        print("Cliente: Conectado ao servidor.")
        
        # "Embrulha" o socket 's' em objetos do tipo arquivo.
        file_writer = s.makefile('wb')
        file_reader = s.makefile('rb')

        # 1. Cliente empacota request
        writer = MedicamentoStreamWriter(file_writer)
        writer.write_itens(lista_para_enviar)
        print(f"Cliente: Enviou {len(lista_para_enviar)} item(ns) para o servidor.")

        # 2. Cliente desempacota reply
        print("Cliente: Aguardando resposta do servidor...")
        reader = MedicamentoStreamReader(file_reader)
        resposta_servidor = reader.read_itens()
        
        print(f"Cliente: Resposta do servidor recebida ({len(resposta_servidor)} itens na lista total):")
        for item in resposta_servidor:
            print(f"  - [RESPOSTA] {item}")

    except ConnectionRefusedError:
        print(f"Erro: Não foi possível conectar a {HOST}:{PORT}.")
        print("Verifique se o 'farmacia_tcp_server.py' está em execução.")
    except Exception as e:
        print(f"Erro durante a comunicação: {e}")

    print("Cliente: Conexão fechada.")