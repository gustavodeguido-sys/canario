import secrets 
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException

from ..config import settings
from ..db import SessionDep
from ..schemas import EmailRecebido
from ..servicos import correlacao

router = APIRouter(prefix="/webhooks", tags=["sensores"])

@router.post("/email", status_code=202)
def receber_email(
    evento: EmailRecebido,
    session: SessionDep,
    x_canario_segredo: Annotated[str, Header()],
):
    esperado = settings.webhook_segredo
    if not esperado or not secrets.compare_digest(x_canario_segredo.encode(),
     esperado.encode()):
        raise HTTPException(status_code=401, detail="Segredo inválido")
    correlacao.processar_email(session, evento)
    return {"recebido": True}