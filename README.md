# SDD TaskAnalyzer

Projeto cumulativo da disciplina **Bootcamp III** (CEUB), desenvolvido
seguindo o paradigma **Spec-Driven Development (SDD)**.

**Autor:** Juan Conceição Cassimiro — Ciências da Computação — Turma A - 0726
**E-mail institucional:** juan.cassimiro67@sempreceub.com

## Sobre o projeto

O TaskAnalyzer é um módulo de análise de tarefas e produtividade que
calcula, a partir de uma lista de tarefas, o tempo médio de conclusão,
a taxa de atraso e indicadores por prioridade. Todo o desenvolvimento
foi guiado por uma especificação executável (`specs/`) e por regras de
contexto para IA (`CONTEXT_RULES.md`), com homologação humana de todo
código gerado.

## Estrutura do repositório

```
sdd-task-analyzer/
├── README.md              # Este arquivo
├── CONTEXT_RULES.md        # Regras persistentes para a IA
├── specs/
│   └── task_analyzer_spec.md   # Especificação SDD (fonte da verdade)
├── tests/
│   └── test_harness.py    # Testes automatizados (pytest)
├── src/
│   └── task_analyzer.py   # Implementação homologada
├── .gitignore
└── requirements.txt
```

## Como executar os testes

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Como usar

```python
from datetime import datetime, timezone
from src.task_analyzer import Tarefa, Prioridade, StatusTarefa, analisar_tarefas

tarefas = [
    Tarefa(
        id_tarefa=1,
        titulo="Preparar relatório",
        prioridade=Prioridade.ALTA,
        status=StatusTarefa.CONCLUIDA,
        data_criacao=datetime(2026, 1, 1, tzinfo=timezone.utc),
        prazo=datetime(2026, 1, 3, tzinfo=timezone.utc),
        data_inicio=datetime(2026, 1, 1, 8, tzinfo=timezone.utc),
        data_conclusao=datetime(2026, 1, 2, 10, tzinfo=timezone.utc),
    ),
]

resultado = analisar_tarefas(tarefas)
print(resultado)
```

## Processo de desenvolvimento (SDD)

1. **Especificação** — `specs/task_analyzer_spec.md` define o contrato.
2. **Contexto** — `CONTEXT_RULES.md` orienta a geração de código por IA.
3. **Geração** — código implementado em `src/task_analyzer.py`.
4. **Validação** — testes automatizados em `tests/test_harness.py`.
5. **Homologação** — revisão humana antes de cada commit (ver
   `CONTEXT_RULES.md`, seção 4).

## CI/CD (GitHub Actions)

Todo push e Pull Request para `main`, `develop` e `feature/**` dispara
o workflow `.github/workflows/ci.yml`, que:

1. Executa a suíte de testes em Python 3.11 e 3.12.
2. Verifica o padrão de código (PEP 8) com `flake8`.
3. Constrói a imagem Docker e roda os testes dentro do container.

Nenhum merge deve ser aprovado com o pipeline falhando.

## Containerização (Docker)

```bash
docker build -t sdd-task-analyzer .
docker run --rm sdd-task-analyzer
```

Por padrão, o container executa a suíte de testes — a imagem só deve
ser considerada válida se todos os testes passarem.

## Governança e Revisão Ética

O relatório completo de governança, segurança e revisão ética (análise
de riscos de alucinação da IA, conformidade com LGPD, vieses e
limitações) está em [`docs/RELATORIO_GOVERNANCA_SEGURANCA.md`](docs/RELATORIO_GOVERNANCA_SEGURANCA.md).

## Fluxo de versionamento

Este repositório segue um Git flow simplificado:

- `main` — versão estável e homologada.
- `develop` — integração das funcionalidades.
- `feature/*` — desenvolvimento de cada funcionalidade isolada.

Commits pequenos e descritivos; Pull Requests obrigatórios para merge
em `develop` e `main`.
