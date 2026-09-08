from pydantic import BaseModel

class AgendamentoCreate(BaseModel):
    nome_cliente: str
    data: str
    hora: str