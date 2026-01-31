"""Board evaluation functions for AI.

This module provides evaluation functions and position-square tables
for the AI to assess board positions.

Typical usage example:
    score = evaluate_board(board, RED)
    depth = DIFFICULTY_DEPTHS['中级']
"""

from typing import Dict, List

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

# ===========================
# 难度等级对应的搜索深度
# ===========================
DIFFICULTY_DEPTHS: Dict[str, int] = {
    '小白': 1,
    '初级': 2,
    '中级': 3,
    '高级': 4,
    '大师': 5,
}

# ===========================
# 位置价值表 (Position Square Tables)
# ===========================
# 兵/卒的位置价值
PAWN_PST_RED = [
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  -2, 0,  3,  0,  -2, 0,  0],
    [2,  0,  8,  0,  8,  0,  8,  0,  2],
    [6,  12, 18, 18, 20, 18, 18, 12, 6],
    [10, 20, 30, 34, 40, 34, 30, 20, 10],
    [14, 26, 42, 60, 80, 60, 42, 26, 14],
    [18, 36, 56, 80, 120, 80, 56, 36, 18],
    [0,  3,  6,  9,  12, 9,  6,  3,  0],
]

# 马的位置价值
KNIGHT_PST = [
    [0,  -3, 5,  4,  2,  4,  5,  -3, 0],
    [-3, 2,  4,  6,  10, 6,  4,  2,  -3],
    [4,  6,  10, 15, 16, 15, 10, 6,  4],
    [2,  10, 13, 14, 15, 14, 13, 10, 2],
    [2,  12, 11, 15, 16, 15, 11, 12, 2],
    [0,  5,  13, 12, 12, 12, 13, 5,  0],
    [-3, 2,  5,  5,  5,  5,  5,  2,  -3],
    [0,  -5, 2,  4,  2,  4,  2,  -5, 0],
    [-8, 2,  4,  -5, -4, -5, 4,  2,  -8],
    [0,  -4, 0,  0,  0,  0,  0,  -4, 0],
]

# 炮的位置价值
CANNON_PST = [
    [0,  0,  1,  0,  -1, 0,  1,  0,  0],
    [0,  1,  0,  0,  0,  0,  0,  1,  0],
    [1,  0,  4,  3,  4,  3,  4,  0,  1],
    [3,  2,  3,  4,  3,  4,  3,  2,  3],
    [3,  2,  5,  4,  6,  4,  5,  2,  3],
    [3,  4,  6,  7,  6,  7,  6,  4,  3],
    [2,  3,  4,  4,  3,  4,  4,  3,  2],
    [0,  0,  0,  1,  1,  1,  0,  0,  0],
    [-1, 1,  1,  1,  0,  1,  1,  1,  -1],
    [0,  0,  0,  2,  4,  2,  0,  0,  0],
]

# 车的位置价值
ROOK_PST = [
    [-2, 10, 6,  14, 12, 14, 6,  10, -2],
    [8,  4,  8,  16, 8,  16, 8,  4,  8],
    [4,  8,  6,  14, 12, 14, 6,  8,  4],
    [6,  10, 8,  14, 14, 14, 8,  10, 6],
    [12, 16, 14, 20, 20, 20, 14, 16, 12],
    [12, 14, 12, 18, 18, 18, 12, 14, 12],
    [12, 18, 16, 22, 22, 22, 16, 18, 12],
    [12, 12, 12, 18, 18, 18, 12, 12, 12],
    [16, 20, 18, 24, 26, 24, 18, 20, 16],
    [14, 14, 12, 18, 16, 18, 12, 14, 14],
]

# 将/帅的位置价值
KING_PST_RED = [
    [0,  0,  0,  8,  9,  8,  0,  0,  0],
    [0,  0,  0,  8,  8,  8,  0,  0,  0],
    [0,  0,  0,  9,  9,  9,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
]

# 仕/士的位置价值
ADVISOR_PST_RED = [
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  2,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
]

# 相/象的位置价值
BISHOP_PST_RED = [
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [-2, 0,  0,  0,  3,  0,  0,  0,  -2],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  3,  0,  0,  0,  3,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
]


def _flip_pst(pst: List[List[int]]) -> List[List[int]]:
    """Flip a position-square table for the opposite color.

    Args:
        pst: The position-square table to flip.

    Returns:
        Flipped position-square table.
    """
    return [row[:] for row in reversed(pst)]


# Black's position-square tables (flipped from red)
PAWN_PST_BLACK = _flip_pst(PAWN_PST_RED)
KING_PST_BLACK = _flip_pst(KING_PST_RED)
ADVISOR_PST_BLACK = _flip_pst(ADVISOR_PST_RED)
BISHOP_PST_BLACK = _flip_pst(BISHOP_PST_RED)


def get_position_value(piece: str, row: int, col: int) -> int:
    """Get the positional value for a piece at a given location.

    Args:
        piece: The piece character.
        row: Board row.
        col: Board column.

    Returns:
        Positional value bonus.
    """
    piece_type = piece.upper()
    color = get_piece_color(piece)
    
    if piece_type == 'P':
        pst = PAWN_PST_RED if color == RED else PAWN_PST_BLACK
        return pst[row][col]
    elif piece_type == 'N':
        return KNIGHT_PST[row][col]
    elif piece_type == 'C':
        return CANNON_PST[row][col]
    elif piece_type == 'R':
        return ROOK_PST[row][col]
    elif piece_type == 'K':
        pst = KING_PST_RED if color == RED else KING_PST_BLACK
        return pst[row][col]
    elif piece_type == 'A':
        pst = ADVISOR_PST_RED if color == RED else ADVISOR_PST_BLACK
        return pst[row][col]
    elif piece_type == 'B':
        pst = BISHOP_PST_RED if color == RED else BISHOP_PST_BLACK
        return pst[row][col]
    
    return 0


def evaluate_board(board: Board, perspective_color: int) -> int:
    """Evaluate the board position from a player's perspective.

    Args:
        board: The board state to evaluate.
        perspective_color: The color to evaluate for (RED or BLACK).

    Returns:
        Evaluation score. Positive indicates advantage, negative disadvantage.
    """
    score = 0
    
    # 遍历所有棋子
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            piece = board.get_piece(row, col)
            if not piece:
                continue
            
            color = get_piece_color(piece)
            piece_type = piece.upper()
            
            # 材质价值
            material_value = PIECE_VALUES[piece]
            
            # 兵过河加倍
            if piece_type == 'P':
                if color == RED and row > RIVER_ROW:
                    material_value = 200
                elif color == BLACK and row < RIVER_ROW + 1:
                    material_value = 200
            
            # 位置价值
            position_value = get_position_value(piece, row, col)
            
            # 总价值
            piece_value = material_value + position_value
            
            # 根据视角和颜色调整符号
            if color == perspective_color:
                score += piece_value
            else:
                score -= piece_value
    
    return score
