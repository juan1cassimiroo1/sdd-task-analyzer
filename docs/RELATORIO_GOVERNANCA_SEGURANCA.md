# Relatório de Governança, Segurança e Revisão Ética — TaskAnalyzer

**Autor:** Juan Conceição Cassimiro — Ciências da Computação — Turma A - 0726 (CEUB)
**Fase:** 3 — DevOps, Testes e Revisão Ética
**Data:** Fase 3, Bootcamp III

## 1. Objetivo

Este relatório documenta a revisão crítica do processo de desenvolvimento
assistido por IA do módulo TaskAnalyzer, cobrindo riscos de alucinação,
aderência ao contrato, segurança, privacidade e responsabilidade humana
no ciclo de homologação.

## 2. Análise de Alucinações e Desvios da IA

Durante a geração do código na Fase 2, os seguintes riscos de
"alucinação" (comportamento não especificado ou incorreto) foram
observados e mitigados antes da homologação:

| Risco identificado | Mitigação aplicada |
|---|---|
| Calcular tempo médio de conclusão mesmo sem nenhuma tarefa concluída (divisão por zero silenciosa) | Implementada exceção específica `NenhumaTarefaConcluidaError`, conforme Cenário 2 de aceite. |
| Aceitar tarefas com `data_conclusao` anterior a `data_inicio` sem validação | Validação explícita em `_validar_tarefa`, lançando `DataInvalidaError`. |
| Ambiguidade sobre o que fazer quando uma prioridade não tem tarefas concluídas | Decisão de design documentada explicitamente em `specs/task_analyzer_spec.md` (retorna métricas zeradas, não lança exceção — decisão humana, não assumida pela IA). |
| Uso de bibliotecas não previstas no contrato | Nenhuma biblioteca externa foi utilizada em `src/`; apenas `pytest` como dependência de desenvolvimento, autorizada em `CONTEXT_RULES.md`. |

Nenhum código gerado foi aceito sem que o comportamento fosse
primeiro coberto por um teste automatizado correspondente, reduzindo o
risco de comportamento não verificado entrar em produção.

## 3. Aderência ao Contrato e às CONTEXT_RULES

Checklist de conformidade (verificado manualmente antes de cada commit):

- [x] Python 3.11+ (imagem Docker usa `python:3.11-slim`; CI testa 3.11 e 3.12).
- [x] Type hints em 100% das funções e métodos públicos e privados.
- [x] Docstrings no padrão Google style em todos os módulos, classes e funções.
- [x] Funções pequenas, coesas e com responsabilidade única (SRP).
- [x] Nenhuma persistência de dados em arquivo ou banco.
- [x] Nenhuma alteração na assinatura de `analisar_tarefas`.
- [x] Nenhuma alteração nos cenários de teste originais da Fase 1.
- [x] 100% dos testes automatizados passando antes de cada merge (10/10).

## 4. Segurança e Privacidade de Dados (LGPD)

- O módulo **não persiste, não transmite e não armazena** dados fora da
  memória do processo em execução — não há banco de dados, arquivo de
  log de dados de negócio, nem chamadas de rede.
- Os únicos dados tratados são os campos definidos no contrato
  (`id_tarefa`, `titulo`, datas, prioridade, status). Recomenda-se que,
  em uso real, o campo `titulo` não contenha dados pessoais sensíveis,
  já que o módulo não realiza nenhuma anonimização.
- A imagem Docker executa como usuário não-root (`appuser`), reduzindo
  a superfície de risco em caso de execução em ambiente compartilhado.
- O pipeline de CI/CD roda em ambiente efêmero (GitHub Actions), sem
  persistir segredos ou dados de teste entre execuções.

## 5. Vieses e Limitações

- As categorias de prioridade (baixa, média, alta) são tratadas de
  forma simétrica pelo algoritmo — nenhuma prioridade recebe peso ou
  tratamento privilegiado nos cálculos, evitando viés algorítmico.
- Limitação conhecida: o módulo assume que todas as datas fornecidas
  já estão em UTC; não há conversão automática de fuso horário, o que
  deve ser tratado por quem integrar o módulo.
- Limitação conhecida: tarefas cujo `status` é `"cancelada"` são
  ignoradas nas métricas de tempo e atraso, mas contam para
  `quantidade_tarefas` quando agregadas por prioridade — comportamento
  intencional, não uma falha.

## 6. Transparência e Auditabilidade

- Rastreabilidade completa entre cenário de aceite → caso de teste →
  linha de código: cada cenário da especificação tem pelo menos um
  teste automatizado correspondente em `tests/test_harness.py`.
- Logs estruturados via módulo `logging` registram o início e o fim de
  cada análise, além de alertas quando nenhuma tarefa concluída é
  encontrada.
- Histórico de versionamento (Git) preserva a evolução completa:
  commits pequenos, branches `feature/*` isoladas, merges via Pull
  Request e tags de release (`v0.2.0`, `v0.3.0`).

## 7. Responsabilidade Humana no Ciclo de Homologação

Em nenhuma etapa o código gerado por IA foi commitado diretamente sem
passar pelas cinco etapas do plano de homologação definido em
`CONTEXT_RULES.md`: (1) execução de testes, (2) revisão de
conformidade com o contrato, (3) análise de qualidade de código, (4)
testes manuais complementares e (5) aprovação humana final antes do
commit. A IA atuou como ferramenta de geração; a decisão técnica final
permaneceu sempre humana.

## 8. Conclusão

O módulo TaskAnalyzer, em sua versão homologada, atende integralmente
ao contrato de negócio definido na Fase 1, não apresenta persistência
ou tratamento inadequado de dados, e possui cobertura de testes para
os dois cenários de aceite especificados, incluindo casos de borda
adicionais. O pipeline de CI/CD garante que nenhuma alteração futura
seja integrada sem validação automatizada equivalente.
