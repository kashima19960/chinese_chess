"""
Control panel for game settings and actions.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QListWidget, QLabel, QComboBox, QGroupBox, QRadioButton,
                              QButtonGroup, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ControlPanel(QWidget):
    """控制面板"""
    
    # 信号定义
    start_game_clicked = pyqtSignal()
    undo_clicked = pyqtSignal()
    hint_clicked = pyqtSignal()
    resign_clicked = pyqtSignal()
    settings_changed = pyqtSignal(str, str, str)  # (mode, difficulty, player_color)
    theme_changed = pyqtSignal(str)  # theme
    
    def __init__(self):
        super().__init__()
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("中国象棋")
        title_label.setFont(QFont("SimHei", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 设置区域
        settings_group = self._create_settings_group()
        layout.addWidget(settings_group)
        
        # 操作按钮区域
        actions_group = self._create_actions_group()
        layout.addWidget(actions_group)
        
        # 进度条(AI思考时显示)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("请点击开始游戏")
        self.status_label.setFont(QFont("SimHei", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: blue;")
        layout.addWidget(self.status_label)
        
        # 棋谱记录
        notation_label = QLabel("棋谱记录:")
        notation_label.setFont(QFont("SimHei", 12, QFont.Bold))
        layout.addWidget(notation_label)
        
        self.notation_list = QListWidget()
        self.notation_list.setFont(QFont("SimSun", 10))
        self.notation_list.setMaximumHeight(300)
        layout.addWidget(self.notation_list)
        
        # 弹性空间
        layout.addStretch()
        
        self.setLayout(layout)
        self.setFixedWidth(300)
    
    def _create_settings_group(self) -> QGroupBox:
        """创建设置区域"""
        group = QGroupBox("游戏设置")
        group.setFont(QFont("SimHei", 11, QFont.Bold))
        layout = QVBoxLayout()
        
        # 主题选择
        theme_label = QLabel("界面主题:")
        layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "深色青色", "深色蓝色", "深色紫色", "深色琥珀色",
            "深色红色", "深色粉色", "深色绿色", "深色黄色", "深色青蓝",
            "浅色青色", "浅色蓝色", "浅色紫色", "浅色琥珀色",
            "浅色红色", "浅色粉色", "浅色绿色", "浅色黄色", "浅色青蓝", "浅色青蓝500"
        ])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        layout.addWidget(self.theme_combo)
        
        # 模式选择
        mode_label = QLabel("游戏模式:")
        layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["人机对战", "人人对战"])
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        layout.addWidget(self.mode_combo)
        
        # 难度选择
        self.difficulty_label = QLabel("难度等级:")
        layout.addWidget(self.difficulty_label)
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["小白", "初级", "中级", "高级", "大师"])
        self.difficulty_combo.setCurrentText("中级")
        layout.addWidget(self.difficulty_combo)
        
        # 执子选择
        self.color_label = QLabel("执子选择:")
        layout.addWidget(self.color_label)
        
        color_layout = QHBoxLayout()
        self.color_button_group = QButtonGroup()
        
        self.red_radio = QRadioButton("执红(先手)")
        self.red_radio.setChecked(True)
        self.color_button_group.addButton(self.red_radio)
        color_layout.addWidget(self.red_radio)
        
        self.black_radio = QRadioButton("执黑(后手)")
        self.color_button_group.addButton(self.black_radio)
        color_layout.addWidget(self.black_radio)
        
        layout.addLayout(color_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_actions_group(self) -> QGroupBox:
        """创建操作按钮区域"""
        group = QGroupBox("游戏操作")
        group.setFont(QFont("SimHei", 11, QFont.Bold))
        layout = QVBoxLayout()
        
        # 开始游戏按钮
        self.start_button = QPushButton("开始游戏")
        self.start_button.setFont(QFont("SimHei", 12))
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.start_game_clicked.emit)
        layout.addWidget(self.start_button)
        
        # 其他操作按钮(默认禁用)
        buttons_layout = QVBoxLayout()
        
        self.undo_button = QPushButton("悔棋")
        self.undo_button.setEnabled(False)
        self.undo_button.clicked.connect(self.undo_clicked.emit)
        buttons_layout.addWidget(self.undo_button)
        
        self.hint_button = QPushButton("智能提示")
        self.hint_button.setEnabled(False)
        self.hint_button.clicked.connect(self.hint_clicked.emit)
        buttons_layout.addWidget(self.hint_button)
        
        self.resign_button = QPushButton("认输")
        self.resign_button.setEnabled(False)
        self.resign_button.clicked.connect(self.resign_clicked.emit)
        buttons_layout.addWidget(self.resign_button)
        
        layout.addLayout(buttons_layout)
        
        group.setLayout(layout)
        return group
    
    def _on_theme_changed(self, theme_name: str):
        """主题改变时的处理"""
        theme_map = {
            "深色青色": "dark_teal.xml",
            "深色蓝色": "dark_blue.xml",
            "深色紫色": "dark_purple.xml",
            "深色琥珀色": "dark_amber.xml",
            "深色红色": "dark_red.xml",
            "深色粉色": "dark_pink.xml",
            "深色绿色": "dark_lightgreen.xml",
            "深色黄色": "dark_yellow.xml",
            "深色青蓝": "dark_cyan.xml",
            "浅色青色": "light_teal.xml",
            "浅色蓝色": "light_blue.xml",
            "浅色紫色": "light_purple.xml",
            "浅色琥珀色": "light_amber.xml",
            "浅色红色": "light_red.xml",
            "浅色粉色": "light_pink.xml",
            "浅色绿色": "light_lightgreen.xml",
            "浅色黄色": "light_yellow.xml",
            "浅色青蓝": "light_cyan.xml",
            "浅色青蓝500": "light_cyan_500.xml"
        }
        theme_file = theme_map.get(theme_name, "dark_teal.xml")
        self.theme_changed.emit(theme_file)
    
    def _on_mode_changed(self, mode: str):
        """模式改变时的处理"""
        is_pve = (mode == "人机对战")
        
        # PVE模式下启用难度和执子选择
        self.difficulty_label.setEnabled(is_pve)
        self.difficulty_combo.setEnabled(is_pve)
        self.color_label.setEnabled(is_pve)
        self.red_radio.setEnabled(is_pve)
        self.black_radio.setEnabled(is_pve)
        self.hint_button.setEnabled(False)  # 开始游戏后才启用
    
    def get_settings(self) -> tuple[str, str, str]:
        """
        获取当前设置
        
        Returns:
            (mode, difficulty, player_color)
        """
        mode = "PVE" if self.mode_combo.currentText() == "人机对战" else "PVP"
        difficulty = self.difficulty_combo.currentText()
        player_color = "RED" if self.red_radio.isChecked() else "BLACK"
        
        return mode, difficulty, player_color
    
    def set_game_active(self, active: bool):
        """设置游戏活动状态"""
        # 禁用/启用设置
        self.mode_combo.setEnabled(not active)
        self.difficulty_combo.setEnabled(not active)
        self.red_radio.setEnabled(not active)
        self.black_radio.setEnabled(not active)
        
        # 启用/禁用操作按钮
        if active:
            self.start_button.setText("重新开始")
            self.undo_button.setEnabled(True)
            self.hint_button.setEnabled(True)
            self.resign_button.setEnabled(True)
        else:
            self.start_button.setText("开始游戏")
            self.undo_button.setEnabled(False)
            self.hint_button.setEnabled(False)
            self.resign_button.setEnabled(False)
    
    def add_notation(self, notation: str):
        """添加棋谱记录"""
        move_number = self.notation_list.count() + 1
        text = f"{move_number}. {notation}"
        self.notation_list.addItem(text)
        self.notation_list.scrollToBottom()
    
    def clear_notation(self):
        """清空棋谱记录"""
        self.notation_list.clear()
    
    def set_status(self, text: str, color: str = "blue"):
        """设置状态文本"""
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")
    
    def show_thinking(self, show: bool):
        """显示/隐藏思考进度条"""
        self.progress_bar.setVisible(show)
        if show:
            self.set_status("AI思考中...", "orange")
            self.hint_button.setEnabled(False)
        else:
            self.hint_button.setEnabled(True)
    
    def enable_hint(self, enabled: bool):
        """启用/禁用提示按钮"""
        self.hint_button.setEnabled(enabled)
