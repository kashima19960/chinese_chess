"""Unified search interface for Chinese Chess AI.

This module provides a unified interface to the search engine,
maintaining backward compatibility with the existing codebase
while using the new high-performance NNUE + Alpha-Beta engine.

Typical usage example:
    best_move = get_best_move(board, '中级')
"""

from typing import Optional, Tuple

from core.board import Board

from ai.search_engine import search_best_move, get_search_engine, DIFFICULTY_CONFIG


# Re-export difficulty depths for compatibility
DIFFICULTY_DEPTHS = {
    '小白': 2,
    '初级': 3,
    '中级': 4,
    '高级': 5,
    '大师': 6,
}


def get_best_move(
    board: Board,
    difficulty: str = '中级'
) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """Get the best move for the current player.

    This function uses the new NNUE + Alpha-Beta search engine
    for improved play strength and performance.

    Args:
        board: Current board state.
        difficulty: Difficulty level ('小白', '初级', '中级', '高级', '大师').

    Returns:
        Best move as ((from_row, from_col), (to_row, to_col)),
        or None if no legal moves.
    """
    return search_best_move(board, difficulty)


def minimax_search(
    board: Board,
    depth: int,
    alpha: int = -999999,
    beta: int = 999999,
    maximizing: bool = True
) -> Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
    """Legacy minimax search interface.
    
    This function is maintained for backward compatibility.
    It now delegates to the new search engine.

    Args:
        board: Current board state.
        depth: Search depth.
        alpha: Alpha value for pruning.
        beta: Beta value for pruning.
        maximizing: Whether this is a maximizing node.

    Returns:
        Tuple of (evaluation_score, best_move).
    """
    engine = get_search_engine()
    best_move = engine.search(board, depth=depth)
    
    # Get evaluation score from the engine's stats
    # Note: The new engine uses NNUE evaluation
    from ai.nnue import nnue_evaluate
    score = nnue_evaluate(board, board.current_player)
    
    return score, best_move
