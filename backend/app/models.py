from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel

def agora() -> datetime:
    return datetime.now(timezone.utc)

class StatusCanario(str, Enum):
    ATIVO = "ATIVO"
    DISPARADO = "DISPARADO"
    APOSENTADO = "APOSENTADO"

class Confianca(str, Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA" 
    ALTA = "ALTA"

class Organizacao(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str 
    criada_em: datetime = Field(default_factory=agora)

class Base(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    organizacao_id: int = Field(foreign_key="organizacao.id", index=True)
    nome: str
    destino: str
    criada_em: datetime = Field(default_factory=agora)

class Canario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    base_id: int = Field(foreign_key="base.id", index=True)
    token: str = Field(unique=True, index=True)
    nome_ficticio: str
    email: str
    url_isca: str
    status: StatusCanario = StatusCanario.ATIVO
    plantado_em: datetime = Field(default_factory=agora)

class Evento(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    canario_id: int | None = Field(default=None, foreign_key="canario.id", index=True)
    tipo: str 
    origem: str
    payload_bruto: str
    recebido_em: datetime = Field(default_factory=agora)

class Incidente(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    canario_id: int = Field(foreign_key="canario.id", index=True)
    base_id: int = Field(foreign_key="base.id", index=True)
    janela_inicio: datetime  # copia de Canario.plantado_em
    janela_fim: datetime  # recebido_em do primeiro Evento
    confianca: Confianca
    aberto_em: datetime = Field(default_factory=agora)


    