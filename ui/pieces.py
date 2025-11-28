"""
Chess piece graphics items.
"""

from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem, QGraphicsObject
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QObject, pyqtProperty, QPointF
from PyQt5.QtGui import QBrush, QColor, QPen, QFont
import sys
sys.path.append('..')

from core.constants import PIECE_CHINESE_NAMES, get_piece_color, RED


class PieceItem(QGraphicsObject):
    """棋子图形项"""
    
    def __init__(self, piece: str, row: int, col: int, cell_size: float):
        """
        初始化棋子
        
        Args:
            piece: 棋子类型
            row, col: 棋盘位置
            cell_size: 单元格大小
        """
        super().__init__()
        
        self.piece = piece
        self.board_row = row
        self.board_col = col
        self.cell_size = cell_size
        self.radius = cell_size * 0.4
        
        # 创建椭圆形状
        self.ellipse = QGraphicsEllipseItem(-self.radius, -self.radius, 
                                            self.radius * 2, self.radius * 2, self)
        
        # 设置棋子样式
        self._setup_appearance()
        
        # 创建文字
        self.text_item = QGraphicsTextItem(PIECE_CHINESE_NAMES[piece], self)
        self._setup_text()
        
        # 设置交互属性
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setZValue(10)  # 确保棋子在棋盘上方
        
        self.is_selected = False
    
    def boundingRect(self):
        """返回边界矩形"""
        return QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)
    
    def paint(self, painter, option, widget):
        """绘制方法(QGraphicsObject需要实现)"""
        pass  # 实际绘制由子项完成
    
    def _setup_appearance(self):
        """设置棋子外观"""
        color = get_piece_color(self.piece)
        
        # 背景色
        if color == RED:
            bg_color = QColor(255, 220, 180)  # 浅橙色
        else:
            bg_color = QColor(50, 50, 50)     # 深灰色
        
        self.ellipse.setBrush(QBrush(bg_color))
        
        # 边框
        pen = QPen(QColor(0, 0, 0), 2)
        self.ellipse.setPen(pen)
    
    def _setup_text(self):
        """设置文字样式"""
        color = get_piece_color(self.piece)
        
        # 文字颜色
        if color == RED:
            text_color = QColor(200, 0, 0)  # 红色
        else:
            text_color = QColor(255, 255, 255)  # 白色
        
        self.text_item.setDefaultTextColor(text_color)
        
        # 字体
        font = QFont("SimHei", int(self.cell_size * 0.3), QFont.Bold)
        self.text_item.setFont(font)
        
        # 居中
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(-text_rect.width() / 2, -text_rect.height() / 2)
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.is_selected = selected
        
        if selected:
            # 选中时显示光晕效果
            pen = QPen(QColor(255, 215, 0), 4)  # 金色
            self.ellipse.setPen(pen)
        else:
            # 未选中时恢复普通边框
            pen = QPen(QColor(0, 0, 0), 2)
            self.ellipse.setPen(pen)
    
    def update_position(self, row: int, col: int):
        """更新棋盘位置"""
        self.board_row = row
        self.board_col = col
