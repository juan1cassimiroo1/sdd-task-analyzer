# CONTEXT_RULES — TaskAnalyzer

Este arquivo é a fonte de verdade fornecida a qualquer assistente de IA
que gere ou modifique código neste repositório. Ele complementa o
contrato de negócio definido em `specs/task_analyzer_spec.md`.

## 1. Diretrizes Arquiteturais (Obrigatórias)

- Python 3.11+ como versão mínima obrigatória.
- Utilizar type hints (anotações de tipo) em todas as funções e métodos.
- Seguir o princípio Single Responsibility (SRP) e código limpo (PEP 8).
- Documentação formal no padrão Google style docstrings em módulos,
  classes, funções e parâmetros.
- Funções devem ser pequenas, coesas e com um único propósito.
- Tratamento de exceções específico e com mensagens claras.
- Logs estruturados utilizando o módulo padrão `logging`.
- Código legível, manutenível e com nomes de variáveis e funções
  descritivos.

## 2. Proibições Explícitas (Regras Restritivas)

- Não utilizar bibliotecas externas não autorizadas (apenas `pytest`
  como dependência de desenvolvimento é permitido).
- Não alterar, remover ou adaptar os cenários de teste fornecidos em
  `tests/test_harness.py`.
- Não modificar a estrutura de pastas definida nesta especificação.
- Não persistir dados em arquivos ou bancos de dados.
- Não alterar a assinatura (nome e parâmetros) das funções públicas
  sem autorização — em especial `analisar_tarefas`.
- Não gerar código sem testes correspondentes para as novas
  funcionalidades.
- Não inserir código duplicado ou sem necessidade.
- Não assumir comportamentos não especificados no contrato de negócio.

## 3. Regras de Interação com a IA

- Fornecer sempre o contexto completo (especificação, cenários e
  regras) antes de solicitar geração de código.
- Validar se a IA compreendeu o contrato antes de aceitar a solução
  proposta.
- Solicitar explicações à IA sempre que houver ambiguidade na solução
  apresentada.
- Revisar criticamente todo código gerado antes de qualquer commit.
- Rejeitar e solicitar nova geração sempre que a resposta violar as
  proibições ou o contrato definido.

## 4. Plano de Homologação Humana

Todo código gerado pela IA passa pelas seguintes etapas antes de ser
aceito e versionado:

1. Execução completa dos testes automatizados (`pytest`) para
   validação funcional.
2. Revisão de conformidade com o contrato de negócio e com estas
   CONTEXT_RULES.
3. Análise de qualidade de código, legibilidade, tratamento de erros
   e aderência aos padrões definidos.
4. Testes manuais complementares em casos de borda.
5. Somente após aprovação, o código é commitado no repositório.
