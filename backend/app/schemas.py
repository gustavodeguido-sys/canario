from datetime import datetime

from sqlmodel import SQLModel

from .models import StatusCanario

class BaseCreate(SQLModel):
    nome: str
    destino: str

class BasePublic(BaseCreate): 
    id: int
    criada_em: datetime

class CanarioPublic(SQLModel):
    id: int
    nome_ficticio: str
    email: str
    url_isca: str
    status: StatusCanario