"""Board evaluation functions for Chinese Chess AI.

This module provides evaluation functions for the AI, including:
- NNUE neural network evaluation (primary)
- Classical piece-square table evaluation (fallback)
- Material and positional evaluation

The evaluation system uses a hybrid approach:
- NNUE provides complex pattern recognition
- Classical evaluation provides baseline material counting

Typical usage example:
    score = evaluate_board(board, RED)
    depth = DIFFICULTY_DEPTHS['中级']
"""

from typing import Dict, Final

from core.board import Board
from core.constants import (
    BLACK,
    BOARD_COLS,
    BOARD_ROWS,
    PIECE_VALUES,
    RED,
    RIVER_ROW,
    get_piece_color,
)

from ai.nnue import nnue_evaluate, get_nnue_evaluator


# =============================================================================
# Difficulty Configuration
# =============================================================================
DIFFICULTY_DEPTHS: Final[Dict[str, int]] = {
    '小白': 2,
    '初级': 3,
    '中级': 4,
    '高级': 5,
    '大师': 6,
}


# =============================================================================
# Main Evaluation Function
# =============================================================================
def evaluate_board(board: Board, perspective_color: int) -> int:
    """Evaluate the board position from a player's perspective.

    This is the main evaluation function that uses NNUE for
    sophisticated position assessment.

    Args:
        board: The board state to evaluate.
        perspective_color: The color to evaluate for (RED or BLACK).

    Returns:
        Evaluation score. Positive indicates advantage, negative disadvantage.
        Score is in centipawns (100 = 1 pawn value).
    """
    return nnue_evaluate(board, perspective_color)


# =============================================================================
# Classical Evaluation (Fallback)
# =============================================================================
def classical_evaluate(board: Board, perspective_color: int) -> int:
    """Classical evaluation using material and piece-square tables.
    
    This is a simpler evaluation function that can be used as a
    fallback or for debugging purposes.

    Args:
        board: The board state to evaluate.
        perspective_color: The color to evaluate for (RED or BLACK).

    Returns:
        Evaluation score in centipawns.
    """
    evaluator = get_nnue_evaluator()
    return evaluator._classical_evaluate(board, perspective_color)


# =============================================================================
# Material Evaluation
# =============================================================================
def material_balance(board: Board) -> int:
    """Calculate pure material balance (Red - Black).

    Args:
        board: The board state.

    Returns:
        Material balance. Positive favors Red.
    """
    score = 0
    
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            piece = board.get_piece(row, col)
            if piece is None:
                continue
            
            value = PIECE_VALUES.get(piece, 0)
            color = get_piece_color(piece)
            
            # Add pawn crossing bonus
            piece_type = piece.upper()
            if piece_type == 'P':
                if color == RED and row > RIVER_ROW:
                    value += 100
                elif color == BLACK and row <= RIVER_ROW:
                    value += 100
            
            if color == RED:
                score += value
            else:
                score -= value
    
    return score


# =============================================================================
# Position Features (for analysis/debugging)
# =============================================================================
def count_pieces(board: Board, color: int) -> Dict[str, int]:
    """Count pieces for a given color.

    Args:
        board: The board state.
        color: The color to count pieces for.

    Returns:
        Dictionary mapping piece types to counts.
    """
    counts = {
        'K': 0, 'A': 0, 'B': 0, 'N': 0, 'R': 0, 'C': 0, 'P': 0
    }
    
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            piece = board.get_piece(row, col)
            if piece and get_piece_color(piece) == color:
                counts[piece.upper()] += 1
    
    return counts


def is_endgame(board: Board) -> bool:
    """Check if the position is in endgame phase.

    Endgame is defined as having limited major pieces remaining.

    Args:
        board: The board state.

    Returns:
        True if in endgame phase.
    """
    red_counts = count_pieces(board, RED)
    black_counts = count_pieces(board, BLACK)
    
    # Count major pieces (Rooks, Cannons, Knights)
    red_major = red_counts['R'] + red_counts['C'] + red_counts['N']
    black_major = black_counts['R'] + black_counts['C'] + black_counts['N']
    
    # Endgame if total major pieces <= 4
    return (red_major + black_major) <= 4


def king_safety(board: Board, color: int) -> int:
    """Evaluate king safety for a color.

    Args:
        board: The board state.
        color: The color to evaluate.

    Returns:
        King safety score (higher is safer).
    """
    score = 0
    
    # Find king position
    king_char = 'K' if color == RED else 'k'
    king_pos = None
    
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board.get_piece(row, col) == king_char:
                king_pos = (row, col)
                break
        if king_pos:
            break
    
    if king_pos is None:
        return -10000  # No king = very bad
    
    row, col = king_pos
    
    # Bonus for staying in center of palace
    if col == 4:  # Center column
        score += 10
    
    # Bonus for having advisors nearby
    for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        r, c = row + dr, col + dc
        if 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS:
            piece = board.get_piece(r, c)
            if piece and piece.upper() == 'A' and get_piece_color(piece) == color:
                score += 20
    
    # Penalty for exposed king (no pieces in front)
    direction = 1 if color == RED else -1
    exposed = True
    for i in range(1, 10):
        r = row + i * direction
        if 0 <= r < BOARD_ROWS:
            if board.get_piece(r, col):
                exposed = False
                break
    
    if exposed:
        score -= 30
    
    return score


# =============================================================================
# Re-export NNUE functions for convenience
# =============================================================================
__all__ = [
    'DIFFICULTY_DEPTHS',
    'evaluate_board',
    'classical_evaluate',
    'material_balance',
    'count_pieces',
    'is_endgame',
    'king_safety',
    'nnue_evaluate',
]
