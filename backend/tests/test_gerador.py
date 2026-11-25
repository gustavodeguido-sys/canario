from app.config import settings
from app.servicos.gerador import plantar

def test_plantar_cria_a_quantidade_pedida(session, base):
    canarios = plantar(session, base, 5)
    assert 