from datetime import datetime

from sqlmodel import Field, SQLModel

from .models import StatusCanario

class BaseCreate(SQLModel):
    nome: str
    destino: str
    organizacao_id: int

class PlantarCreate(SQLModel):
    qtd: int 


class BasePublic(BaseCreate): 
    id: int
    criada_em: datetime

class CanarioPublic(SQLModel):
    id: int
    nome_ficticio: str
    email: str
    url_isca: str
    status: StatusCanario