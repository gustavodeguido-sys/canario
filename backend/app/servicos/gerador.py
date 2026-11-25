import secrets
import unicodedata

from faker import Faker
from sqlmodel import Session

from ..config import settings
from ..models import Base, Canario

fake = Faker("pt_BR")


def novo_token() -> str:
    return secrets.token_hex(8)


def remover_acentos(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.lower()


def plantar(session: Session, base: Base, qtd: int) -> list[Canario]:
    canarios = []
    for _ in range(qtd):
        token = novo_token()
        nome_ficticio = f"{fake.first_name()} {fake.last_name()}"
        local_email = remover_acentos(nome_ficticio).replace(" ", ".")
        email = f"{local_email}.{token}@{settings.dominio_isca}"
        url_isca = f"https://{settings.dominio_isca}/c/{token}"
        canario = Canario(
            base_id=base.id,
            token=token,
            nome_ficticio=nome_ficticio,
            email=email,
            url_isca=url_isca,
        )
        canarios.append(canario)
    session.add_all(canarios)
    session.commit()

    for canario in canarios:
        session.refresh(canario)

    return canarios