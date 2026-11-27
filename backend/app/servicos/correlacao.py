from sqlmodel import select
from app.models import Canario, StatusCanario, Evento, Incidente, Confianca
from app.schemas import EmailRecebido
from sqlmodel import Session

def processar_email(session: Session, email: EmailRecebido) -> Incidente | None :
    extrair_token = email.destinatario.split("@")[0].split(".")[-1]
    buscar_canario_pelo_token = select(Canario).where(Canario.token == extrair_token)
    no_banco = session.exec(buscar_canario_pelo_token).first()  
    registro = Evento(
                 tipo = "email",
                 origem = email.remetente,
                 payload_bruto = email.model_dump_json(),
                 canario_id = no_banco.id if no_banco else None,
             )
    session.add(registro)
    session.commit()
    session.refresh(registro)

    if no_banco is None or no_banco.status != StatusCanario.ATIVO:
        return None     
    no_banco.status = StatusCanario.DISPARADO
    incidente = Incidente(
                janela_inicio = no_banco.plantado_em,
                janela_fim = registro.recebido_em,
                canario_id = no_banco.id,
                base_id = no_banco.base_id,
                confianca = Confianca.ALTA
            )
    session.add(incidente)
    session.commit()
    session.refresh(incidente)
    return incidente 

 
