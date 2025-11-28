"""
Board evaluation functions for AI.
"""

from typing import Dict
import sys
sys.path.append('..')

from core.constants import *
from core.board import Board

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


def _flip_pst(pst: list[list[int]]) -> list[list[int]]:
    """翻转位置价值表(用于黑方)"""
    return [row[:] for row in reversed(pst)]


# 黑方的位置价值表(翻转红方的)
PAWN_PST_BLACK = _flip_pst(PAWN_PST_RED)
KING_PST_BLACK = _flip_pst(KING_PST_RED)
ADVISOR_PST_BLACK = _flip_pst(ADVISOR_PST_RED)
BISHOP_PST_BLACK = _flip_pst(BISHOP_PST_RED)


def get_position_value(piece: str, row: int, col: int) -> int:
    """
    获取棋子在指定位置的位置价值
    
    Args:
        piece: 棋子类型
        row, col: 位置
    
    Returns:
        位置价值
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
    """
    评估棋盘局势
    
    Args:
        board: 棋盘状态
        perspective_color: 评估视角(RED或BLACK)
    
    Returns:
        评估分数,正数表示有利,负数表示不利
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
