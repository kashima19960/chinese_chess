"""
Board state management with FEN parsing.
"""

from typing import Optional
from .constants import *


class Board:
    """中国象棋棋盘状态管理类"""
    
    def __init__(self, fen: str = INITIAL_FEN):
        """
        初始化棋盘
        
        Args:
            fen: FEN字符串表示的棋盘状态
        """
        self.board: list[list[Optional[str]]] = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.current_player: int = RED  # 当前走子方
        self.history: list[str] = []  # 历史FEN记录
        self.move_history: list[tuple[tuple[int, int], tuple[int, int]]] = []  # 移动历史
        
        self.load_fen(fen)
    
    def load_fen(self, fen: str) -> None:
        """
        从FEN字符串加载棋盘状态
        
        FEN格式: "棋盘布局 当前玩家"
        例: "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w"
        """
        parts = fen.split()
        if len(parts) < 1:
            raise ValueError("Invalid FEN string")
        
        board_str = parts[0]
        rows = board_str.split('/')
        
        if len(rows) != BOARD_ROWS:
            raise ValueError(f"FEN must have {BOARD_ROWS} rows")
        
        # 清空棋盘
        self.board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        
        # 解析每一行(从黑方到红方: row 9 -> 0)
        for i, row_str in enumerate(rows):
            row_idx = BOARD_ROWS - 1 - i  # FEN第一行对应row=9
            col_idx = 0
            
            for char in row_str:
                if char.isdigit():
                    # 数字表示空格数量
                    col_idx += int(char)
                elif char in ALL_PIECES:
                    if col_idx >= BOARD_COLS:
                        raise ValueError(f"Too many pieces in row {row_idx}")
                    self.board[row_idx][col_idx] = char
                    col_idx += 1
        
        # 解析当前玩家
        if len(parts) > 1:
            self.current_player = RED if parts[1] == 'w' else BLACK
        else:
            self.current_player = RED
    
    def to_fen(self) -> str:
        """
        将当前棋盘状态转换为FEN字符串
        """
        rows = []
        for row_idx in range(BOARD_ROWS - 1, -1, -1):  # 从row 9到row 0
            row_str = ""
            empty_count = 0
            
            for col_idx in range(BOARD_COLS):
                piece = self.board[row_idx][col_idx]
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += piece
            
            if empty_count > 0:
                row_str += str(empty_count)
            
            rows.append(row_str)
        
        board_str = '/'.join(rows)
        player_str = 'w' if self.current_player == RED else 'b'
        
        return f"{board_str} {player_str}"
    
    def get_piece(self, row: int, col: int) -> Optional[str]:
        """获取指定位置的棋子"""
        if not is_in_bounds(row, col):
            return None
        return self.board[row][col]
    
    def set_piece(self, row: int, col: int, piece: Optional[str]) -> None:
        """设置指定位置的棋子"""
        if is_in_bounds(row, col):
            self.board[row][col] = piece
    
    def move_piece(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> Optional[str]:
        """
        移动棋子
        
        Args:
            from_pos: 起始位置 (row, col)
            to_pos: 目标位置 (row, col)
        
        Returns:
            被吃掉的棋子,如果没有则返回None
        """
        r1, c1 = from_pos
        r2, c2 = to_pos
        
        piece = self.get_piece(r1, c1)
        captured = self.get_piece(r2, c2)
        
        # 保存当前状态到历史
        self.history.append(self.to_fen())
        self.move_history.append((from_pos, to_pos))
        
        # 执行移动
        self.set_piece(r2, c2, piece)
        self.set_piece(r1, c1, None)
        
        # 切换玩家
        self.current_player = -self.current_player
        
        return captured
    
    def undo_move(self) -> bool:
        """
        悔棋
        
        Returns:
            是否成功悔棋
        """
        if not self.history:
            return False
        
        # 恢复上一个状态
        last_fen = self.history.pop()
        self.move_history.pop()
        self.load_fen(last_fen)
        
        return True
    
    def copy(self) -> 'Board':
        """创建棋盘的深拷贝"""
        new_board = Board()
        new_board.load_fen(self.to_fen())
        new_board.history = self.history.copy()
        new_board.move_history = self.move_history.copy()
        return new_board
    
    def find_king(self, color: int) -> Optional[tuple[int, int]]:
        """
        查找指定颜色的将/帅位置
        
        Args:
            color: RED 或 BLACK
        
        Returns:
            (row, col) 或 None
        """
        king = 'K' if color == RED else 'k'
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board[row][col] == king:
                    return (row, col)
        return None
    
    def get_all_pieces(self, color: int) -> list[tuple[int, int, str]]:
        """
        获取指定颜色的所有棋子
        
        Args:
            color: RED 或 BLACK
        
        Returns:
            [(row, col, piece), ...]
        """
        pieces = []
        target_set = RED_PIECES if color == RED else BLACK_PIECES
        
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece and piece in target_set:
                    pieces.append((row, col, piece))
        
        return pieces
    
    def __str__(self) -> str:
        """打印棋盘(用于调试)"""
        lines = []
        lines.append("  0 1 2 3 4 5 6 7 8")
        for row in range(BOARD_ROWS - 1, -1, -1):
            line = f"{row} "
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece:
                    line += piece + " "
                else:
                    line += ". "
            lines.append(line)
        return "\n".join(lines)
