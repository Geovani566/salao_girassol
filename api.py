from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from crud_api import CrudApi
from database import inicializar_banco
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
inicializar_banco()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, restrinja isso
    allow_methods=["*"],
    allow_headers=["*"],
)
crud = CrudApi()
class novo_servico(BaseModel):
    nome:str
    descricao:str
    cor:str
    duracao:float
    preco:float




class login(BaseModel):
    email:str
    senha:str

class Agendamento(BaseModel):
    nome: str
    telefone: str
    servico:str
    data: str
    hora: str

class AgendamentoUpdate(BaseModel):
    nome: str

class HorarioTrabalho(BaseModel):
    dia_semana: int
    ativo: bool
    hora_inicio: str
    hora_fim: str
    intervalo: int

@app.get("/")
def home():
    return {"status": "API ESTÁ RODANDO!"}

@app.get("/agendamentos")
def listar_agendamentos():
    return crud.listar_agendamentos()

@app.get("/agendamentos/{id}")
def buscar_agendamento(id: int):
    resultado = crud.buscar_agendamento(id)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return resultado

@app.post("/criar_agendamento")
def criar_novo_agendamento(agendamento: Agendamento):
    try:
        crud.criar_agendamento(
            agendamento.nome,
            agendamento.servico,
            agendamento.telefone,
            agendamento.data,
            agendamento.hora,
        )
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro))
    return {"status": "Agendamento criado com sucesso!"}

@app.put("/agendamentos/{id}")
def editar_agendamento(id: int, agendamento: AgendamentoUpdate):
    if crud.buscar_agendamento(id) is None:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return crud.editar_agendamento(id, agendamento.nome)

@app.delete("/agendamentos/{id}")
def deletar_agendamento(id: int):
    if crud.buscar_agendamento(id) is None:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    crud.deletar_agendamento(id)
    return {"status": "Agendamento deletado com sucesso!"}

@app.post("/admin/login")
def login(dados:login):
    if (
        dados.email == "teste@123"
        and dados.senha =="123"
    ): 
        return {"access_token":"token_teste"}
    raise HTTPException(
        status_code=401,
        detail= "Credenciais inválidas"
    )
@app.get("/mostrar_servicos")
def mostrar_servicos():
    return crud.mostrar_servicos()


@app.post("/novo_servico")
def criar_novo_servico(servico: novo_servico):
    novo_id = crud.criar_servico(
        servico.nome,
        servico.descricao,
        servico.cor,
        servico.duracao,
        servico.preco,
    )
    return {"status": "Serviço criado com sucesso!", "id": novo_id}

@app.get("/horarios_trabalho")
def listar_horarios_trabalho():
    return crud.listar_horarios_trabalho()

@app.post("/horarios_trabalho")
def salvar_horarios_trabalho(horarios: list[HorarioTrabalho]):
    return crud.salvar_horarios_trabalho([horario.model_dump() for horario in horarios])

@app.get("/horarios_disponiveis")
def listar_horarios_disponiveis(data: str, servico: str):
    return {"horarios": crud.listar_horarios_disponiveis(data, servico)}
