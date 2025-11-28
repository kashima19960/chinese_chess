"""
Board view with graphics scene.
"""

from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsRectItem,
                              QGraphicsLineItem, QGraphicsEllipseItem)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QBrush, QColor, QPen, QPainter
from typing import Optional, List, Tuple
import sys
sys.path.append('..')

from core.board import Board
from core.constants import BOARD_ROWS, BOARD_COLS, get_piece_color
from .pieces import PieceItem


class BoardView(QGraphicsView):
    """棋盘视图"""
    
    # 信号定义
    piece_clicked = pyqtSignal(int, int)  # 棋子被点击: (row, col)
    move_made = pyqtSignal(tuple, tuple)  # 移动完成: (from_pos, to_pos)
    
    def __init__(self, board: Board, cell_size: float = 60.0):
        """
        初始化棋盘视图
        
        Args:
            board: 棋盘对象
            cell_size: 单元格大小
        """
        super().__init__()
        
        self.board = board
        self.cell_size = cell_size
        self.margin = cell_size
        
        # 创建场景
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # 设置视图属性
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 交互状态
        self.selected_piece: Optional[PieceItem] = None
        self.selected_pos: Optional[Tuple[int, int]] = None
        self.hint_markers: List[QGraphicsEllipseItem] = []
        self.legal_move_markers: List[QGraphicsEllipseItem] = []
        self.is_locked = False  # 锁定状态(AI思考时)
        
        # 棋子项字典
        self.piece_items: dict[Tuple[int, int], PieceItem] = {}
        
        # 动画
        self.current_animation: Optional[QPropertyAnimation] = None
        
        # 绘制棋盘
        self._draw_board()
        self._draw_pieces()
        
        # 设置场景大小
        scene_width = self.margin * 2 + (BOARD_COLS - 1) * self.cell_size
        scene_height = self.margin * 2 + (BOARD_ROWS - 1) * self.cell_size
        self.setSceneRect(0, 0, scene_width, scene_height)
        self.setFixedSize(int(scene_width) + 20, int(scene_height) + 20)
    
    def _draw_board(self):
        """绘制棋盘"""
        # 背景
        bg_rect = QGraphicsRectItem(0, 0, 
                                     self.margin * 2 + (BOARD_COLS - 1) * self.cell_size,
                                     self.margin * 2 + (BOARD_ROWS - 1) * self.cell_size)
        bg_rect.setBrush(QBrush(QColor(220, 179, 92)))  # 木色
        bg_rect.setPen(QPen(Qt.NoPen))
        bg_rect.setZValue(0)
        self.scene.addItem(bg_rect)
        
        # 绘制网格线
        pen = QPen(QColor(0, 0, 0), 2)
        
        # 横线
        for row in range(BOARD_ROWS):
            y = self.margin + row * self.cell_size
            line = QGraphicsLineItem(self.margin, y,
                                     self.margin + (BOARD_COLS - 1) * self.cell_size, y)
            line.setPen(pen)
            line.setZValue(1)
            self.scene.addItem(line)
        
        # 竖线
        for col in range(BOARD_COLS):
            x = self.margin + col * self.cell_size
            # 红方半场
            line1 = QGraphicsLineItem(x, self.margin,
                                      x, self.margin + 4 * self.cell_size)
            line1.setPen(pen)
            line1.setZValue(1)
            self.scene.addItem(line1)
            
            # 黑方半场
            line2 = QGraphicsLineItem(x, self.margin + 5 * self.cell_size,
                                      x, self.margin + 9 * self.cell_size)
            line2.setPen(pen)
            line2.setZValue(1)
            self.scene.addItem(line2)
        
        # 绘制九宫格斜线
        self._draw_palace_lines()
        
        # 绘制炮/兵标记
        self._draw_markers()
    
    def _draw_palace_lines(self):
        """绘制九宫格斜线"""
        pen = QPen(QColor(0, 0, 0), 2)
        
        # 红方九宫
        x1 = self.margin + 3 * self.cell_size
        x2 = self.margin + 5 * self.cell_size
        y1 = self.margin + 0 * self.cell_size
        y2 = self.margin + 2 * self.cell_size
        
        line1 = QGraphicsLineItem(x1, y1, x2, y2)
        line1.setPen(pen)
        line1.setZValue(1)
        self.scene.addItem(line1)
        
        line2 = QGraphicsLineItem(x2, y1, x1, y2)
        line2.setPen(pen)
        line2.setZValue(1)
        self.scene.addItem(line2)
        
        # 黑方九宫
        y1 = self.margin + 7 * self.cell_size
        y2 = self.margin + 9 * self.cell_size
        
        line3 = QGraphicsLineItem(x1, y1, x2, y2)
        line3.setPen(pen)
        line3.setZValue(1)
        self.scene.addItem(line3)
        
        line4 = QGraphicsLineItem(x2, y1, x1, y2)
        line4.setPen(pen)
        line4.setZValue(1)
        self.scene.addItem(line4)
    
    def _draw_markers(self):
        """绘制炮/兵位置标记"""
        # 这里可以添加传统的炮架、兵位标记
        pass
    
    def _draw_pieces(self):
        """绘制所有棋子"""
        self.piece_items.clear()
        
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board.get_piece(row, col)
                if piece:
                    self._add_piece_item(piece, row, col)
    
    def _add_piece_item(self, piece: str, row: int, col: int):
        """添加棋子项"""
        piece_item = PieceItem(piece, row, col, self.cell_size)
        
        # 计算屏幕位置
        x, y = self._board_to_scene(row, col)
        piece_item.setPos(x, y)
        
        self.scene.addItem(piece_item)
        self.piece_items[(row, col)] = piece_item
    
    def _board_to_scene(self, row: int, col: int) -> Tuple[float, float]:
        """将棋盘坐标转换为场景坐标"""
        x = self.margin + col * self.cell_size
        y = self.margin + (BOARD_ROWS - 1 - row) * self.cell_size  # Y轴翻转
        return x, y
    
    def _scene_to_board(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        """将场景坐标转换为棋盘坐标"""
        col = round((x - self.margin) / self.cell_size)
        row = BOARD_ROWS - 1 - round((y - self.margin) / self.cell_size)
        
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            return row, col
        return None
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self.is_locked:
            return
        
        # 获取点击位置
        scene_pos = self.mapToScene(event.pos())
        board_pos = self._scene_to_board(scene_pos.x(), scene_pos.y())
        
        if board_pos:
            row, col = board_pos
            self.piece_clicked.emit(row, col)
    
    def select_piece(self, row: int, col: int, legal_moves: List[Tuple[int, int]]):
        """
        选中棋子并显示合法移动标记
        
        Args:
            row, col: 棋子位置
            legal_moves: 合法移动列表
        """
        # 取消之前的选中
        self.clear_selection()
        
        # 选中新棋子
        if (row, col) in self.piece_items:
            piece_item = self.piece_items[(row, col)]
            piece_item.set_selected(True)
            self.selected_piece = piece_item
            self.selected_pos = (row, col)
        
        # 显示合法移动标记
        self._show_legal_moves(legal_moves)
    
    def clear_selection(self):
        """清除选中状态"""
        if self.selected_piece:
            self.selected_piece.set_selected(False)
            self.selected_piece = None
            self.selected_pos = None
        
        self._clear_legal_moves()
    
    def _show_legal_moves(self, legal_moves: List[Tuple[int, int]]):
        """显示合法移动标记"""
        self._clear_legal_moves()
        
        for row, col in legal_moves:
            x, y = self._board_to_scene(row, col)
            
            # 检查目标位置是否有棋子
            has_piece = (row, col) in self.piece_items
            
            if has_piece:
                # 有棋子,显示红色圆圈(可吃子)
                marker = QGraphicsEllipseItem(x - 25, y - 25, 50, 50)
                marker.setPen(QPen(QColor(255, 0, 0), 3))
                marker.setBrush(QBrush(Qt.NoBrush))
            else:
                # 无棋子,显示绿色小圆点
                marker = QGraphicsEllipseItem(x - 8, y - 8, 16, 16)
                marker.setPen(QPen(Qt.NoPen))
                marker.setBrush(QBrush(QColor(0, 255, 0, 150)))
            
            marker.setZValue(5)
            self.scene.addItem(marker)
            self.legal_move_markers.append(marker)
    
    def _clear_legal_moves(self):
        """清除合法移动标记"""
        for marker in self.legal_move_markers:
            self.scene.removeItem(marker)
        self.legal_move_markers.clear()
    
    def show_hint(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """
        显示提示标记
        
        Args:
            from_pos: 起始位置
            to_pos: 目标位置
        """
        self.clear_hint()
        
        # 在起始和目标位置显示闪烁的蓝色标记
        for pos in [from_pos, to_pos]:
            row, col = pos
            x, y = self._board_to_scene(row, col)
            
            marker = QGraphicsEllipseItem(x - 30, y - 30, 60, 60)
            marker.setPen(QPen(QColor(0, 100, 255), 4))
            marker.setBrush(QBrush(Qt.NoBrush))
            marker.setZValue(5)
            self.scene.addItem(marker)
            self.hint_markers.append(marker)
    
    def clear_hint(self):
        """清除提示标记"""
        for marker in self.hint_markers:
            self.scene.removeItem(marker)
        self.hint_markers.clear()
    
    def animate_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                     captured_piece: Optional[str] = None):
        """
        动画移动棋子
        
        Args:
            from_pos: 起始位置
            to_pos: 目标位置
            captured_piece: 被吃掉的棋子
        """
        r1, c1 = from_pos
        r2, c2 = to_pos
        
        if (r1, c1) not in self.piece_items:
            return
        
        piece_item = self.piece_items[(r1, c1)]
        
        # 如果目标位置有棋子,先移除
        if (r2, c2) in self.piece_items:
            captured_item = self.piece_items.pop((r2, c2))
            self.scene.removeItem(captured_item)
        
        # 创建移动动画
        start_pos = piece_item.pos()
        end_x, end_y = self._board_to_scene(r2, c2)
        end_pos = QPointF(end_x, end_y)
        
        animation = QPropertyAnimation(piece_item, b"pos")
        animation.setDuration(300)  # 300ms
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 动画结束后更新字典
        def on_finished():
            self.piece_items.pop((r1, c1), None)
            self.piece_items[(r2, c2)] = piece_item
            piece_item.update_position(r2, c2)
            self.move_made.emit(from_pos, to_pos)
        
        animation.finished.connect(on_finished)
        animation.start()
        
        self.current_animation = animation
    
    def refresh_board(self):
        """刷新棋盘显示"""
        # 移除所有棋子
        for piece_item in self.piece_items.values():
            self.scene.removeItem(piece_item)
        
        # 重新绘制
        self._draw_pieces()
        self.clear_selection()
        self.clear_hint()
    
    def set_locked(self, locked: bool):
        """设置锁定状态"""
        self.is_locked = locked
        
        # 锁定时清除选中和标记
        if locked:
            self.clear_selection()
            self.clear_hint()
