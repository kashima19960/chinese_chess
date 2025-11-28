"""
Chinese notation generator for chess moves.
"""

from typing import Optional
from .constants import *
from .board import Board


class NotationGenerator:
    """中文记谱生成器"""
    
    def __init__(self, board: Board):
        self.board = board
    
    def generate_notation(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> str:
        """
        生成中文记谱
        
        Args:
            from_pos: 起始位置 (row, col)
            to_pos: 目标位置 (row, col)
        
        Returns:
            中文记谱字符串,如"炮二平五"
        """
        r1, c1 = from_pos
        r2, c2 = to_pos
        
        piece = self.board.get_piece(r1, c1)
        if not piece:
            return ""
        
        color = get_piece_color(piece)
        piece_name = PIECE_CHINESE_NAMES.get(piece, "")
        
        # 获取列号映射
        col_map = RED_COL_TO_CHINESE if color == RED else BLACK_COL_TO_CHINESE
        
        # 计算移动方向和距离
        dr = r2 - r1
        dc = c2 - c1
        
        # 判断是否需要前后区分(同列有多个相同棋子)
        prefix = self._get_position_prefix(r1, c1, piece, color)
        
        # 确定起始列或前后位置
        if prefix:
            # 有歧义,使用前/后/中等标记
            start_notation = prefix + piece_name
        else:
            # 无歧义,使用列号
            start_notation = piece_name + col_map[c1]
        
        # 确定移动方式和目标
        if dc == 0:
            # 纵向移动
            if dr > 0:
                # 向前(红方向上,黑方向下)
                direction = "进"
                distance = abs(dr)
            else:
                # 向后
                direction = "退"
                distance = abs(dr)
            
            # 对于特殊棋子使用目标列号
            if piece.upper() in ['A', 'B']:  # 仕/士/相/象
                target = col_map[c2]
            else:
                target = self._number_to_chinese(distance, color)
        else:
            # 横向移动
            direction = "平"
            target = col_map[c2]
        
        return start_notation + direction + target
    
    def _get_position_prefix(self, row: int, col: int, piece: str, color: int) -> str:
        """
        获取位置前缀(前/后/中等)
        
        Args:
            row, col: 棋子位置
            piece: 棋子类型
            color: 棋子颜色
        
        Returns:
            位置前缀字符串,如"前"/"后"/"",如果无歧义返回空字符串
        """
        # 检查同一列是否有相同类型的棋子
        same_pieces = []
        for r in range(BOARD_ROWS):
            p = self.board.get_piece(r, col)
            if p == piece:
                same_pieces.append(r)
        
        if len(same_pieces) <= 1:
            return ""
        
        # 排序(从己方视角)
        same_pieces.sort(reverse=(color == RED))
        
        # 找到当前棋子的位置
        idx = same_pieces.index(row)
        
        if len(same_pieces) == 2:
            return "前" if idx == 0 else "后"
        elif len(same_pieces) == 3:
            return ["前", "中", "后"][idx]
        elif len(same_pieces) == 4:
            return ["前", "二", "三", "四"][idx]
        else:  # >= 5
            return ["前", "二", "三", "四", "五"][idx] if idx < 5 else "后"
    
    def _number_to_chinese(self, num: int, color: int) -> str:
        """
        将数字转换为中文
        
        Args:
            num: 数字
            color: RED 使用汉字数字, BLACK 使用阿拉伯数字
        
        Returns:
            中文数字字符串
        """
        if color == RED:
            chinese_nums = {
                1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
                6: "六", 7: "七", 8: "八", 9: "九", 10: "十"
            }
            return chinese_nums.get(num, str(num))
        else:
            return str(num)
