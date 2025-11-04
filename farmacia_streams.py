import struct
import sys
from typing import List, Any
from farmacia_pojo import Medicamento

class MedicamentoStreamWriter:
    """
    Escreve uma LISTA de objetos Medicamento em um stream de destino 
    (arquivo, socket, stdout).
    """

    def __init__(self, dest_stream: Any):
        """
        Construtor. Recebe o stream de destino.
        :param dest_stream: Um objeto com método .write()
        """
        self.stream = dest_stream

    def write_itens(self, itens: List[Medicamento]):
        """
        Escreve a lista de itens no stream.
        
        Formato:
        1. Cabeçalho: [Num Objetos (I)] [Tam. Objeto (I)] - 8 bytes
        2. Dados: [Objeto 1] [Objeto 2] ...
        """
        try:
            num_objetos = len(itens)
            serial_size = Medicamento.get_serial_size()

            if num_objetos == 0:
                print("Aviso: Tentando escrever uma lista vazia.", file=sys.stderr)

            # 1. Escreve o Cabeçalho: (num_objetos, serial_size)
            header_format = '<II'
            header_bytes = struct.pack(header_format, num_objetos, serial_size)
            self.stream.write(header_bytes)

            # 2. Escreve cada objeto
            for item in itens:
                item_bytes = item.to_bytes()
                self.stream.write(item_bytes)
            
            # Garante que os dados sejam enviados (flush)
            if hasattr(self.stream, 'flush'):
                self.stream.flush()

        except Exception as e:
            print(f"Erro ao escrever no stream: {e}", file=sys.stderr)


class MedicamentoStreamReader:
    """
    Lê uma lista de objetos Medicamento de um stream de origem
    (arquivo, socket, stdin).
    """

    def __init__(self, source_stream: Any):
        """
        Construtor. Recebe o stream de origem.
        :param source_stream: Um objeto com método .read()
        """
        self.stream = source_stream

    def read_itens(self) -> List[Medicamento]:
        """
        Lê o cabeçalho e, em seguida, todos os objetos do stream,
        retornando uma lista de POJOs Medicamento.
        """
        itens_lidos = []
        try:
            # 1. Lê o Cabeçalho (exatos 8 bytes = I + I)
            header_format = '<II'
            header_size = struct.calcsize(header_format)
            header_bytes = self.stream.read(header_size)

            # Se não vier nada, o stream fechou (EOF)
            if not header_bytes:
                return [] 

            num_objetos, serial_size = struct.unpack(header_format, header_bytes)

            # Verificação de segurança
            expected_size = Medicamento.get_serial_size()
            if serial_size != expected_size:
                raise ValueError(f"Tamanho do objeto no stream ({serial_size}) não confere com o esperado ({expected_size})")

            # 2. Lê cada objeto do stream
            for _ in range(num_objetos):
                objeto_bytes = self.stream.read(serial_size)
                
                if len(objeto_bytes) < serial_size:
                    raise IOError("Stream interrompido no meio da leitura dos dados.")
                
                item = Medicamento.from_bytes(objeto_bytes)
                itens_lidos.append(item)
            
            return itens_lidos

        except Exception as e:
            print(f"Erro ao ler do stream: {e}", file=sys.stderr)
            return itens_lidos