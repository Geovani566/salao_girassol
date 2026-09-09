import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr
from crud_api import CrudApi
from database import inicializar_banco
from fastapi.middleware.cors import CORSMiddleware


def load_local_env():
    """Carrega o arquivo .env local sem sobrescrever variaveis do Render."""
    env_file = Path(__file__).with_name(".env")
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip())


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"A variavel de ambiente {name} precisa ser configurada.")
    return value


load_local_env()
ADMIN_EMAIL = required_env("ADMIN_EMAIL")
ADMIN_PASSWORD = required_env("ADMIN_PASSWORD")
ADMIN_TOKEN = required_env("ADMIN_TOKEN")


def require_admin(authorization: str | None = Header(default=None)):
    if authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="Nao autorizado")


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
def listar_agendamentos(_admin: None = Depends(require_admin)):
    return crud.listar_agendamentos()

@app.get("/agendamentos/{id}")
def buscar_agendamento(id: int, _admin: None = Depends(require_admin)):
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
def editar_agendamento(id: int, agendamento: AgendamentoUpdate, _admin: None = Depends(require_admin)):
    if crud.buscar_agendamento(id) is None:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return crud.editar_agendamento(id, agendamento.nome)

@app.delete("/agendamentos/{id}")
def deletar_agendamento(id: int, _admin: None = Depends(require_admin)):
    if crud.buscar_agendamento(id) is None:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    crud.deletar_agendamento(id)
    return {"status": "Agendamento deletado com sucesso!"}

@app.post("/admin/login")
def login(dados:login):
    if (
        dados.email == ADMIN_EMAIL
        and dados.senha == ADMIN_PASSWORD
    ): 
        return {"access_token": ADMIN_TOKEN}
    raise HTTPException(
        status_code=401,
        detail= "Credenciais inválidas"
    )
@app.get("/mostrar_servicos")
def mostrar_servicos():
    return crud.mostrar_servicos()


@app.post("/novo_servico")
def criar_novo_servico(servico: novo_servico, _admin: None = Depends(require_admin)):
    novo_id = crud.criar_servico(
        servico.nome,
        servico.descricao,
        servico.cor,
        servico.duracao,
        servico.preco,
    )
    return {"status": "Serviço criado com sucesso!", "id": novo_id}

@app.get("/horarios_trabalho")
def listar_horarios_trabalho(_admin: None = Depends(require_admin)):
    return crud.listar_horarios_trabalho()

@app.post("/horarios_trabalho")
def salvar_horarios_trabalho(horarios: list[HorarioTrabalho], _admin: None = Depends(require_admin)):
    return crud.salvar_horarios_trabalho([horario.model_dump() for horario in horarios])

@app.get("/horarios_disponiveis")
def listar_horarios_disponiveis(data: str, servico: str):
    return {"horarios": crud.listar_horarios_disponiveis(data, servico)}
