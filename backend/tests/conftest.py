"""Fixtures compartilhadas pelos testes.

O pytest carrega este arquivo sozinho: qualquer teste em tests/ pode pedir
`session` ou `base` como parâmetro, sem importar nada.
"""

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401  registra as tabelas no metadata
from app.models import Base, Organizacao


@pytest.fixture
def session():
    # Banco SQLite em memória, novo a cada teste: nenhum teste vê os dados de outro.
    # StaticPool + check_same_thread=False mantêm uma única conexão, para que o
    # banco em memória não suma entre conexões (será necessário no TestClient).
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def base(session: Session) -> Base:
    # Organização fictícia da demo, conforme o CLAUDE.md.
    organizacao = Organizacao(nome="Casa de Apoio Esperança")
    session.add(organizacao)
    session.commit()
    session.refresh(organizacao)

    base = Base(organizacao_id=organizacao.id, nome="Base interna", destino="interna")
    session.add(base)
    session.commit()
    session.refresh(base)
    return base
