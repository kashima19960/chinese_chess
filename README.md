# 中国象棋 (Chinese Chess)

一个基于PySide6开发的中国象棋游戏，支持人人对战(PVP)和人机对战(PVE)模式。

[English](README_EN.md)

## 功能特点

### 核心功能
- ✅ 完整的中国象棋规则引擎
- ✅ FEN格式棋盘状态管理
- ✅ 标准中文记谱（如"炮二平五"）
- ✅ 将军、将死、困毙判定
- ✅ 马腿、象眼、飞将检测

### AI功能
- ✅ 5个难度等级（小白→大师）
- ✅ NNUE（高效可更新神经网络）评估
- ✅ 高性能 Alpha-Beta 搜索（PVS/LMR/空着剪枝/静态搜索/置换表）
- ✅ 走法排序（MVV-LVA、Killer/History）
- ✅ 迭代加深 + 期望窗口（Aspiration Windows）
- ✅ 异步计算（不阻塞UI）
- ✅ 智能提示功能

### 界面功能
- ✅ 无边框现代化界面
- ✅ 自定义标题栏（可拖动、最小化、最大化）
- ✅ 木纹棋盘背景
- ✅ 棋子移动动画效果
- ✅ 选中高亮+合法移动标记
- ✅ 棋谱实时记录
- ✅ 高DPI屏幕支持（2K/4K）

### 游戏模式
- ✅ 人人对战（PVP）
- ✅ 人机对战（PVE）
- ✅ 执红/执黑选择
- ✅ 悔棋功能
- ✅ 认输功能

## 安装说明

### 环境要求
- Python 3.8+
- Windows 10/11（支持其他操作系统）

### 安装步骤

1. 克隆仓库
```bash
git clone git@github.com:kashima19960/chinese_chess.git
cd chinese_chess
```

2. 创建虚拟环境（推荐）
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行程序
```bash
python main.py
```

## 项目结构

```
chinese_chess/
├── core/               # 核心逻辑模块
│   ├── __init__.py
│   ├── constants.py    # 常量定义
│   ├── board.py        # 棋盘状态管理(FEN解析)
│   ├── rules.py        # 规则引擎(移动验证、将军检测)
│   └── notation.py     # 中文记谱生成
├── ai/                 # AI模块
│   ├── __init__.py
│   ├── evaluation.py   # 评估接口（NNUE为主，经典评估为辅）
│   ├── nnue.py         # NNUE评估网络
│   ├── search_engine.py # 高性能搜索引擎
│   ├── search.py       # 统一搜索接口
│   └── worker.py       # QThread异步计算
├── ui/                 # 界面模块
│   ├── __init__.py
│   ├── styles.py       # 样式常量
│   ├── pieces.py       # 棋子图形项
│   ├── board_view.py   # 棋盘视图(QGraphicsView)
│   └── control_panel.py # 控制面板
├── resources/          # 资源文件
│   ├── app_icon.ico    # Windows图标
│   ├── app_icon.png    # 应用图标
│   └── icon/           # SVG图标资源
├── generate_icon.py    # 图标生成脚本
├── main.py             # 主程序入口
├── 需求设计文档.md     # 设计文档
├── README.md          # 本文件
└── README_EN.md       # 英文README
```

## 使用说明

### 开始游戏
1. 选择游戏模式（人机对战/人人对战）
2. 选择难度等级（人机模式）
3. 选择执子颜色（人机模式）
4. 点击"开始游戏"

### 操作说明
- **移动棋子**: 点击棋子选中，再点击目标位置
- **悔棋**: 点击"悔棋"按钮（PVE模式悔两步）
- **智能提示**: 点击"智能提示"显示最佳走法
- **认输**: 点击"认输"结束游戏

### 窗口操作
- **拖动窗口**: 按住标题栏拖动
- **最大化/还原**: 点击□/❐按钮或双击标题栏
- **最小化**: 点击—按钮
- **关闭**: 点击×按钮

## 技术栈

- **Python 3.8+**: 编程语言
- **PySide6**: GUI框架
- **NNUE**: 高效可更新神经网络评估
- **Alpha-Beta搜索**: 高性能剪枝搜索
- **NumPy**: 数值计算加速

## 开发计划

- [ ] 添加在线对战功能
- [ ] 支持残局库
- [ ] 棋谱导入/导出功能
- [ ] 复盘分析功能
- [ ] 更多AI难度等级
- [ ] 音效支持

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 作者

kashima19960

## 更新日志

### v1.2.0 (2026-02-01)
- 🤖 AI引擎升级：NNUE + 高性能 Alpha-Beta 搜索
- ⚡ 搜索优化：置换表 / LMR / 空着剪枝 / 静态搜索
- 📦 新增 NumPy 依赖与搜索引擎模块

### v1.1.0 (2026-02-01)
- 🔄 从PyQt5迁移到PySide6
- 🎨 UI重设计，采用Soft UI Evolution风格
- 📝 代码重构为Google Python Style Guide规范
- 🌐 新增英文README

### v1.0.0 (2025-11-29)
- 🎉 首次发布
- ✅ 完整的象棋规则引擎
- ✅ AI对战功能（5个难度）
- ✅ 现代化界面
- ✅ 高DPI屏幕支持
