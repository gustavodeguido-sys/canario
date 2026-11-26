from sqlmodel import select

from app.config import settings
from app.models import Base, Canario, StatusCanario
from app.servicos.gerador import plantar


def test_plantar_cria_a_quantidade_pedida(session, base):
    canarios = plantar(session, base, 5)

    assert len(canarios) == 5


def test_canarios_ficam_salvos_no_banco(session, base):
    plantar(session, base, 5)

    consulta = select(Canario).where(Canario.base_id == base.id)
    no_banco = session.exec(consulta).all()

    assert len(no_banco) == 5


def test_tokens_sao_unicos(session, base):
    canarios = plantar(session, base, 50)

    tokens = [c.token for c in canarios]

    # O set descarta repetidos: se os tamanhos batem, não houve repetição.
    assert len(set(tokens)) == len(tokens)


def test_token_tem_tamanho_seguro(session, base):
    canarios = plantar(session, base, 5)

    for c in canarios:
        # token_hex(8) = 8 bytes = 16 caracteres hexadecimais
        assert len(c.token) == 16


def test_email_usa_dominio_isca_e_contem_token(session, base):
    canarios = plantar(session, base, 5)

    for c in canarios:
        assert c.email.endswith("@" + settings.dominio_isca)
        assert c.token in c.email


def test_url_isca_termina_com_token(session, base):
    canarios = plantar(session, base, 5)

    for c in canarios:
        assert c.url_isca.endswith("/c/" + c.token)


def test_email_nao_tem_acento_nem_espaco(session, base):
    canarios = plantar(session, base, 20)

    for c in canarios:
        assert c.email.isascii()
        assert " " not in c.email


def test_canario_nasce_ativo_e_ligado_a_base(session, base):
    canarios = plantar(session, base, 5)

    for c in canarios:
        assert c.status == StatusCanario.ATIVO
        assert c.base_id == base.id


def test_dois_lotes_nao_colidem(session, base):
    # Arrange: uma segunda cópia da base, da mesma organização (ex.: a gráfica).
    outra_base = Base(organizacao_id=base.organizacao_id, nome="Base da gráfica", destino="grafica")
    session.add(outra_base)
    session.commit()
    session.refresh(outra_base)

    # Act: cada cópia recebe o seu lote.
    lote_interno = plantar(session, base, 20)
    lote_grafica = plantar(session, outra_base, 20)

    # Assert: nenhum token aparece nos dois lotes...
    tokens_interno = {c.token for c in lote_interno}
    tokens_grafica = {c.token for c in lote_grafica}
    assert tokens_interno.isdisjoint(tokens_grafica)

    # ...e cada lote ficou ligado à sua própria base.
    assert all(c.base_id == base.id for c in lote_interno)
    assert all(c.base_id == outra_base.id for c in lote_grafica)
