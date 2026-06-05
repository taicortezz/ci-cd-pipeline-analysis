# Task Manager CI Metrics

API simples de gerenciamento de tarefas criada para uma atividade academica
sobre analise de metricas de pipelines CI/CD com GitHub Actions.

O objetivo do projeto e manter uma base pequena, legivel e facil de testar.
A API usa dados em memoria e nao possui banco de dados, autenticacao, Docker
ou servicos externos.

## Tecnologias

- Python 3.12
- FastAPI
- Pytest
- Flake8

## Instalar dependencias

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Executar a API

```bash
uvicorn app.main:app --reload
```

A documentacao interativa fica disponivel em:

```text
http://127.0.0.1:8000/docs
```

## Executar os testes

```bash
pytest tests
```

## Executar lint

```bash
flake8 --jobs 1 app tests
```

## Pipeline CI

O workflow `.github/workflows/ci.yml` executa em `push` e `pull_request`.
Ele instala as dependencias, roda o lint com Flake8 e executa os testes com
Pytest.

Ao final, o pipeline gera dois artefatos para apoiar analises futuras:

- `test-results.xml`: resultado dos testes em formato JUnit XML.
- `test-summary.json`: resumo simples com total de testes, falhas e data de geracao.

## Endpoints

- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}/complete`
- `DELETE /tasks/{task_id}`
- `GET /tasks/stats`
