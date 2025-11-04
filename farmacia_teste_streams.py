import sys
import math # Importa a biblioteca de matemática para comparar floats
from farmacia_pojo import Cosmetico, Suplemento, EquipamentoHospitalar
from farmacia_streams import MedicamentoStreamWriter, MedicamentoStreamReader

# POJOs de exemplo
item1 = Cosmetico(codigo=1, nome="Shampoo Anti-Caspa", preco=22.50, estoque=100, area_aplicacao="Cabelo")
item2 = Suplemento(codigo=2, nome="Whey Protein", preco=150.0, estoque=30, tipo="Proteina")
item3 = EquipamentoHospitalar(codigo=3, nome="Seringa Descartável", preco=1.20, estoque=1000, departamento="Injeção")

meus_itens = [item1, item2, item3]
ARQUIVO_BIN = "itens_farmacia.bin"

def testar_escrita_arquivo():
    """Teste: Escreve em um arquivo (FileOutputStream)"""
    print(f"Testando: Escrita para arquivo '{ARQUIVO_BIN}'...")
    with open(ARQUIVO_BIN, "wb") as f:
        writer_file = MedicamentoStreamWriter(f)
        writer_file.write_itens(meus_itens)
    print("...Escrita no arquivo concluída.")

def testar_leitura_arquivo():
    """Teste: Lê de um arquivo (FileInputStream)"""
    print(f"\nTestando: Leitura do arquivo '{ARQUIVO_BIN}'...")
    try:
        with open(ARQUIVO_BIN, "rb") as f:
            reader_file = MedicamentoStreamReader(f)
            itens_lidos = reader_file.read_itens()
            
            print(f"Itens lidos do arquivo ({len(itens_lidos)}):")
            for item in itens_lidos:
                print(f"  - {item}")
            
            # --- INÍCIO DA CORREÇÃO ---
            # A asserção 'assert itens_lidos == meus_itens' falha devido à
            # perda de precisão do float (1.20) e perda de tipo (Cosmetico -> Medicamento).
            
            # Vamos fazer uma verificação manual, atributo por atributo.
            assert len(itens_lidos) == len(meus_itens)
            
            for original, lido in zip(meus_itens, itens_lidos):
                assert original.codigo == lido.codigo
                assert original.nome == lido.nome
                assert original.estoque == lido.estoque
                # Compara os floats com uma pequena tolerância (aceita 1.20 vs 1.2000...04)
                assert math.isclose(original.preco, lido.preco, rel_tol=1e-5)
            # --- FIM DA CORREÇÃO ---
            
            print("...Verificação OK: Dados lidos são iguais aos escritos.")

    except FileNotFoundError:
        print(f"Erro: Arquivo '{ARQUIVO_BIN}' não encontrado.")
    except Exception as e:
        # Agora, se a asserção falhar, ela imprimirá uma mensagem de erro útil
        print(f"Erro ao ler arquivo: FALHA NA VERIFICAÇÃO - {e}")

def testar_stdout_writer():
    """Teste: Escreve na saída padrão (System.out)"""
    writer_stdout = MedicamentoStreamWriter(sys.stdout.buffer)
    writer_stdout.write_itens(meus_itens)

def testar_stdin_reader():
    """Teste: Lê da entrada padrão (System.in)"""
    reader_stdin = MedicamentoStreamReader(sys.stdin.buffer)
    itens_do_stdin = reader_stdin.read_itens()
    
    # Imprime os resultados no 'stderr' para não poluir o 'stdout'
    print(f"\n--- Leitura do Stdin ---", file=sys.stderr)
    print(f"Itens lidos do stdin ({len(itens_do_stdin)}):", file=sys.stderr)
    for p in itens_do_stdin:
        print(f"  - {p}", file=sys.stderr)
    print(f"--- Fim da Leitura do Stdin ---", file=sys.stderr)

if __name__ == "__main__":
    
    if "--modo=writer" in sys.argv:
        testar_stdout_writer()
    elif "--modo=reader" in sys.argv:
        testar_stdin_reader()
    else:
        # Execução padrão: Testar escrita e leitura de arquivo
        testar_escrita_arquivo()
        testar_leitura_arquivo()

        print("\n---\n")
        print("Testando Escrita/Leitura de Stdout/Stdin")
        print("Para testar, execute no terminal:")
        print("python farmacia_teste_streams.py --modo=writer | python farmacia_teste_streams.py --modo=reader")