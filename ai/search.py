"""
Minimax search algorithm with alpha-beta pruning.
"""

from typing import Optional, Tuple
import sys
sys.path.append('..')

from core.board import Board
from core.rules import RuleEngine
from core.constants import RED, BLACK
from .evaluation import evaluate_board


def minimax_search(
    board: Board,
    depth: int,
    alpha: int = -999999,
    beta: int = 999999,
    maximizing: bool = True
) -> Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
    """
    Minimax搜索算法(带Alpha-Beta剪枝)
    
    Args:
        board: 当前棋盘状态
        depth: 搜索深度
        alpha: Alpha值
        beta: Beta值
        maximizing: 是否为最大化节点
    
    Returns:
        (评估分数, 最佳移动)
    """
    # 创建规则引擎
    rule_engine = RuleEngine(board)
    
    # 终止条件:深度为0或游戏结束
    if depth == 0:
        return evaluate_board(board, board.current_player), None
    
    # 检查游戏是否结束
    result = rule_engine.get_game_result()
    if result is not None:
        if result == board.current_player:
            return 999999, None  # 己方胜
        else:
            return -999999, None  # 对方胜
    
    # 获取所有合法移动
    all_moves = []
    pieces = board.get_all_pieces(board.current_player)
    for r, c, piece in pieces:
        legal_moves = rule_engine.get_legal_moves(r, c)
        for to_pos in legal_moves:
            all_moves.append(((r, c), to_pos))
    
    if not all_moves:
        # 无合法移动,判负
        return -999999, None
    
    best_move = None
    
    if maximizing:
        # 最大化节点
        max_eval = -999999
        
        for move in all_moves:
            from_pos, to_pos = move
            
            # 创建临时棋盘执行移动
            temp_board = board.copy()
            temp_board.move_piece(from_pos, to_pos)
            
            # 递归搜索
            eval_score, _ = minimax_search(temp_board, depth - 1, alpha, beta, False)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            
            # Alpha-Beta剪枝
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        
        return max_eval, best_move
    
    else:
        # 最小化节点
        min_eval = 999999
        
        for move in all_moves:
            from_pos, to_pos = move
            
            # 创建临时棋盘执行移动
            temp_board = board.copy()
            temp_board.move_piece(from_pos, to_pos)
            
            # 递归搜索
            eval_score, _ = minimax_search(temp_board, depth - 1, alpha, beta, True)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            
            # Alpha-Beta剪枝
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        
        return min_eval, best_move


def get_best_move(board: Board, difficulty: str = '中级') -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    获取最佳移动
    
    Args:
        board: 当前棋盘状态
        difficulty: 难度等级
    
    Returns:
        最佳移动 ((from_row, from_col), (to_row, to_col))
    """
    from .evaluation import DIFFICULTY_DEPTHS
    
    depth = DIFFICULTY_DEPTHS.get(difficulty, 3)
    _, best_move = minimax_search(board, depth, maximizing=True)
    
    return best_move
