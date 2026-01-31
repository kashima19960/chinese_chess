"""AI engine for Chinese Chess.

This package provides AI functionality including board evaluation,
minimax search with alpha-beta pruning, and threaded computation.

Modules:
    evaluation: Board evaluation and position-square tables.
    search: Minimax search algorithm.
    worker: QThread worker for async AI computation.
"""

from ai.evaluation import DIFFICULTY_DEPTHS, evaluate_board
from ai.search import get_best_move, minimax_search
from ai.worker import AIWorker

__all__ = [
    'AIWorker',
    'DIFFICULTY_DEPTHS',
    'evaluate_board',
    'get_best_move',
    'minimax_search',
]
