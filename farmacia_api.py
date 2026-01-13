from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

# --- 1. MODELO DE DADOS (O que é um remédio) ---
class Medicine(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    category: str

# --- 2. LÓGICA DE NEGÓCIO (Banco de dados em memória) ---
class Inventory:
    def __init__(self):
        # Dicionário para guardar os remédios {id: dados}
        self.medicines: Dict[int, dict] = {} 
        self.counter = 1 # Auto-incremento para o ID

        # Dados iniciais para não começar vazio
        self.add(Medicine(id=0, name="Dipirona 500mg", price=5.50, quantity=100, category="Analgésico"))
        self.add(Medicine(id=0, name="Vitamina C", price=12.00, quantity=50, category="Suplemento"))
        self.add(Medicine(id=0, name="Amoxicilina", price=25.90, quantity=20, category="Antibiótico"))

    def get_all(self) -> List[dict]:
        return list(self.medicines.values())

    def add(self, med: Medicine):
        # Atribui um ID novo e salva
        med.id = self.counter
        self.medicines[self.counter] = med.dict()
        self.counter += 1
        return med

    def sell(self, med_id: int, qtd: int):
        if med_id in self.medicines:
            current_qtd = self.medicines[med_id]['quantity']
            if current_qtd >= qtd:
                self.medicines[med_id]['quantity'] -= qtd
                return True
        return False

    def delete(self, med_id: int):
        if med_id in self.medicines:
            del self.medicines[med_id]
            return True
        return False

# --- 3. CONFIGURAÇÃO DA API (Rotas) ---
app = FastAPI()
inventory = Inventory()

# Configuração CORS (Permite que o JS e o C# acessem a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota: Listar tudo
@app.get("/medicines")
def list_medicines():
    return inventory.get_all()

# Rota: Adicionar novo
@app.post("/medicines")
def add_medicine(med: Medicine):
    return inventory.add(med)

# Rota: Vender (Baixar estoque)
@app.post("/sell/{med_id}/{quantity}")
def sell_medicine(med_id: int, quantity: int):
    success = inventory.sell(med_id, quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Erro: Estoque insuficiente ou ID inválido")
    return {"status": "sold", "id": med_id, "quantity_sold": quantity}

# Rota: Deletar
@app.delete("/medicines/{med_id}")
def delete_medicine(med_id: int):
    inventory.delete(med_id)
    return {"status": "deleted"}

# Se quiser rodar direto pelo Python sem usar o comando 'uvicorn' no terminal
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)