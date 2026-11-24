from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel

def agora() -> datetime:
    return datetime.now(timezone.utc)

class StatusCanario(str, Enum):
    ATIVO = "ATIVO"
    DISPARADO = "DISPARADO"
    APOSENTADO = "APOSENTADO"


class Base(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    base_id: int = Field(foreign_key="base.id", index=True)
    token: str = Field(unique=True, index=True)
    nome_ficticio: str
    email: str
    url_isca: str
    status: StatusCanario = StatusCanario.ATIVO
    plantado_em: datetime = Field(default_factory=agora)

    