from sqlmodel import select

from app.config import settings
from app.models import Confianca, Evento, Incidente, StatusCanario
from app.schemas import EmailRecebido
from app.servicos.correlacao import processar_email
from app.servicos.gerador import plantar


def montar_email(destinatario: str) -> EmailRecebido:
    # Função auxiliar: não começa com "test_", então o pytest não a executa
    # como teste. Só evita repetir os 4 campos em cada teste.
    # "exemplo.com" é um domínio fictício: nada de dados reais nos testes.
    return EmailRecebido(
        remetente="golpista@exemplo.com",
        destinatario=destinatario,
        assunto="Seu cadastro foi bloqueado",
        corpo="Clique no link para regularizar.",
    )


def test_email_com_token_valido_abre_incidente(session, base):
    # Arrange: 5 canários no banco; o golpista escreve para só um deles.
    canarios = plantar(session, base, 5)
    alvo = canarios[0]

    # Act
    incidente = processar_email(session, montar_email(alvo.email))

    # Assert 1: o retorno é um Incidente ligado ao canário e à base certos.
    assert incidente is not None
    assert incidente.confianca == Confianca.ALTA
    assert incidente.canario_id == alvo.id
    assert incidente.base_id == base.id

    # Assert 2: o estado no banco. refresh() relê o objeto do banco,
    # para vermos o que a função realmente gravou.
    session.refresh(alvo)
    assert alvo.status == StatusCanario.DISPARADO

    # Os outros 4 continuam ATIVO: prova que a busca pegou o canário certo,
    # e não "qualquer um".
    for outro in canarios[1:]:
        session.refresh(outro)
        assert outro.status == StatusCanario.ATIVO


def test_email_sem_token_nao_abre_incidente(session, base):
    # Arrange: canários no banco só como cenário. Com o banco vazio,
    # o teste passaria por um motivo trivial.
    plantar(session, base, 5)
    email = montar_email(f"contato@{settings.dominio_isca}")

    # Act
    resultado = processar_email(session, email)

    # Assert: nenhum incidente...
    assert resultado is None
    # A classe Incidente é só a definição da tabela. Para ver o que foi
    # salvo, consultamos o banco (como um repository.findAll() no Spring).
    incidentes = session.exec(select(Incidente)).all()
    assert len(incidentes) == 0

    # ...mas o Evento é registrado sempre, como órfão (sem canário).
    eventos = session.exec(select(Evento)).all()
    assert len(eventos) == 1
    assert eventos[0].canario_id is None


def test_segundo_email_nao_duplica_incidente(session, base):
    # Arrange
    canario = plantar(session, base, 1)[0]
    email = montar_email(canario.email)

    # Act: o mesmo canário recebe dois golpes.
    primeiro = processar_email(session, email)
    segundo = processar_email(session, email)

    # Assert: só o primeiro abre incidente; o segundo encontra o canário
    # já DISPARADO e devolve None.
    assert primeiro is not None
    assert segundo is None

    incidentes = session.exec(select(Incidente)).all()
    assert len(incidentes) == 1

    # Os dois e-mails viram Evento: o histórico do vazamento fica completo.
    eventos = session.exec(select(Evento)).all()
    assert len(eventos) == 2
