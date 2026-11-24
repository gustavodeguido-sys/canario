# Canário — contexto do projeto

Canário é um sistema de **detecção de vazamento de dados por registros-isca** (canary tokens), feito para o hackathon **Hack Brasil**, na trilha de **Cibersegurança**. Desenvolvedor: Gustavo, trabalhando sozinho. Estudante de ADS na FIAP, com foco em back-end.

**Prazo final da entrega: 30/11/2026, 23h59.** Tudo deve caber nesse prazo. Prefira a solução simples que funciona à solução elegante que atrasa.

## O que o produto faz

1. **Plantar:** gera registros falsos (nome, e-mail, link-isca) no formato da base da organização. Cada cópia da base (interna, gráfica, CRM) recebe o seu próprio lote de canários.
2. **Esperar:** nenhum contato legítimo procura esses "clientes".
3. **Cantar:** quando alguém usa um canário (e-mail recebido no domínio-isca ou link-isca aberto), um webhook registra o evento.
4. **Responder:** o motor de correlação liga token → canário → base → cópia de origem e abre um Incidente com a janela do vazamento (plantado_em → primeiro evento) e a confiança (BAIXA, MÉDIA ou ALTA).
5. **Diferencial:** um LLM lê a mensagem do golpista, classifica o golpe e gera um aviso pronto para os clientes reais e um rascunho de comunicação à ANPD.

Público-alvo: organizações pequenas sem time de segurança (ONGs, clínicas, casas de apoio).

## Stack

- **Backend:** Python 3.11+, FastAPI, SQLModel, SQLite em dev e Postgres no deploy, Faker("pt_BR"), pydantic-settings, pytest
- **Frontend:** React + Vite em `frontend/` (painel ao vivo via SSE)
- **E-mail:** domínio próprio com Cloudflare Email Routing e um Email Worker que faz POST em `/webhooks/email`
- **Deploy:** Render ou Railway
- **Ambiente:** Windows + PowerShell, venv em `backend/.venv`

## Estrutura

```
canario/
├── backend/
│   ├── app/
│   │   ├── main.py        # monta o app: lifespan, CORS, include_router
│   │   ├── config.py      # Settings lê o .env
│   │   ├── db.py          # engine, get_session, SessionDep
│   │   ├── models.py      # tabelas: Organizacao, Base, Canario, Evento, Incidente
│   │   ├── schemas.py     # contratos de entrada/saída (*Create, *Public)
│   │   ├── rotas/         # camada HTTP: bases, incidentes, webhooks
│   │   └── servicos/      # regras de negócio: gerador, correlacao, classificador
│   ├── tests/
│   ├── pyproject.toml     # [tool.fastapi] entrypoint = "app.main:app"
│   └── requirements.txt
└── frontend/
```

## Regras de arquitetura

- **Rotas são finas:** recebem, validam, chamam um serviço e devolvem. Nenhuma regra de negócio fica em `rotas/`.
- **Serviços não importam `fastapi`.** Eles recebem a `Session` como parâmetro.
- **Imports só descem:** rotas → servicos → models/schemas → config. `models.py` e `config.py` não importam nada do projeto. Uma rota nunca importa outra rota.
- **`models.py` ≠ `schemas.py`:** nunca use uma classe `table=True` como corpo de requisição. A saída usa `*Public` e esconde campos internos como `payload_bruto`.
- **Rotas que usam a `Session` são `def`, não `async def`.** Use `async def` só no stream SSE e em chamadas HTTP assíncronas (`httpx.AsyncClient`, LLM).
- **Use `lifespan`, não `@app.on_event`.**
- `main.py` precisa manter `from . import models` para o `create_all` criar as tabelas.

## Convenções

- Código, nomes e comentários em **português**, sem acento em identificadores: `plantado_em`, `nome_ficticio`.
- snake_case para funções e variáveis, PascalCase para classes. Datas sempre em UTC (`datetime.now(timezone.utc)`).
- Status HTTP corretos: 201 ao criar, 202 em webhook, 404 quando o recurso não existe, 401 quando o segredo é inválido.
- Mensagens de commit em português, no imperativo e curtas: "Adiciona gerador de canários".

## Segurança (a trilha é de cibersegurança: isso é avaliado)

- Os webhooks exigem o header `X-Canario-Segredo`, comparado com `secrets.compare_digest`.
- Tokens são gerados com `secrets`, nunca com `random`.
- Segredos ficam só no `.env`, que nunca é commitado. Mantenha o `.env.example` atualizado quando criar uma variável nova.
- **Nunca use dados pessoais reais** em código, testes, seeds ou demo. A organização da demo é fictícia ("Casa de Apoio Esperança"). Não use a marca da Caixa em nenhum material além da manchete citada no vídeo.
- Os e-mails de golpe da demo só podem ser enviados para endereços do próprio domínio-isca.

## Comandos (rode de dentro de `backend/`, com o venv ativo)

```powershell
.venv\Scripts\Activate.ps1      # ativar o venv
fastapi dev                     # servidor de dev; documentação em http://127.0.0.1:8000/docs
pytest -q                       # testes
pip freeze > requirements.txt   # depois de instalar um pacote
```

Se mudar colunas de um model, apague `canario.db`: o `create_all` não altera tabelas existentes.

## Plano

- Dia 1: models e gerador de canários
- Dia 2: sensor de e-mail (webhook) e correlação
- Dia 3: painel React ao vivo (SSE)
- Dia 4: injeção no navegador, lotes por cópia e LLM
- Dia 5: deploy e README
- Dia 6: gravar o vídeo da demo (até 3 min)

## Como trabalhar comigo

- **Estou aprendendo FastAPI. Prefiro escrever o código principal eu mesmo**, de preferência `servicos/` (gerador, correlação e classificador), apenas guie dando dicas sobre o código quando eu pedir. Por padrão, explique o conceito, aponte o problema ou proponha a estrutura, e só escreva a implementação completa quando eu pedir.
- Ao revisar o meu código, aponte erros e riscos com clareza e explique o porquê, comparando com Java/Spring Boot quando ajudar.
- Faça mudanças pequenas e focadas. Não reestruture pastas nem renomeie arquivos sem perguntar.
- Antes de dar uma tarefa por concluída, rode `pytest -q` e confirme que passa.
- Lembre-me de commitar ao fim de cada parte que funcionar. O regulamento avalia o histórico de commits feitos durante o evento.
- Responda em português.