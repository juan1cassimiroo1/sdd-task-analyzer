"""Módulo de análise de tarefas e produtividade (TaskAnalyzer).

Este módulo implementa o contrato executável definido em
``specs/task_analyzer_spec.md`` (Fase 1 — SDD). Ele calcula, a partir de
uma lista de tarefas em memória, três indicadores de produtividade:

    * Tempo médio de conclusão (em horas).
    * Taxa de atraso (percentual de tarefas concluídas após o prazo).
    * Indicadores agregados por prioridade (baixa, média, alta).

O módulo não realiza persistência de dados, não expõe interface gráfica
e não se comunica com serviços externos, conforme as CONTEXT_RULES.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Exceções específicas (tratamento de erros claro e objetivo)
# --------------------------------------------------------------------------


class TaskAnalyzerError(Exception):
    """Exceção base para todos os erros do módulo TaskAnalyzer."""


class TaskValidationError(TaskAnalyzerError):
    """Exceção base para entradas que violam o contrato de negócio.

    Agrupa os erros de validação (identificador, datas e ausência de
    tarefas concluídas), permitindo que o chamador trate qualquer falha
    de contrato com um único ``except TaskValidationError``.
    """


class IdentificadorInvalidoError(TaskValidationError):
    """Levantada quando ``id_tarefa`` é menor ou igual a zero."""


class DataInvalidaError(TaskValidationError):
    """Levantada quando as datas de uma tarefa são inconsistentes.

    Ocorre, por exemplo, quando ``data_conclusao`` é anterior a
    ``data_inicio``, ou quando uma tarefa concluída não possui
    ``data_inicio`` ou ``data_conclusao`` preenchida.
    """


class NenhumaTarefaConcluidaError(TaskValidationError):
    """Levantada quando não há tarefas concluídas para calcular métricas.

    Evita divisão por zero no cálculo de tempo médio de conclusão e de
    taxa de atraso.
    """


# --------------------------------------------------------------------------
# Modelos de dados (entradas e saídas do contrato)
# --------------------------------------------------------------------------


class Prioridade(str, Enum):
    """Valores aceitos para a prioridade de uma tarefa."""

    BAIXA = "baixa"
    MEDIA = "média"
    ALTA = "alta"


class StatusTarefa(str, Enum):
    """Valores aceitos para o status de uma tarefa."""

    CONCLUIDA = "concluída"
    PENDENTE = "pendente"
    CANCELADA = "cancelada"


@dataclass(frozen=True)
class Tarefa:
    """Representa uma tarefa de entrada, conforme o contrato (seção 1.3.1).

    Attributes:
        id_tarefa: Identificador único da tarefa (> 0).
        titulo: Título ou descrição curta da tarefa.
        prioridade: Prioridade da tarefa (baixa, média ou alta).
        status: Status atual da tarefa.
        data_criacao: Data/hora de criação da tarefa (UTC).
        prazo: Data-limite prevista para conclusão (UTC).
        data_inicio: Data/hora de início da execução (UTC), opcional.
        data_conclusao: Data/hora de conclusão (UTC). Obrigatória quando
            ``status`` é ``StatusTarefa.CONCLUIDA``.
    """

    id_tarefa: int
    titulo: str
    prioridade: Prioridade
    status: StatusTarefa
    data_criacao: datetime
    prazo: datetime
    data_inicio: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None


@dataclass(frozen=True)
class IndicadorPrioridade:
    """Métricas agregadas para um grupo de tarefas de mesma prioridade.

    Attributes:
        quantidade_tarefas: Total de tarefas naquela prioridade.
        tempo_medio_conclusao_horas: Tempo médio de conclusão (horas).
        taxa_atraso_percentual: Percentual de tarefas concluídas em atraso.
    """

    quantidade_tarefas: int
    tempo_medio_conclusao_horas: float
    taxa_atraso_percentual: float


@dataclass(frozen=True)
class ResultadoAnalise:
    """Saída consolidada do TaskAnalyzer (contrato, seção 1.3.2).

    Attributes:
        quantidade_tarefas: Total de tarefas analisadas na entrada.
        tempo_medio_conclusao_horas: Tempo médio de conclusão geral (horas).
        taxa_atraso_percentual: Taxa de atraso geral (percentual).
        indicadores_por_prioridade: Métricas recalculadas por prioridade.
    """

    quantidade_tarefas: int
    tempo_medio_conclusao_horas: float
    taxa_atraso_percentual: float
    indicadores_por_prioridade: dict[str, IndicadorPrioridade] = field(
        default_factory=dict
    )


# --------------------------------------------------------------------------
# Validação (regras de negócio, seção 1.3.3)
# --------------------------------------------------------------------------


def _validar_tarefa(tarefa: Tarefa) -> None:
    """Valida os dados de uma tarefa antes do processamento.

    Args:
        tarefa: Tarefa a ser validada.

    Raises:
        IdentificadorInvalidoError: Se ``id_tarefa`` não for maior que zero.
        DataInvalidaError: Se as datas da tarefa forem inconsistentes.
    """
    if tarefa.id_tarefa <= 0:
        raise IdentificadorInvalidoError(
            f"id_tarefa inválido ({tarefa.id_tarefa}): deve ser > 0."
        )

    if tarefa.status == StatusTarefa.CONCLUIDA:
        if tarefa.data_conclusao is None:
            raise DataInvalidaError(
                f"Tarefa {tarefa.id_tarefa}: status 'concluída' exige "
                "data_conclusao preenchida."
            )
        if tarefa.data_inicio is None:
            raise DataInvalidaError(
                f"Tarefa {tarefa.id_tarefa}: status 'concluída' exige "
                "data_inicio preenchida para calcular o tempo de conclusão."
            )
        if tarefa.data_conclusao < tarefa.data_inicio:
            raise DataInvalidaError(
                f"Tarefa {tarefa.id_tarefa}: data_conclusao anterior a "
                "data_inicio."
            )


# --------------------------------------------------------------------------
# Cálculos (funções pequenas, coesas e com um único propósito)
# --------------------------------------------------------------------------


def _tarefas_concluidas(tarefas: list[Tarefa]) -> list[Tarefa]:
    """Filtra apenas as tarefas com status concluída."""
    return [t for t in tarefas if t.status == StatusTarefa.CONCLUIDA]


def _tempo_conclusao_horas(tarefa: Tarefa) -> float:
    """Calcula o tempo de conclusão de uma tarefa concluída, em horas.

    Requer que ``data_inicio`` e ``data_conclusao`` estejam preenchidas;
    essa condição é garantida por ``_validar_tarefa`` antes do cálculo.
    """
    delta = tarefa.data_conclusao - tarefa.data_inicio  # type: ignore[operator]
    return round(delta.total_seconds() / 3600, 2)


def _tarefa_em_atraso(tarefa: Tarefa) -> bool:
    """Indica se uma tarefa concluída foi finalizada após o prazo."""
    return tarefa.data_conclusao > tarefa.prazo  # type: ignore[operator]


def _calcular_tempo_medio(tarefas_concluidas: list[Tarefa]) -> float:
    """Calcula o tempo médio de conclusão (horas) de uma lista de tarefas.

    Raises:
        NenhumaTarefaConcluidaError: Se a lista estiver vazia.
    """
    if not tarefas_concluidas:
        raise NenhumaTarefaConcluidaError(
            "Não há tarefas concluídas para calcular o tempo médio."
        )
    tempos = [_tempo_conclusao_horas(t) for t in tarefas_concluidas]
    return round(sum(tempos) / len(tempos), 2)


def _calcular_taxa_atraso(tarefas_concluidas: list[Tarefa]) -> float:
    """Calcula o percentual de tarefas concluídas em atraso.

    Raises:
        NenhumaTarefaConcluidaError: Se a lista estiver vazia.
    """
    if not tarefas_concluidas:
        raise NenhumaTarefaConcluidaError(
            "Não há tarefas concluídas para calcular a taxa de atraso."
        )
    em_atraso = sum(1 for t in tarefas_concluidas if _tarefa_em_atraso(t))
    return round((em_atraso / len(tarefas_concluidas)) * 100, 2)


def _calcular_indicador_prioridade(
    tarefas: list[Tarefa], prioridade: Prioridade
) -> IndicadorPrioridade:
    """Calcula as métricas agregadas para uma prioridade específica.

    Diferente do cálculo geral, aqui a ausência de tarefas concluídas
    naquela prioridade não é um erro: retorna métricas zeradas, pois é
    uma situação normal de segmentação dos dados.
    """
    tarefas_prioridade = [t for t in tarefas if t.prioridade == prioridade]
    concluidas = _tarefas_concluidas(tarefas_prioridade)

    if not concluidas:
        return IndicadorPrioridade(
            quantidade_tarefas=len(tarefas_prioridade),
            tempo_medio_conclusao_horas=0.0,
            taxa_atraso_percentual=0.0,
        )

    return IndicadorPrioridade(
        quantidade_tarefas=len(tarefas_prioridade),
        tempo_medio_conclusao_horas=_calcular_tempo_medio(concluidas),
        taxa_atraso_percentual=_calcular_taxa_atraso(concluidas),
    )


# --------------------------------------------------------------------------
# Função pública principal (ponto de entrada do contrato)
# --------------------------------------------------------------------------


def analisar_tarefas(tarefas: list[Tarefa]) -> ResultadoAnalise:
    """Analisa uma lista de tarefas e retorna métricas de produtividade.

    Args:
        tarefas: Lista de tarefas a serem analisadas.

    Returns:
        ResultadoAnalise contendo as métricas gerais e por prioridade.

    Raises:
        IdentificadorInvalidoError: Se alguma tarefa tiver id_tarefa <= 0.
        DataInvalidaError: Se alguma tarefa tiver datas inconsistentes.
        NenhumaTarefaConcluidaError: Se não houver tarefas concluídas.
    """
    logger.info("Iniciando análise de %d tarefa(s).", len(tarefas))

    for tarefa in tarefas:
        _validar_tarefa(tarefa)

    concluidas = _tarefas_concluidas(tarefas)
    if not concluidas:
        logger.warning("Nenhuma tarefa concluída encontrada na entrada.")
        raise NenhumaTarefaConcluidaError(
            "Não é possível calcular métricas: nenhuma tarefa concluída "
            "no conjunto de entrada."
        )

    resultado = ResultadoAnalise(
        quantidade_tarefas=len(tarefas),
        tempo_medio_conclusao_horas=_calcular_tempo_medio(concluidas),
        taxa_atraso_percentual=_calcular_taxa_atraso(concluidas),
        indicadores_por_prioridade={
            prioridade.value: _calcular_indicador_prioridade(tarefas, prioridade)
            for prioridade in Prioridade
        },
    )

    logger.info("Análise concluída com sucesso.")
    return resultado
