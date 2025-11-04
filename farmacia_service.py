from farmacia_pojo import Medicamento, MedicamentoControlado, Vendas
from typing import List, Dict

class Farmacia:
    """
    Classe de modelo (Agregação).
    Contém um conjunto de medicamentos para venda e controle de estoque.
    """
    
    def __init__(self):
        # Usamos um dicionário para busca rápida por código
        self.itens_estoque: Dict[int, Medicamento] = {}
        self.last_codigo = 0

    def adicionar_item(self, item: Medicamento) -> Medicamento:
        """Adiciona um novo item ao sistema ou atualiza existente."""
        if item.codigo == 0: # Auto-incrementa se o código for 0
            self.last_codigo += 1
            item.codigo = self.last_codigo
        
        if item.codigo in self.itens_estoque:
            print(f"Item {item.codigo} já existe. Atualizando...")
            
        self.itens_estoque[item.codigo] = item
        print(f"Item '{item.nome}' (Código {item.codigo}) adicionado/atualizado.")
        return item

    def buscar_item_por_codigo(self, codigo: int) -> Medicamento | None:
        """Busca um item pelo código."""
        return self.itens_estoque.get(codigo)
        
    def get_todos_itens(self) -> List[Medicamento]:
        """Retorna uma lista de todos os itens."""
        return list(self.itens_estoque.values())

class ServicoVendasFarmacia(Vendas):
    """
    Classe de modelo que implementa a interface de Vendas.
    """
    
    def __init__(self, farmacia: Farmacia):
        # Recebe a agregação
        self.farmacia = farmacia

    def verificarReceita(self, item: Medicamento) -> bool:
        """Verifica se o item é um MedicamentoControlado."""
        return isinstance(item, MedicamentoControlado)

    def atualizarEstoque(self, codigo: int, mudanca: int) -> Medicamento | None:
        """
        Altera o estoque de um item.
        'mudanca' pode ser negativa (venda) ou positiva (reposição).
        """
        item = self.farmacia.buscar_item_por_codigo(codigo)
        if item:
            if (item.estoque + mudanca) < 0:
                return None # Estoque insuficiente
            item.estoque += mudanca
            return item
        return None

    def registrarAtendimento(self, codigo: int, quantidade: int) -> (bool, str):
        """
        Tenta registrar uma venda (atendimento).
        """
        item = self.farmacia.buscar_item_por_codigo(codigo)
        
        if not item:
            return (False, "Item não encontrado.")
            
        if quantidade <= 0:
            return (False, "Quantidade deve ser positiva.")

        # 1. Verifica Receita
        if self.verificarReceita(item):
            print(f"Atendimento: {item.nome} exige receita. (Simulando verificação OK)")
            
        # 2. Verifica e Atualiza Estoque
        item_atualizado = self.atualizarEstoque(codigo, -quantidade) # Tenta baixar o estoque
        
        if not item_atualizado:
            return (False, f"Estoque insuficiente. Disponível: {item.estoque}")

        return (True, f"Venda de {quantidade}x {item.nome} registrada. Novo estoque: {item_atualizado.estoque}")