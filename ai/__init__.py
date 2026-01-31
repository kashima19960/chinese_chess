"""AI engine for Chinese Chess.

This package provides AI functionality including:
- NNUE neural network evaluation
- High-performance Alpha-Beta search with modern optimizations
- Threaded computation for responsive UI

Modules:
    nnue: NNUE (Efficiently Updatable Neural Network) evaluation.
    search_engine: High-performance search with TT, LMR, null move pruning.
    evaluation: Board evaluation interface and utilities.
    search: Unified search interface.
    worker: QThread worker for async AI computation.

Architecture:
    The AI uses a two-layer approach:
    1. NNUE for sophisticated position evaluation
    2. Alpha-Beta search with modern pruning techniques

Key Features:
    - Transposition Table with Zobrist hashing
    - Principal Variation Search (PVS)
    - Late Move Reductions (LMR)
    - Null Move Pruning
    - Quiescence Search
    - Killer Move and History Heuristics
    - Aspiration Windows
    - Iterative Deepening
"""

from ai.evaluation import DIFFICULTY_DEPTHS, evaluate_board
from ai.search import get_best_move, minimax_search
from ai.search_engine import SearchEngine, get_search_engine, search_best_move
from ai.nnue import NNUEEvaluator, nnue_evaluate, get_nnue_evaluator
from ai.worker import AIWorker

__all__ = [
    # Worker
    'AIWorker',
    
    # Search
    'SearchEngine',
    'get_search_engine',
    'search_best_move',
    'get_best_move',
    'minimax_search',
    
    # Evaluation
    'NNUEEvaluator',
    'nnue_evaluate',
    'get_nnue_evaluator',
    'evaluate_board',
    'DIFFICULTY_DEPTHS',
]
