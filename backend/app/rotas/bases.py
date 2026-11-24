from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from ..db import SessionDep
from ..models import Base, Canario 
from ..schemas import BaseCreate, BasePublic, CanarioPublic
from ..servicos import gerador

router = APIRouter(prefix="/api/bases", tags=["bases"])

@router.post("", response_model=BasePublic, status_code=201)
def criar_base(dados: BaseCreate, session: SessionDep):
    base = Base.model_validate(dados)
    session.add(base)
    session.commit()
    session.refresh(base)
    return base


@router.post("/{base_id}/canarios", response_model=list[CanarioPublic], status_code=201)
def gerar_canarios(
    base_id: int,
    session: SessionDep,
    qtd: Annotated[int, Query(ge=1, le=50)] = 5,
):
    base = session.get(Base, base_id)
    if base is None:
        raise HTTPException(status_code=404, detail="Base não encontrada")
    return gerador.plantar(session, base, qtd)

@router.get("/{base_id}/canarios", response_model=list[CanarioPublic])
def listar_canarios(base_id: int, session: SessionDep):
    consulta = select(Canario).where(Canario.base_id == base_id)
    return session.exec(consulta).all()