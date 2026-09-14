# Especificação SDD — TaskAnalyzer

**Autor:** Juan Conceição Cassimiro — Ciências da Computação — Turma A - 0726 (CEUB)
**Versão:** 1.0

> Esta especificação é a versão em Markdown, para versionamento no
> repositório, do documento entregue na Fase 1
> ("Especificação SDD TaskAnalyzer"). É a fonte da verdade que orienta
> a implementação e os testes deste projeto.

## 1. Propósito do Módulo

O TaskAnalyzer recebe uma lista de tarefas e calcula métricas de
produtividade: tempo médio de conclusão, taxa de atraso e indicadores
agregados por prioridade (baixa, média, alta). Não realiza persistência
de dados, não possui interface gráfica e não se comunica com serviços
externos.

## 2. Contrato Executável de Interface

### 2.1 Entradas (`Tarefa`)

| Campo | Tipo | Obrigatório | Descrição / Restrições |
|---|---|---|---|
| `id_tarefa` | int | Sim | Identificador único da tarefa (> 0). |
| `titulo` | str | Sim | Título/descrição curta da tarefa. |
| `prioridade` | enum | Sim | `"baixa"`, `"média"` ou `"alta"`. |
| `status` | enum | Sim | `"concluída"`, `"pendente"` ou `"cancelada"`. |
| `data_criacao` | datetime | Sim | Data/hora de criação (UTC). |
| `prazo` | datetime | Sim | Data-limite prevista para conclusão (UTC). |
| `data_inicio` | datetime | Não | Data/hora de início da execução (UTC). |
| `data_conclusao` | datetime | Não* | Obrigatória quando `status = "concluída"`. |

### 2.2 Saídas (`ResultadoAnalise`)

| Campo | Tipo | Descrição |
|---|---|---|
| `quantidade_tarefas` | int | Total de tarefas analisadas. |
| `tempo_medio_conclusao_horas` | float | Tempo médio (horas) das tarefas concluídas. |
| `taxa_atraso_percentual` | float | % de tarefas concluídas em atraso. |
| `indicadores_por_prioridade` | dict | Métricas acima, recalculadas por prioridade. |

### 2.3 Regras de Negócio

- Apenas tarefas com status `"concluída"` entram no cálculo de tempo
  médio.
- Tempo de conclusão = `data_conclusao − data_inicio`, em horas,
  arredondado a 2 casas decimais.
- Tarefa em atraso: `data_conclusao > prazo`.
- Datas inconsistentes (`data_conclusao` anterior a `data_inicio`, ou
  tarefa concluída sem `data_conclusao`) disparam `DataInvalidaError`.
- Ausência total de tarefas concluídas dispara
  `NenhumaTarefaConcluidaError` (evita divisão por zero).
- Todas as datas são interpretadas em UTC.
- Valores numéricos são arredondados a 2 casas decimais.

## 3. Cenários de Aceite (Dado–Quando–Então)

### Cenário 1 — Sucesso
- **Dado** um conjunto de tarefas válidas, com prioridades, prazos e
  status corretamente preenchidos.
- **Quando** o TaskAnalyzer for executado sobre esse conjunto.
- **Então** o sistema deve retornar as métricas corretas — tempo médio
  de conclusão, taxa de atraso e quantidade de tarefas — corretamente
  segmentadas por prioridade e de forma geral.

### Cenário 2 — Exceção / Erro
- **Dado** uma entrada com datas inválidas ou uma situação de divisão
  por zero (nenhuma tarefa concluída).
- **Quando** o TaskAnalyzer for executado sobre esse conjunto.
- **Então** o sistema deve disparar uma exceção específica e tratada,
  com mensagem clara e objetiva.

> Estes cenários são a fonte de verdade para `tests/test_harness.py` e
> não devem ser alterados, conforme `CONTEXT_RULES.md`.

## 4. Decisão de Design Documentada

Diferente do cálculo geral (que lança `NenhumaTarefaConcluidaError`
quando não há nenhuma tarefa concluída em todo o conjunto), o cálculo
por prioridade retorna métricas zeradas quando uma prioridade
específica não possui tarefas concluídas — pois trata-se de uma
segmentação normal dos dados, não de uma falha de entrada.
