"""
Main application window for Chinese Chess.
"""

import sys
import os

# 在导入PyQt5之前设置环境变量，禁用字体和SVG警告
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.fonts=false'

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QMessageBox, QPushButton, QLabel)
from PyQt5.QtCore import Qt, QDir, QPoint
from PyQt5.QtGui import QFont, QIcon

# 设置高DPI支持
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

from core.board import Board
from core.rules import RuleEngine
from core.notation import NotationGenerator
from core.constants import RED, BLACK, INITIAL_FEN, get_piece_color
from ui.board_view import BoardView
from ui.control_panel import ControlPanel
from ai.worker import AIWorker


class TitleBar(QWidget):
    """自定义标题栏"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pressing = False
        self.start_pos = None
        
        self.setFixedHeight(40)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("中国象棋")
        title_label.setFont(QFont("SimHei", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 最小化按钮
        self.min_btn = QPushButton("—")
        self.min_btn.setFixedSize(40, 30)
        self.min_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.min_btn.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.min_btn)
        
        # 最大化/还原按钮
        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(40, 30)
        self.max_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.max_btn.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.max_btn)
        
        # 关闭按钮
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(40, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.7);
            }
        """)
        self.close_btn.clicked.connect(self.parent.close)
        layout.addWidget(self.close_btn)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.pressing = True
            self.start_pos = event.globalPos() - self.parent.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.pressing and self.start_pos:
            self.parent.move(event.globalPos() - self.start_pos)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.pressing = False
        self.start_pos = None
    
    def mouseDoubleClickEvent(self, event):
        """双击最大化/还原"""
        self.toggle_maximize()
    
    def toggle_maximize(self):
        """切换最大化状态"""
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.max_btn.setText("□")
        else:
            self.parent.showMaximized()
            self.max_btn.setText("❐")


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 游戏状态
        self.board = Board(INITIAL_FEN)
        self.rule_engine = RuleEngine(self.board)
        self.notation_gen = NotationGenerator(self.board)
        
        # 游戏设置
        self.game_mode = "PVE"  # PVE 或 PVP
        self.difficulty = "中级"
        self.player_color = RED
        self.game_active = False
        
        # AI线程
        self.ai_worker: AIWorker = None
        
        # 状态机
        self.state = "IDLE"  # IDLE, USER_TURN, AI_THINKING, HINT_CALCULATING, GAME_OVER
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("中国象棋")
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局（垂直，包含标题栏）
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 添加自定义标题栏
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # 内容布局
        content_widget = QWidget()
        main_layout.addWidget(content_widget)
        
        layout = QHBoxLayout(content_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)
        
        # 棋盘视图
        self.board_view = BoardView(self.board)
        self.board_view.piece_clicked.connect(self.on_piece_clicked)
        self.board_view.move_made.connect(self.on_move_made)
        layout.addWidget(self.board_view)
        
        # 控制面板
        self.control_panel = ControlPanel()
        self.control_panel.start_game_clicked.connect(self.start_game)
        self.control_panel.undo_clicked.connect(self.undo_move)
        self.control_panel.hint_clicked.connect(self.request_hint)
        self.control_panel.resign_clicked.connect(self.resign_game)
        self.control_panel.theme_changed.connect(self.change_theme)
        layout.addWidget(self.control_panel)
        
        # 设置窗口最小尺寸
        self.setMinimumSize(1100, 750)
    
    def start_game(self):
        """开始游戏"""
        # 获取设置
        self.game_mode, self.difficulty, player_color_str = self.control_panel.get_settings()
        self.player_color = RED if player_color_str == "RED" else BLACK
        
        # 重置棋盘
        self.board = Board(INITIAL_FEN)
        self.rule_engine = RuleEngine(self.board)
        self.notation_gen = NotationGenerator(self.board)
        
        # 刷新界面
        self.board_view.board = self.board
        self.board_view.refresh_board()
        self.control_panel.clear_notation()
        
        # 设置游戏活动状态
        self.game_active = True
        self.control_panel.set_game_active(True)
        
        # 根据模式决定初始状态
        if self.game_mode == "PVP":
            self.state = "USER_TURN"
            self.control_panel.set_status("红方走棋", "red")
            self.board_view.set_locked(False)
        else:  # PVE
            if self.player_color == RED:
                self.state = "USER_TURN"
                self.control_panel.set_status("轮到你走棋(红方)", "red")
                self.board_view.set_locked(False)
            else:
                self.state = "AI_THINKING"
                self.control_panel.set_status("AI思考中...", "orange")
                self.board_view.set_locked(True)
                self.request_ai_move()
    
    def on_piece_clicked(self, row: int, col: int):
        """处理棋子点击"""
        if self.state not in ["USER_TURN"]:
            return
        
        piece = self.board.get_piece(row, col)
        
        # 如果已经选中了棋子
        if self.board_view.selected_pos:
            from_pos = self.board_view.selected_pos
            
            # 点击的是合法移动位置
            legal_moves = self.rule_engine.get_legal_moves(from_pos[0], from_pos[1])
            if (row, col) in legal_moves:
                self.make_move(from_pos, (row, col))
                return
            
            # 取消选中
            self.board_view.clear_selection()
        
        # 选中新棋子
        if piece and get_piece_color(piece) == self.board.current_player:
            # PVP模式或者是玩家的回合
            if self.game_mode == "PVP" or self.board.current_player == self.player_color:
                legal_moves = self.rule_engine.get_legal_moves(row, col)
                if legal_moves:
                    self.board_view.select_piece(row, col, legal_moves)
    
    def make_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]):
        """执行移动"""
        # 生成记谱
        notation = self.notation_gen.generate_notation(from_pos, to_pos)
        
        # 执行移动
        captured = self.board.move_piece(from_pos, to_pos)
        
        # 动画移动
        self.board_view.animate_move(from_pos, to_pos, captured)
        
        # 添加记谱
        self.control_panel.add_notation(notation)
        
        # 清除选中和提示
        self.board_view.clear_selection()
        self.board_view.clear_hint()
    
    def on_move_made(self, from_pos: tuple[int, int], to_pos: tuple[int, int]):
        """移动完成后的处理"""
        # 更新规则引擎
        self.rule_engine = RuleEngine(self.board)
        self.notation_gen = NotationGenerator(self.board)
        
        # 检查游戏是否结束
        result = self.rule_engine.get_game_result()
        if result is not None:
            self.end_game(result)
            return
        
        # 切换状态
        if self.game_mode == "PVP":
            # PVP模式,继续等待玩家操作
            self.state = "USER_TURN"
            color_name = "红方" if self.board.current_player == RED else "黑方"
            color = "red" if self.board.current_player == RED else "black"
            self.control_panel.set_status(f"{color_name}走棋", color)
        else:  # PVE
            if self.board.current_player == self.player_color:
                # 玩家回合
                self.state = "USER_TURN"
                self.control_panel.set_status("轮到你走棋", "green")
                self.board_view.set_locked(False)
            else:
                # AI回合
                self.state = "AI_THINKING"
                self.control_panel.set_status("AI思考中...", "orange")
                self.control_panel.show_thinking(True)
                self.board_view.set_locked(True)
                self.request_ai_move()
    
    def request_ai_move(self):
        """请求AI移动"""
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.stop()
            self.ai_worker.wait()
        
        self.ai_worker = AIWorker(self.board, mode='AI_MOVE', difficulty=self.difficulty)
        self.ai_worker.move_ready.connect(self.on_ai_move_ready)
        self.ai_worker.error_occurred.connect(self.on_ai_error)
        self.ai_worker.start()
    
    def on_ai_move_ready(self, from_pos: tuple[int, int], to_pos: tuple[int, int]):
        """AI移动完成"""
        self.control_panel.show_thinking(False)
        self.make_move(from_pos, to_pos)
    
    def request_hint(self):
        """请求提示"""
        if self.state != "USER_TURN":
            return
        
        if self.ai_worker and self.ai_worker.isRunning():
            return
        
        self.state = "HINT_CALCULATING"
        self.control_panel.set_status("计算提示中...", "orange")
        self.control_panel.show_thinking(True)
        self.board_view.set_locked(True)
        
        self.ai_worker = AIWorker(self.board, mode='HINT', difficulty=self.difficulty)
        self.ai_worker.hint_ready.connect(self.on_hint_ready)
        self.ai_worker.error_occurred.connect(self.on_ai_error)
        self.ai_worker.start()
    
    def on_hint_ready(self, from_pos: tuple[int, int], to_pos: tuple[int, int]):
        """提示计算完成"""
        self.control_panel.show_thinking(False)
        self.state = "USER_TURN"
        self.control_panel.set_status("建议走法已显示", "blue")
        self.board_view.set_locked(False)
        
        # 显示提示
        self.board_view.show_hint(from_pos, to_pos)
    
    def on_ai_error(self, error_msg: str):
        """AI错误处理"""
        self.control_panel.show_thinking(False)
        QMessageBox.warning(self, "错误", error_msg)
        
        if self.state == "AI_THINKING":
            # AI无法移动,游戏结束
            self.end_game(self.player_color)
        else:
            self.state = "USER_TURN"
            self.board_view.set_locked(False)
    
    def undo_move(self):
        """悔棋"""
        if not self.game_active:
            return
        
        # PVE模式下悔两步(玩家和AI的移动)
        if self.game_mode == "PVE":
            if len(self.board.history) >= 2:
                self.board.undo_move()
                self.board.undo_move()
            elif len(self.board.history) == 1:
                self.board.undo_move()
        else:  # PVP模式下悔一步
            if self.board.history:
                self.board.undo_move()
        
        # 刷新界面
        self.board_view.board = self.board
        self.board_view.refresh_board()
        self.rule_engine = RuleEngine(self.board)
        self.notation_gen = NotationGenerator(self.board)
        
        # 移除最后的记谱
        count = self.control_panel.notation_list.count()
        if count > 0:
            if self.game_mode == "PVE" and count >= 2:
                self.control_panel.notation_list.takeItem(count - 1)
                self.control_panel.notation_list.takeItem(count - 2)
            else:
                self.control_panel.notation_list.takeItem(count - 1)
        
        # 恢复玩家回合
        self.state = "USER_TURN"
        self.board_view.set_locked(False)
        self.control_panel.set_status("已悔棋", "blue")
    
    def resign_game(self):
        """认输"""
        if not self.game_active:
            return
        
        reply = QMessageBox.question(self, "确认", "确定要认输吗?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            winner = -self.board.current_player
            self.end_game(winner)
    
    def end_game(self, winner: int):
        """游戏结束"""
        self.game_active = False
        self.state = "GAME_OVER"
        self.board_view.set_locked(True)
        self.control_panel.set_game_active(False)
        
        # 显示结果
        if winner == RED:
            winner_name = "红方"
            color = "red"
        else:
            winner_name = "黑方"
            color = "black"
        
        self.control_panel.set_status(f"游戏结束 - {winner_name}获胜!", color)
        
        QMessageBox.information(self, "游戏结束", f"{winner_name}获胜!")
    
    def change_theme(self, theme_file: str):
        """切换主题"""
        try:
            from qt_material import apply_stylesheet
            apply_stylesheet(QApplication.instance(), theme=theme_file)
        except Exception as e:
            print(f"主题切换失败: {e}")
    
    def closeEvent(self, event):
        """关闭窗口时清理资源"""
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.stop()
            self.ai_worker.wait()
        event.accept()


def main():
    """主函数"""
    # 禁用Python警告
    import warnings
    import logging
    warnings.filterwarnings('ignore')
    logging.getLogger().setLevel(logging.CRITICAL)
    
    app = QApplication(sys.argv)
    
    # 设置资源搜索路径
    resource_path = os.path.join(os.path.dirname(__file__), 'resources')
    if os.path.exists(resource_path):
        QDir.addSearchPath('icon', os.path.join(resource_path, 'icon'))
    
    # 应用qt-material主题
    try:
        from qt_material import apply_stylesheet
        # 使用深色主题，指定Windows默认字体避免警告
        apply_stylesheet(app, theme='dark_teal.xml', extra={
            'font_family': 'Segoe UI',
        })
    except Exception:
        pass  # 静默失败
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
