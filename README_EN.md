# Chinese Chess (中国象棋)

A Chinese Chess game developed with PySide6, supporting Player vs Player (PVP) and Player vs AI (PVE) modes.

[中文文档](README.md)

## Features

### Core Features
- ✅ Complete Chinese Chess rule engine
- ✅ FEN format board state management
- ✅ Standard Chinese notation (e.g., "炮二平五")
- ✅ Check, checkmate, and stalemate detection
- ✅ Horse leg blocking, elephant eye blocking, flying general detection

### AI Features
- ✅ 5 difficulty levels (Beginner → Master)
- ✅ Minimax search with Alpha-Beta pruning
- ✅ Position value table evaluation
- ✅ Asynchronous computation (non-blocking UI)
- ✅ Smart hint feature

### UI Features
- ✅ Frameless modern interface
- ✅ Custom title bar (draggable, minimize, maximize)
- ✅ Wood-grain chessboard background
- ✅ Piece movement animation
- ✅ Selection highlight + legal move markers
- ✅ Real-time game notation recording
- ✅ High DPI screen support (2K/4K)

### Game Modes
- ✅ Player vs Player (PVP)
- ✅ Player vs AI (PVE)
- ✅ Play as Red/Black selection
- ✅ Undo move feature
- ✅ Resign feature

## Installation

### Requirements
- Python 3.8+
- Windows 10/11 (other OS supported)

### Installation Steps

1. Clone the repository
```bash
git clone git@github.com:kashima19960/chinese_chess.git
cd chinese_chess
```

2. Create virtual environment (recommended)
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies
```bash
pip install PySide6
```

4. Run the program
```bash
python main.py
```

## Project Structure

```
chinese_chess/
├── core/               # Core logic module
│   ├── __init__.py
│   ├── constants.py    # Constants definition
│   ├── board.py        # Board state management (FEN parsing)
│   ├── rules.py        # Rule engine (move validation, check detection)
│   └── notation.py     # Chinese notation generation
├── ai/                 # AI module
│   ├── __init__.py
│   ├── evaluation.py   # Board evaluation function
│   ├── search.py       # Minimax algorithm + Alpha-Beta pruning
│   └── worker.py       # QThread async computation
├── ui/                 # UI module
│   ├── __init__.py
│   ├── styles.py       # Style constants
│   ├── pieces.py       # Piece graphics items
│   ├── board_view.py   # Board view (QGraphicsView)
│   └── control_panel.py # Control panel
├── resources/          # Resource files
│   └── icon/          # SVG icon resources
├── main.py             # Main program entry
├── 需求设计文档.md     # Design document
├── README.md          # Chinese README
└── README_EN.md       # This file
```

## Usage

### Starting a Game
1. Select game mode (PVE/PVP)
2. Select difficulty level (PVE mode)
3. Select piece color (PVE mode)
4. Click "Start Game"

### Controls
- **Move pieces**: Click to select, click destination to move
- **Undo**: Click "Undo" button (undoes 2 moves in PVE mode)
- **Smart hint**: Click "Smart Hint" to show best move
- **Resign**: Click "Resign" to end game

### Window Controls
- **Drag window**: Hold and drag title bar
- **Maximize/Restore**: Click □/❐ button or double-click title bar
- **Minimize**: Click — button
- **Close**: Click × button

## Tech Stack

- **Python 3.8+**: Programming language
- **PySide6**: GUI framework
- **Minimax Algorithm**: AI search algorithm
- **Alpha-Beta Pruning**: Search optimization

## Roadmap

- [ ] Online multiplayer
- [ ] Endgame database support
- [ ] Game notation import/export
- [ ] Game replay analysis
- [ ] More AI difficulty levels
- [ ] Sound effects

## Contributing

Issues and Pull Requests are welcome!

## License

MIT License

## Author

kashima19960

## Changelog

### v1.1.0 (2026-02-01)
- 🔄 Migrated from PyQt5 to PySide6
- 🎨 UI redesign with Soft UI Evolution style
- 📝 Code refactored to Google Python Style Guide
- 🌐 Added English README

### v1.0.0 (2025-11-29)
- 🎉 Initial release
- ✅ Complete chess rule engine
- ✅ AI gameplay (5 difficulty levels)
- ✅ Modern interface
- ✅ High DPI screen support
