"""
Rule engine for move validation and game state checking.
"""

from typing import Optional
from .constants import *
from .board import Board


class RuleEngine:
    """中国象棋规则引擎"""
    
    def __init__(self, board: Board):
        self.board = board
    
    def get_legal_moves(self, row: int, col: int) -> list[tuple[int, int]]:
        """
        获取指定位置棋子的所有合法移动
        
        Args:
            row, col: 棋子位置
        
        Returns:
            合法目标位置列表 [(row, col), ...]
        """
        piece = self.board.get_piece(row, col)
        if not piece:
            return []
        
        # 获取所有可能的移动
        moves = self._get_pseudo_legal_moves(row, col, piece)
        
        # 过滤掉会导致被将军的移动
        legal_moves = []
        for to_pos in moves:
            if self._is_legal_move((row, col), to_pos):
                legal_moves.append(to_pos)
        
        return legal_moves
    
    def _get_pseudo_legal_moves(self, row: int, col: int, piece: str) -> list[tuple[int, int]]:
        """获取伪合法移动(不考虑将军)"""
        piece_type = piece.upper()
        color = get_piece_color(piece)
        
        if piece_type == 'R':  # 车
            return self._get_rook_moves(row, col, color)
        elif piece_type == 'N':  # 马
            return self._get_knight_moves(row, col, color)
        elif piece_type == 'B':  # 相/象
            return self._get_bishop_moves(row, col, color)
        elif piece_type == 'A':  # 仕/士
            return self._get_advisor_moves(row, col, color)
        elif piece_type == 'K':  # 帅/将
            return self._get_king_moves(row, col, color)
        elif piece_type == 'C':  # 炮
            return self._get_cannon_moves(row, col, color)
        elif piece_type == 'P':  # 兵/卒
            return self._get_pawn_moves(row, col, color)
        
        return []
    
    def _get_rook_moves(self, row: int, col: int, color: int) -> list[tuple[int, int]]:
        """车的移动:直线移动"""
        moves = []
        
        # 四个方向: 上下左右
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while is_in_bounds(r, c):
                target_piece = self.board.get_piece(r, c)
                if target_piece is None:
                    moves.append((r, c))
                elif get_piece_color(target_piece) != color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        
        return moves
    
    def _get_knight_moves(self, row: int, col: int, color: int) -> list[tuple[int, int]]:
        """马的移动:日字,检测蹩腿"""
        moves = []
        
        # 8个可能的移动方向: (dr, dc, 蹩腿检测位置)
        knight_moves = [
            (2, 1, (1, 0)),   # 向上
            (2, -1, (1, 0)),
            (-2, 1, (-1, 0)), # 向下
            (-2, -1, (-1, 0)),
            (1, 2, (0, 1)),   # 向右
            (-1, 2, (0, 1)),
            (1, -2, (0, -1)), # 向左
            (-1, -2, (0, -1)),
        ]
        
        for dr, dc, (block_dr, block_dc) in knight_moves:
            r2, c2 = row + dr, col + dc
            block_r, block_c = row + block_dr, col + block_dc
            
            # 检查目标位置合法性
            if not is_in_bounds(r2, c2):
                continue
            
            # 检查蹩腿
            if self.board.get_piece(block_r, block_c) is not None:
                continue
            
            # 检查目标位置是否为己方棋子
            target_piece = self.board.get_piece(r2, c2)
            if target_piece is None or get_piece_color(target_piece) != color:
                moves.append((r2, c2))
        
        return moves
    
    def _get_bishop_moves(self, row: int, col: int, color: int) -> list[tuple[int, int]]:
        """相/象的移动:田字,检测塞象眼,不能过河"""
        moves = []
        
        # 4个可能的移动方向
        bishop_moves = [
            (2, 2, (1, 1)),    # 右上
            (2, -2, (1, -1)),  # 左上
            (-2, 2, (-1, 1)),  # 右下
            (-2, -2, (-1, -1)) # 左下
        ]
        
        for dr, dc, (block_dr, block_dc) in bishop_moves:
            r2, c2 = row + dr, col + dc
            block_r, block_c = row + block_dr, col + block_dc
            
            # 检查目标位置合法性
            if not is_in_bounds(r2, c2):
                continue
            
            # 检查是否过河
            if not can_cross_river('B' if color == RED else 'b', r2):
                continue
            
            # 检查塞象眼
            if self.board.get_piece(block_r, block_c) is not None:
                continue
            
            # 检查目标位置是否为己方棋子
            target_piece = self.board.get_piece(r2, c2)
            if target_piece is None or get_piece_color(target_piece) != color:
                moves.append((r2, c2))
        
        return moves
    
    def _get_advisor_moves(self, row: int, col: int, color: int) -> list[tuple[int, int]]:
        """仕/士的移动:斜线一步,限制在九宫内"""
        moves = []
        
        # 4个斜向移动
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            r2, c2 = row + dr, col + dc
            
            # 检查是否在九宫内
            if not is_in_palace(r2, c2, color):
                continue
            
            # 检查目标位置是否为己方棋子
            target_piece = self.board.get_piece(r2, c2)
            if target_piece is None or get_piece_color(target_piece) != color:
                moves.append((r2, c2))
        
        return moves
    
    def _get_king_moves(self, row: int, col: int, color: int) -> list[tuple[int, int]]:
        """帅/将的移动:直线一步,限制在九宫内"""
        moves = []
        
        # 4个方向: 上下左右
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
        for dr, dc in directions:
            r2, c2 = row + dr, col + dc
            
            # 检查是否在九宫内
            if not is_in_palace(r2, c2, color):
                continue
            
            # 检查目标位置是否为己方棋子
            target_piece = self.board.get_piece(r2, c2)
            if target_piece is None or get_piece_color(target_piece) != color:
                moves.append((r2, c2))
        
        return moves
    
    def _get_cannon_moves(self, row: int, col: int, color: int) -> list[tuple[int, int]]:
        """炮的移动:直线移动,吃子需要跳一个棋子"""
        moves = []
        
        # 四个方向: 上下左右
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
        for dr, dc in directions:
            jumped = False  # 是否已经跳过一个棋子
            r, c = row + dr, col + dc
            
            while is_in_bounds(r, c):
                target_piece = self.board.get_piece(r, c)
                
                if target_piece is None:
                    # 空位
                    if not jumped:
                        moves.append((r, c))
                else:
                    # 有棋子
                    if not jumped:
                        jumped = True  # 跳过这个棋子
                    else:
                        # 已经跳过一个,可以吃子
                        if get_piece_color(target_piece) != color:
                            moves.append((r, c))
                        break
                
                r += dr
                c += dc
        
        return moves
    
    def _get_pawn_moves(self, row: int, col: int, color: int) -> list[tuple[int, int]]:
        """兵/卒的移动:未过河只能前进,过河后可以横走"""
        moves = []
        
        # 判断是否过河
        if color == RED:
            crossed = row > RIVER_ROW
            forward = 1  # 红方向上走
        else:
            crossed = row < RIVER_ROW + 1
            forward = -1  # 黑方向下走
        
        # 前进
        r2, c2 = row + forward, col
        if is_in_bounds(r2, c2):
            target_piece = self.board.get_piece(r2, c2)
            if target_piece is None or get_piece_color(target_piece) != color:
                moves.append((r2, c2))
        
        # 过河后可以横走
        if crossed:
            for dc in [-1, 1]:
                r2, c2 = row, col + dc
                if is_in_bounds(r2, c2):
                    target_piece = self.board.get_piece(r2, c2)
                    if target_piece is None or get_piece_color(target_piece) != color:
                        moves.append((r2, c2))
        
        return moves
    
    def _is_legal_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """
        检查移动是否合法(考虑将军和飞将)
        
        Args:
            from_pos: 起始位置
            to_pos: 目标位置
        
        Returns:
            是否合法
        """
        # 创建临时棋盘执行移动
        temp_board = self.board.copy()
        r1, c1 = from_pos
        r2, c2 = to_pos
        
        piece = temp_board.get_piece(r1, c1)
        if not piece:
            return False
        
        color = get_piece_color(piece)
        
        # 执行移动
        temp_board.set_piece(r2, c2, piece)
        temp_board.set_piece(r1, c1, None)
        
        # 创建临时规则引擎
        temp_engine = RuleEngine(temp_board)
        
        # 检查是否被将军
        if temp_engine.is_in_check(color):
            return False
        
        # 检查飞将
        if temp_engine._is_flying_general():
            return False
        
        return True
    
    def is_in_check(self, color: int) -> bool:
        """
        检查指定颜色是否被将军
        
        Args:
            color: RED 或 BLACK
        
        Returns:
            是否被将军
        """
        # 找到己方将/帅
        king_pos = self.board.find_king(color)
        if not king_pos:
            return False
        
        # 检查敌方所有棋子是否能攻击到将/帅
        enemy_color = -color
        enemy_pieces = self.board.get_all_pieces(enemy_color)
        
        for r, c, piece in enemy_pieces:
            pseudo_moves = self._get_pseudo_legal_moves(r, c, piece)
            if king_pos in pseudo_moves:
                return True
        
        return False
    
    def _is_flying_general(self) -> bool:
        """检查是否出现飞将(两个将在同一列且之间无棋子)"""
        red_king_pos = self.board.find_king(RED)
        black_king_pos = self.board.find_king(BLACK)
        
        if not red_king_pos or not black_king_pos:
            return False
        
        r1, c1 = red_king_pos
        r2, c2 = black_king_pos
        
        # 检查是否在同一列
        if c1 != c2:
            return False
        
        # 检查之间是否有棋子
        min_row = min(r1, r2)
        max_row = max(r1, r2)
        
        for row in range(min_row + 1, max_row):
            if self.board.get_piece(row, c1) is not None:
                return False
        
        return True
    
    def is_checkmate(self, color: int) -> bool:
        """
        检查指定颜色是否被将死
        
        Args:
            color: RED 或 BLACK
        
        Returns:
            是否被将死
        """
        # 必须先被将军
        if not self.is_in_check(color):
            return False
        
        # 检查是否有任何合法移动
        pieces = self.board.get_all_pieces(color)
        for r, c, piece in pieces:
            legal_moves = self.get_legal_moves(r, c)
            if legal_moves:
                return False
        
        return True
    
    def is_stalemate(self, color: int) -> bool:
        """
        检查指定颜色是否困毙(无子可动但未被将军)
        
        Args:
            color: RED 或 BLACK
        
        Returns:
            是否困毙
        """
        # 不能被将军
        if self.is_in_check(color):
            return False
        
        # 检查是否有任何合法移动
        pieces = self.board.get_all_pieces(color)
        for r, c, piece in pieces:
            legal_moves = self.get_legal_moves(r, c)
            if legal_moves:
                return False
        
        return True
    
    def get_game_result(self) -> Optional[int]:
        """
        获取游戏结果
        
        Returns:
            RED: 红方胜
            BLACK: 黑方胜
            None: 游戏未结束
        """
        current_color = self.board.current_player
        
        # 检查当前玩家是否被将死
        if self.is_checkmate(current_color):
            return -current_color  # 对手获胜
        
        # 检查当前玩家是否困毙
        if self.is_stalemate(current_color):
            return -current_color  # 对手获胜
        
        return None
