"""
QThread worker for AI computation.
"""

from PyQt5.QtCore import QThread, pyqtSignal
from typing import Optional, Tuple
import sys
sys.path.append('..')

from core.board import Board
from .search import get_best_move


class AIWorker(QThread):
    """AI计算线程"""
    
    # 信号定义
    move_ready = pyqtSignal(tuple, tuple)  # AI移动完成: (from_pos, to_pos)
    hint_ready = pyqtSignal(tuple, tuple)  # 提示完成: (from_pos, to_pos)
    error_occurred = pyqtSignal(str)       # 错误发生
    
    def __init__(self, board: Board, mode: str = 'AI_MOVE', difficulty: str = '中级'):
        """
        初始化AI工作线程
        
        Args:
            board: 棋盘状态
            mode: 模式 'AI_MOVE' 或 'HINT'
            difficulty: 难度等级
        """
        super().__init__()
        self.board = board.copy()  # 创建副本避免线程冲突
        self.mode = mode
        self.difficulty = difficulty
        self._is_running = True
    
    def run(self):
        """线程执行函数"""
        try:
            # 计算最佳移动
            best_move = get_best_move(self.board, self.difficulty)
            
            if not self._is_running:
                return
            
            if best_move:
                from_pos, to_pos = best_move
                
                # 根据模式发送信号
                if self.mode == 'AI_MOVE':
                    self.move_ready.emit(from_pos, to_pos)
                elif self.mode == 'HINT':
                    self.hint_ready.emit(from_pos, to_pos)
            else:
                self.error_occurred.emit("无法找到合法移动")
        
        except Exception as e:
            self.error_occurred.emit(f"AI计算错误: {str(e)}")
    
    def stop(self):
        """停止线程"""
        self._is_running = False
