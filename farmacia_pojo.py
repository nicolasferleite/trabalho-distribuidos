from dataclasses import dataclass
from typing import List, Any
import struct
import sys
from abc import ABC, abstractmethod

@dataclass
class Medicamento:
    """Superclasse: Medicamento"""
    codigo: int
    nome: str
    preco: float
    estoque: int

    def to_bytes(self) -> bytes:
        """
        Serializa os atributos selecionados para uma sequência de bytes.
        
        Serializa: codigo (I), nome (str), preco (f), estoque (I).
        Formato Fixo (62 bytes total):
        - 4 bytes para codigo (unsigned int)
        - 50 bytes (fixos) para nome (string preenchida com espaços)
        - 4 bytes para preco (float)
        - 4 bytes para estoque (unsigned int)
        """
        # Formato: < (little-endian), I (4), 50s (50), f (4), I (4)
        FORMAT = '<I50sfI'

        # Encodificar o nome para 50 bytes, preenchendo ou truncando
        nome_bytes = self.nome.encode('utf-8')
        nome_bytes_fixed = nome_bytes.ljust(50)[0:50]

        try:
            return struct.pack(FORMAT, self.codigo, nome_bytes_fixed, self.preco, self.estoque)
        except struct.error as e:
            print(f"Erro ao empacotar {self}: {e}", file=sys.stderr)
            raise

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Medicamento':
        """Desserializa uma sequência de bytes para um objeto Medicamento."""
        FORMAT = '<I50sfI'
        
        try:
            codigo, nome_bytes, preco, estoque = struct.unpack(FORMAT, data)
            # Decodifica e remove espaços em branco extras (strip)
            nome = nome_bytes.decode('utf-8', errors='ignore').strip()
            return cls(codigo=codigo, nome=nome, preco=preco, estoque=estoque)
        except struct.error as e:
            print(f"Erro ao desempacotar: {e}", file=sys.stderr)
            raise
    
    @classmethod
    def get_serial_size(cls) -> int:
        """Retorna o número de bytes usados para gravar os atributos serializados."""
        return struct.calcsize('<I50sfI') # 62 bytes

# --- Subclasses ---

@dataclass
class MedicamentoControlado(Medicamento):
    """Subclasse: Medicamento Controlado"""
    receita_obrigatoria: bool = True

@dataclass
class MedicamentoComum(Medicamento):
    """Subclasse: Medicamento Comum"""
    pass

@dataclass
class Cosmetico(Medicamento):
    """Subclasse: Cosmético"""
    area_aplicacao: str = "N/A"

@dataclass
class Suplemento(Medicamento):
    """Subclasse: Suplemento"""
    tipo: str = "N/A"

@dataclass
class EquipamentoHospitalar(Medicamento):
    """Subclasse: Equipamento Hospitalar"""
    departamento: str = "N/A"

# --- Interface ---

class Vendas(ABC):
    """Interface Vendas"""

    @abstractmethod
    def verificarReceita(self, item: Medicamento) -> bool:
        """Verifica se um item exige receita."""
        pass

    @abstractmethod
    def atualizarEstoque(self, codigo: int, mudanca: int) -> Medicamento | None:
        """Atualiza o estoque de um item."""
        pass

    @abstractmethod
    def registrarAtendimento(self, codigo: int, quantidade: int) -> (bool, str):
        """Processa a venda de um item."""
        pass