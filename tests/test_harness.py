"""Testes automatizados do TaskAnalyzer.

Cada teste está diretamente rastreado a um cenário de aceite ou a uma
regra de negócio definida em ``specs/task_analyzer_spec.md`` (Fase 1).
Os cenários de aceite fornecidos NÃO são alterados, conforme as
CONTEXT_RULES — apenas decompostos em casos de teste concretos.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.task_analyzer import (
    DataInvalidaError,
    IdentificadorInvalidoError,
    NenhumaTarefaConcluidaError,
    Prioridade,
    StatusTarefa,
    Tarefa,
    analisar_tarefas,
)

UTC = timezone.utc


# --------------------------------------------------------------------------
# Fixtures — dados de apoio
# --------------------------------------------------------------------------


def _tarefa_concluida(
    id_tarefa: int,
    prioridade: Prioridade,
    horas_execucao: float,
    em_atraso: bool,
) -> Tarefa:
    """Cria uma tarefa concluída válida, com controle de atraso e duração."""
    criacao = datetime(2026, 1, 1, tzinfo=UTC)
    inicio = criacao + timedelta(hours=1)
    conclusao = inicio + timedelta(hours=horas_execucao)
    prazo = conclusao - timedelta(hours=1) if em_atraso else conclusao + timedelta(hours=1)
    return Tarefa(
        id_tarefa=id_tarefa,
        titulo=f"Tarefa {id_tarefa}",
        prioridade=prioridade,
        status=StatusTarefa.CONCLUIDA,
        data_criacao=criacao,
        prazo=prazo,
        data_inicio=inicio,
        data_conclusao=conclusao,
    )


@pytest.fixture
def conjunto_valido() -> list[Tarefa]:
    """Conjunto de tarefas válidas cobrindo as três prioridades.

    - 2 tarefas de prioridade alta: 1 no prazo, 1 em atraso.
    - 1 tarefa de prioridade média: no prazo.
    - 1 tarefa de prioridade baixa: no prazo.
    """
    return [
        _tarefa_concluida(1, Prioridade.ALTA, horas_execucao=10, em_atraso=False),
        _tarefa_concluida(2, Prioridade.ALTA, horas_execucao=20, em_atraso=True),
        _tarefa_concluida(3, Prioridade.MEDIA, horas_execucao=5, em_atraso=False),
        _tarefa_concluida(4, Prioridade.BAIXA, horas_execucao=8, em_atraso=False),
    ]


# --------------------------------------------------------------------------
# Cenário 1 (Sucesso) — especificação seção 2.1
# --------------------------------------------------------------------------


class TestCenario1Sucesso:
    """Dado um conjunto de tarefas válidas, quando o TaskAnalyzer for
    executado, então deve retornar as métricas corretas."""

    def test_quantidade_total_de_tarefas(self, conjunto_valido: list[Tarefa]) -> None:
        resultado = analisar_tarefas(conjunto_valido)
        assert resultado.quantidade_tarefas == 4

    def test_tempo_medio_conclusao_geral(self, conjunto_valido: list[Tarefa]) -> None:
        resultado = analisar_tarefas(conjunto_valido)
        # (10 + 20 + 5 + 8) / 4 = 10.75
        assert resultado.tempo_medio_conclusao_horas == 10.75

    def test_taxa_atraso_geral(self, conjunto_valido: list[Tarefa]) -> None:
        resultado = analisar_tarefas(conjunto_valido)
        # 1 em atraso de 4 concluídas = 25.0%
        assert resultado.taxa_atraso_percentual == 25.0

    def test_indicadores_por_prioridade_alta(
        self, conjunto_valido: list[Tarefa]
    ) -> None:
        resultado = analisar_tarefas(conjunto_valido)
        indicador_alta = resultado.indicadores_por_prioridade["alta"]
        assert indicador_alta.quantidade_tarefas == 2
        assert indicador_alta.tempo_medio_conclusao_horas == 15.0
        assert indicador_alta.taxa_atraso_percentual == 50.0

    def test_indicadores_por_prioridade_sem_tarefas(
        self, conjunto_valido: list[Tarefa]
    ) -> None:
        """Prioridade sem tarefas concluídas retorna métricas zeradas,
        sem lançar exceção (decisão de design documentada no README)."""
        resultado = analisar_tarefas(
            [_tarefa_concluida(1, Prioridade.ALTA, 5, em_atraso=False)]
        )
        indicador_media = resultado.indicadores_por_prioridade["média"]
        assert indicador_media.quantidade_tarefas == 0
        assert indicador_media.tempo_medio_conclusao_horas == 0.0
        assert indicador_media.taxa_atraso_percentual == 0.0


# --------------------------------------------------------------------------
# Cenário 2 (Exceção/Erro) — especificação seção 2.1
# --------------------------------------------------------------------------


class TestCenario2ExcecaoErro:
    """Dado uma entrada com datas inválidas ou divisão por zero, quando o
    TaskAnalyzer for executado, então deve disparar uma exceção
    específica e tratada."""

    def test_data_conclusao_anterior_a_data_inicio(self) -> None:
        criacao = datetime(2026, 1, 1, tzinfo=UTC)
        tarefa_invalida = Tarefa(
            id_tarefa=1,
            titulo="Tarefa com datas inconsistentes",
            prioridade=Prioridade.ALTA,
            status=StatusTarefa.CONCLUIDA,
            data_criacao=criacao,
            prazo=criacao + timedelta(days=1),
            data_inicio=criacao + timedelta(hours=5),
            data_conclusao=criacao + timedelta(hours=1),
        )
        with pytest.raises(DataInvalidaError):
            analisar_tarefas([tarefa_invalida])

    def test_tarefa_concluida_sem_data_conclusao(self) -> None:
        criacao = datetime(2026, 1, 1, tzinfo=UTC)
        tarefa_invalida = Tarefa(
            id_tarefa=2,
            titulo="Tarefa concluída sem data_conclusao",
            prioridade=Prioridade.MEDIA,
            status=StatusTarefa.CONCLUIDA,
            data_criacao=criacao,
            prazo=criacao + timedelta(days=1),
            data_inicio=criacao,
            data_conclusao=None,
        )
        with pytest.raises(DataInvalidaError):
            analisar_tarefas([tarefa_invalida])

    def test_nenhuma_tarefa_concluida_gera_excecao(self) -> None:
        criacao = datetime(2026, 1, 1, tzinfo=UTC)
        tarefa_pendente = Tarefa(
            id_tarefa=3,
            titulo="Tarefa ainda pendente",
            prioridade=Prioridade.BAIXA,
            status=StatusTarefa.PENDENTE,
            data_criacao=criacao,
            prazo=criacao + timedelta(days=1),
        )
        with pytest.raises(NenhumaTarefaConcluidaError):
            analisar_tarefas([tarefa_pendente])

    def test_lista_vazia_gera_excecao(self) -> None:
        with pytest.raises(NenhumaTarefaConcluidaError):
            analisar_tarefas([])

    def test_id_tarefa_invalido(self) -> None:
        criacao = datetime(2026, 1, 1, tzinfo=UTC)
        tarefa_invalida = Tarefa(
            id_tarefa=0,
            titulo="Tarefa com id inválido",
            prioridade=Prioridade.ALTA,
            status=StatusTarefa.PENDENTE,
            data_criacao=criacao,
            prazo=criacao + timedelta(days=1),
        )
        with pytest.raises(IdentificadorInvalidoError):
            analisar_tarefas([tarefa_invalida])
