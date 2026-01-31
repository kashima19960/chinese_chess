"""High-performance Alpha-Beta search engine for Chinese Chess.

This module implements a state-of-the-art chess search engine with
modern optimization techniques used in top engines like Stockfish.

Key Features:
    - Principal Variation Search (PVS)
    - Transposition Table with Zobrist Hashing
    - Quiescence Search with SEE
    - Late Move Reductions (LMR)
    - Null Move Pruning
    - Killer Move Heuristic
    - History Heuristic
    - Aspiration Windows
    - Iterative Deepening

Typical usage example:
    engine = SearchEngine()
    best_move = engine.search(board, depth=6)
"""

import random
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, Final, List, Optional, Tuple

from core.board import Board
from core.constants import (
    ALL_PIECES,
    BLACK,
    BOARD_COLS,
    BOARD_ROWS,
    PIECE_VALUES,
    RED,
    get_piece_color,
)
from core.rules import RuleEngine

from ai.nnue import nnue_evaluate

# Type alias for moves
Move = Tuple[Tuple[int, int], Tuple[int, int]]


# =============================================================================
# Constants
# =============================================================================
INFINITY: Final[int] = 999999
MATE_SCORE: Final[int] = 100000
MATE_THRESHOLD: Final[int] = MATE_SCORE - 1000

# Transposition table entry types
class TTFlag(IntEnum):
    """Transposition table entry flag types."""
    EXACT = 0      # Exact score
    ALPHA = 1      # Upper bound (fail-low)
    BETA = 2       # Lower bound (fail-high)


# LMR reduction table (indexed by depth and move number)
LMR_TABLE: List[List[int]] = []
for d in range(64):
    LMR_TABLE.append([])
    for m in range(64):
        if d == 0 or m == 0:
            LMR_TABLE[d].append(0)
        else:
            import math
            LMR_TABLE[d].append(int(0.75 + math.log(d) * math.log(m) / 2.25))


# =============================================================================
# Zobrist Hashing
# =============================================================================
class ZobristHash:
    """Zobrist hashing for board positions.
    
    Zobrist hashing creates a unique 64-bit hash for each board position
    using XOR operations, allowing efficient incremental updates.
    """
    
    def __init__(self, seed: int = 12345) -> None:
        """Initialize Zobrist hash tables.
        
        Args:
            seed: Random seed for reproducible hash values.
        """
        random.seed(seed)
        
        # Hash values for each piece on each square
        # Index: [piece_index][square]
        self.piece_table: Dict[str, List[int]] = {}
        
        for piece in ALL_PIECES:
            self.piece_table[piece] = [
                random.getrandbits(64) for _ in range(BOARD_ROWS * BOARD_COLS)
            ]
        
        # Hash value for side to move
        self.side_to_move: int = random.getrandbits(64)
    
    def hash_board(self, board: Board) -> int:
        """Compute the full Zobrist hash of a board position.
        
        Args:
            board: The board to hash.
        
        Returns:
            64-bit hash value.
        """
        h = 0
        
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = board.get_piece(row, col)
                if piece:
                    sq = row * BOARD_COLS + col
                    h ^= self.piece_table[piece][sq]
        
        if board.current_player == BLACK:
            h ^= self.side_to_move
        
        return h
    
    def update_piece(
        self,
        h: int,
        piece: str,
        row: int,
        col: int
    ) -> int:
        """Update hash for adding/removing a piece.
        
        Args:
            h: Current hash value.
            piece: The piece being added/removed.
            row: Board row.
            col: Board column.
        
        Returns:
            Updated hash value.
        """
        sq = row * BOARD_COLS + col
        return h ^ self.piece_table[piece][sq]
    
    def toggle_side(self, h: int) -> int:
        """Toggle the side to move in the hash.
        
        Args:
            h: Current hash value.
        
        Returns:
            Updated hash value.
        """
        return h ^ self.side_to_move


# =============================================================================
# Transposition Table
# =============================================================================
@dataclass
class TTEntry:
    """Transposition table entry.
    
    Attributes:
        key: Full hash key for verification.
        depth: Search depth of this entry.
        score: Evaluation score.
        flag: Type of score (exact, alpha, beta).
        best_move: Best move found at this position.
        age: Search generation for replacement.
    """
    key: int = 0
    depth: int = 0
    score: int = 0
    flag: TTFlag = TTFlag.EXACT
    best_move: Optional[Move] = None
    age: int = 0


class TranspositionTable:
    """Transposition table for storing search results.
    
    Uses a fixed-size hash table with replacement scheme based on
    depth and age.
    """
    
    def __init__(self, size_mb: int = 64) -> None:
        """Initialize the transposition table.
        
        Args:
            size_mb: Table size in megabytes.
        """
        # Estimate entries based on size
        entry_size = 64  # Approximate bytes per entry
        self.size = (size_mb * 1024 * 1024) // entry_size
        self.table: Dict[int, TTEntry] = {}
        self.generation: int = 0
    
    def clear(self) -> None:
        """Clear the transposition table."""
        self.table.clear()
        self.generation = 0
    
    def new_search(self) -> None:
        """Increment generation for new search."""
        self.generation += 1
    
    def probe(self, key: int) -> Optional[TTEntry]:
        """Look up a position in the table.
        
        Args:
            key: Zobrist hash key.
        
        Returns:
            TTEntry if found, None otherwise.
        """
        idx = key % self.size
        entry = self.table.get(idx)
        
        if entry and entry.key == key:
            return entry
        return None
    
    def store(
        self,
        key: int,
        depth: int,
        score: int,
        flag: TTFlag,
        best_move: Optional[Move]
    ) -> None:
        """Store a position in the table.
        
        Args:
            key: Zobrist hash key.
            depth: Search depth.
            score: Evaluation score.
            flag: Score type flag.
            best_move: Best move found.
        """
        idx = key % self.size
        existing = self.table.get(idx)
        
        # Replacement strategy:
        # - Always replace if empty
        # - Replace if new entry has greater depth
        # - Replace if existing entry is from old search
        should_replace = (
            existing is None or
            existing.age < self.generation or
            existing.depth <= depth
        )
        
        if should_replace:
            self.table[idx] = TTEntry(
                key=key,
                depth=depth,
                score=score,
                flag=flag,
                best_move=best_move,
                age=self.generation
            )


# =============================================================================
# Move Ordering
# =============================================================================
@dataclass
class MoveOrderer:
    """Move ordering heuristics for better pruning.
    
    Good move ordering is crucial for alpha-beta efficiency.
    This class manages:
    - Killer moves (quiet moves that caused beta cutoffs)
    - History heuristic (historically good moves)
    - Counter moves
    """
    
    # Killer moves per ply (2 slots)
    killers: List[List[Optional[Move]]] = field(default_factory=list)
    
    # History heuristic: [piece_type][to_square] -> score
    history: Dict[str, List[int]] = field(default_factory=dict)
    
    # Counter move heuristic
    counter_moves: Dict[Move, Move] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize data structures."""
        self.killers = [[None, None] for _ in range(64)]
        self.history = {p: [0] * 90 for p in ALL_PIECES}
    
    def clear(self) -> None:
        """Clear all move ordering data."""
        self.killers = [[None, None] for _ in range(64)]
        for piece in self.history:
            self.history[piece] = [0] * 90
        self.counter_moves.clear()
    
    def update_killer(self, move: Move, ply: int) -> None:
        """Update killer moves for a ply.
        
        Args:
            move: The move that caused a cutoff.
            ply: Current search ply.
        """
        if ply < 64:
            if self.killers[ply][0] != move:
                self.killers[ply][1] = self.killers[ply][0]
                self.killers[ply][0] = move
    
    def update_history(
        self,
        board: Board,
        move: Move,
        depth: int,
        is_good: bool
    ) -> None:
        """Update history heuristic for a move.
        
        Args:
            board: Current board state.
            move: The move to update.
            depth: Search depth (used for bonus scaling).
            is_good: Whether this was a good move (caused cutoff).
        """
        from_pos, to_pos = move
        piece = board.get_piece(from_pos[0], from_pos[1])
        if piece:
            to_sq = to_pos[0] * BOARD_COLS + to_pos[1]
            bonus = depth * depth
            if is_good:
                self.history[piece][to_sq] += bonus
            else:
                self.history[piece][to_sq] -= bonus
            
            # Cap history values
            self.history[piece][to_sq] = max(-8000, min(8000, self.history[piece][to_sq]))
    
    def get_history_score(self, board: Board, move: Move) -> int:
        """Get history heuristic score for a move.
        
        Args:
            board: Current board state.
            move: The move to score.
        
        Returns:
            History score.
        """
        from_pos, to_pos = move
        piece = board.get_piece(from_pos[0], from_pos[1])
        if piece:
            to_sq = to_pos[0] * BOARD_COLS + to_pos[1]
            return self.history[piece][to_sq]
        return 0
    
    def is_killer(self, move: Move, ply: int) -> bool:
        """Check if a move is a killer move.
        
        Args:
            move: The move to check.
            ply: Current search ply.
        
        Returns:
            True if move is a killer.
        """
        if ply < 64:
            return move in self.killers[ply]
        return False


def mvv_lva_score(board: Board, move: Move) -> int:
    """Calculate MVV-LVA (Most Valuable Victim - Least Valuable Attacker) score.
    
    This ordering prioritizes capturing valuable pieces with cheap pieces.
    
    Args:
        board: Current board state.
        move: The capture move.
    
    Returns:
        MVV-LVA score (higher is better).
    """
    from_pos, to_pos = move
    
    attacker = board.get_piece(from_pos[0], from_pos[1])
    victim = board.get_piece(to_pos[0], to_pos[1])
    
    if victim is None:
        return 0
    
    victim_value = PIECE_VALUES.get(victim, 0)
    attacker_value = PIECE_VALUES.get(attacker, 0)
    
    # Score = 10 * victim_value - attacker_value
    # This prioritizes high value victims and low value attackers
    return 10 * victim_value - attacker_value


def order_moves(
    board: Board,
    moves: List[Move],
    tt_move: Optional[Move],
    orderer: MoveOrderer,
    ply: int
) -> List[Move]:
    """Order moves for better alpha-beta pruning.
    
    Move ordering priority:
    1. TT move (hash move)
    2. Winning captures (MVV-LVA)
    3. Killer moves
    4. History heuristic
    5. Losing captures
    
    Args:
        board: Current board state.
        moves: List of legal moves.
        tt_move: Best move from transposition table.
        orderer: Move orderer with killer/history data.
        ply: Current search ply.
    
    Returns:
        Ordered list of moves.
    """
    scored_moves = []
    
    for move in moves:
        score = 0
        
        # TT move gets highest priority
        if move == tt_move:
            score = 1000000
        else:
            from_pos, to_pos = move
            captured = board.get_piece(to_pos[0], to_pos[1])
            
            if captured:
                # Capture move - use MVV-LVA
                score = 100000 + mvv_lva_score(board, move)
            elif orderer.is_killer(move, ply):
                # Killer move
                score = 90000
            else:
                # History heuristic for quiet moves
                score = orderer.get_history_score(board, move)
        
        scored_moves.append((score, move))
    
    # Sort by score descending
    scored_moves.sort(key=lambda x: x[0], reverse=True)
    
    return [move for _, move in scored_moves]


# =============================================================================
# Search Engine
# =============================================================================
@dataclass
class SearchStats:
    """Statistics from a search.
    
    Attributes:
        nodes: Total nodes searched.
        qnodes: Quiescence nodes searched.
        tt_hits: Transposition table hits.
        tt_cutoffs: TT cutoffs.
        null_cutoffs: Null move pruning cutoffs.
        lmr_reductions: Late move reductions applied.
        time_ms: Search time in milliseconds.
    """
    nodes: int = 0
    qnodes: int = 0
    tt_hits: int = 0
    tt_cutoffs: int = 0
    null_cutoffs: int = 0
    lmr_reductions: int = 0
    time_ms: float = 0.0


class SearchEngine:
    """High-performance Alpha-Beta search engine.
    
    This engine implements modern search techniques for optimal
    move selection in Chinese Chess.
    """
    
    def __init__(self, tt_size_mb: int = 64) -> None:
        """Initialize the search engine.
        
        Args:
            tt_size_mb: Transposition table size in megabytes.
        """
        self.tt = TranspositionTable(tt_size_mb)
        self.zobrist = ZobristHash()
        self.orderer = MoveOrderer()
        self.stats = SearchStats()
        
        # Search control
        self._stop_search = False
        self._start_time = 0.0
        self._time_limit = float('inf')
        
        # Principal variation
        self._pv: List[List[Move]] = [[]]
    
    def clear(self) -> None:
        """Clear all search state."""
        self.tt.clear()
        self.orderer.clear()
    
    def search(
        self,
        board: Board,
        depth: int = 6,
        time_limit: Optional[float] = None
    ) -> Optional[Move]:
        """Search for the best move using iterative deepening.
        
        Args:
            board: Current board position.
            depth: Maximum search depth.
            time_limit: Time limit in seconds (optional).
        
        Returns:
            Best move found, or None if no legal moves.
        """
        self._stop_search = False
        self._start_time = time.time()
        self._time_limit = time_limit if time_limit else float('inf')
        
        # Reset statistics
        self.stats = SearchStats()
        self.tt.new_search()
        
        best_move: Optional[Move] = None
        best_score = -INFINITY
        
        # Iterative deepening
        for d in range(1, depth + 1):
            if self._should_stop():
                break
            
            # Aspiration window search
            alpha = -INFINITY if d <= 1 else best_score - 50
            beta = INFINITY if d <= 1 else best_score + 50
            
            score, move = self._search_root(board, d, alpha, beta)
            
            # Re-search with full window if outside aspiration
            if score <= alpha or score >= beta:
                score, move = self._search_root(board, d, -INFINITY, INFINITY)
            
            if not self._should_stop() and move:
                best_move = move
                best_score = score
        
        self.stats.time_ms = (time.time() - self._start_time) * 1000
        
        return best_move
    
    def _should_stop(self) -> bool:
        """Check if search should stop due to time limit.
        
        Returns:
            True if search should stop.
        """
        if self._stop_search:
            return True
        if time.time() - self._start_time > self._time_limit:
            self._stop_search = True
            return True
        return False
    
    def _search_root(
        self,
        board: Board,
        depth: int,
        alpha: int,
        beta: int
    ) -> Tuple[int, Optional[Move]]:
        """Search from the root position.
        
        Args:
            board: Current board position.
            depth: Search depth.
            alpha: Alpha bound.
            beta: Beta bound.
        
        Returns:
            Tuple of (score, best_move).
        """
        rule_engine = RuleEngine(board)
        moves = self._generate_moves(board, rule_engine)
        
        if not moves:
            return -MATE_SCORE, None
        
        # Get TT move for ordering
        hash_key = self.zobrist.hash_board(board)
        tt_entry = self.tt.probe(hash_key)
        tt_move = tt_entry.best_move if tt_entry else None
        
        # Order moves
        moves = order_moves(board, moves, tt_move, self.orderer, 0)
        
        best_move = moves[0]
        best_score = -INFINITY
        
        for i, move in enumerate(moves):
            if self._should_stop():
                break
            
            # Make move
            new_board = board.copy()
            new_board.move_piece(move[0], move[1])
            
            # PVS: Full window for first move, null window for rest
            if i == 0:
                score = -self._search(new_board, depth - 1, -beta, -alpha, 1, True)
            else:
                # Late Move Reduction
                reduction = 0
                if i >= 4 and depth >= 3:
                    reduction = LMR_TABLE[min(depth, 63)][min(i, 63)]
                    self.stats.lmr_reductions += 1
                
                # Null window search with reduction
                score = -self._search(
                    new_board, depth - 1 - reduction,
                    -alpha - 1, -alpha, 1, True
                )
                
                # Re-search if fail high
                if score > alpha:
                    score = -self._search(new_board, depth - 1, -beta, -alpha, 1, True)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            if score > alpha:
                alpha = score
            
            if alpha >= beta:
                break
        
        # Store in TT
        flag = TTFlag.EXACT
        if best_score <= alpha:
            flag = TTFlag.ALPHA
        elif best_score >= beta:
            flag = TTFlag.BETA
        
        self.tt.store(hash_key, depth, best_score, flag, best_move)
        
        return best_score, best_move
    
    def _search(
        self,
        board: Board,
        depth: int,
        alpha: int,
        beta: int,
        ply: int,
        can_null: bool
    ) -> int:
        """Recursive alpha-beta search.
        
        Args:
            board: Current board position.
            depth: Remaining search depth.
            alpha: Alpha bound.
            beta: Beta bound.
            ply: Current ply from root.
            can_null: Whether null move pruning is allowed.
        
        Returns:
            Position evaluation score.
        """
        self.stats.nodes += 1
        
        # Check for stop
        if self._should_stop():
            return 0
        
        # Mate distance pruning
        alpha = max(alpha, -MATE_SCORE + ply)
        beta = min(beta, MATE_SCORE - ply)
        if alpha >= beta:
            return alpha
        
        # Transposition table lookup
        hash_key = self.zobrist.hash_board(board)
        tt_entry = self.tt.probe(hash_key)
        tt_move = None
        
        if tt_entry:
            self.stats.tt_hits += 1
            tt_move = tt_entry.best_move
            
            if tt_entry.depth >= depth:
                score = tt_entry.score
                
                # Adjust mate scores for ply
                if score > MATE_THRESHOLD:
                    score -= ply
                elif score < -MATE_THRESHOLD:
                    score += ply
                
                if tt_entry.flag == TTFlag.EXACT:
                    self.stats.tt_cutoffs += 1
                    return score
                elif tt_entry.flag == TTFlag.ALPHA and score <= alpha:
                    self.stats.tt_cutoffs += 1
                    return alpha
                elif tt_entry.flag == TTFlag.BETA and score >= beta:
                    self.stats.tt_cutoffs += 1
                    return beta
        
        rule_engine = RuleEngine(board)
        
        # Check for game over
        result = rule_engine.get_game_result()
        if result is not None:
            if result == board.current_player:
                return MATE_SCORE - ply
            else:
                return -MATE_SCORE + ply
        
        # Quiescence search at depth 0
        if depth <= 0:
            return self._quiescence(board, alpha, beta, ply)
        
        # Null Move Pruning
        if can_null and depth >= 3 and not self._is_in_check(board, rule_engine):
            # Make null move (pass turn)
            null_board = board.copy()
            null_board.current_player = -null_board.current_player
            
            # Reduced depth search
            reduction = 3 + depth // 4
            score = -self._search(
                null_board, depth - 1 - reduction,
                -beta, -beta + 1, ply + 1, False
            )
            
            if score >= beta:
                self.stats.null_cutoffs += 1
                return beta
        
        # Generate and order moves
        moves = self._generate_moves(board, rule_engine)
        
        if not moves:
            # No legal moves - checkmate or stalemate
            if self._is_in_check(board, rule_engine):
                return -MATE_SCORE + ply
            return 0
        
        moves = order_moves(board, moves, tt_move, self.orderer, ply)
        
        best_move = moves[0]
        best_score = -INFINITY
        moves_searched = 0
        
        for i, move in enumerate(moves):
            # Make move
            new_board = board.copy()
            captured = new_board.move_piece(move[0], move[1])
            
            # PVS with LMR
            if i == 0:
                score = -self._search(new_board, depth - 1, -beta, -alpha, ply + 1, True)
            else:
                # Late Move Reduction
                reduction = 0
                is_quiet = captured is None
                
                if (is_quiet and moves_searched >= 4 and depth >= 3 and
                        not self.orderer.is_killer(move, ply)):
                    reduction = LMR_TABLE[min(depth, 63)][min(moves_searched, 63)]
                    self.stats.lmr_reductions += 1
                
                # Null window search
                score = -self._search(
                    new_board, depth - 1 - reduction,
                    -alpha - 1, -alpha, ply + 1, True
                )
                
                # Re-search if fail high
                if score > alpha and (score < beta or reduction > 0):
                    score = -self._search(
                        new_board, depth - 1,
                        -beta, -alpha, ply + 1, True
                    )
            
            moves_searched += 1
            
            if score > best_score:
                best_score = score
                best_move = move
            
            if score > alpha:
                alpha = score
            
            if alpha >= beta:
                # Update killer moves for quiet moves
                if captured is None:
                    self.orderer.update_killer(move, ply)
                    self.orderer.update_history(board, move, depth, True)
                break
        
        # Store in TT
        flag = TTFlag.EXACT
        if best_score <= alpha:
            flag = TTFlag.ALPHA
        elif best_score >= beta:
            flag = TTFlag.BETA
        
        self.tt.store(hash_key, depth, best_score, flag, best_move)
        
        return best_score
    
    def _quiescence(
        self,
        board: Board,
        alpha: int,
        beta: int,
        ply: int
    ) -> int:
        """Quiescence search to resolve tactical positions.
        
        Only searches captures to avoid horizon effect.
        
        Args:
            board: Current board position.
            alpha: Alpha bound.
            beta: Beta bound.
            ply: Current ply from root.
        
        Returns:
            Position evaluation score.
        """
        self.stats.qnodes += 1
        
        # Stand pat
        stand_pat = nnue_evaluate(board, board.current_player)
        
        if stand_pat >= beta:
            return beta
        
        if stand_pat > alpha:
            alpha = stand_pat
        
        # Generate capture moves only
        rule_engine = RuleEngine(board)
        moves = self._generate_captures(board, rule_engine)
        
        # Order by MVV-LVA
        moves.sort(key=lambda m: mvv_lva_score(board, m), reverse=True)
        
        for move in moves:
            # Delta pruning: skip if capture doesn't help enough
            captured = board.get_piece(move[1][0], move[1][1])
            if captured:
                delta = stand_pat + PIECE_VALUES.get(captured, 0) + 200
                if delta < alpha:
                    continue
            
            # Make move
            new_board = board.copy()
            new_board.move_piece(move[0], move[1])
            
            score = -self._quiescence(new_board, -beta, -alpha, ply + 1)
            
            if score >= beta:
                return beta
            
            if score > alpha:
                alpha = score
        
        return alpha
    
    def _generate_moves(
        self,
        board: Board,
        rule_engine: RuleEngine
    ) -> List[Move]:
        """Generate all legal moves.
        
        Args:
            board: Current board position.
            rule_engine: Rule engine for move validation.
        
        Returns:
            List of legal moves.
        """
        moves = []
        pieces = board.get_all_pieces(board.current_player)
        
        for r, c, piece in pieces:
            legal_moves = rule_engine.get_legal_moves(r, c)
            for to_pos in legal_moves:
                moves.append(((r, c), to_pos))
        
        return moves
    
    def _generate_captures(
        self,
        board: Board,
        rule_engine: RuleEngine
    ) -> List[Move]:
        """Generate only capture moves.
        
        Args:
            board: Current board position.
            rule_engine: Rule engine for move validation.
        
        Returns:
            List of capture moves.
        """
        moves = []
        pieces = board.get_all_pieces(board.current_player)
        
        for r, c, piece in pieces:
            legal_moves = rule_engine.get_legal_moves(r, c)
            for to_pos in legal_moves:
                captured = board.get_piece(to_pos[0], to_pos[1])
                if captured:
                    moves.append(((r, c), to_pos))
        
        return moves
    
    def _is_in_check(self, board: Board, rule_engine: RuleEngine) -> bool:
        """Check if current player is in check.
        
        Args:
            board: Current board position.
            rule_engine: Rule engine.
        
        Returns:
            True if in check.
        """
        return rule_engine.is_in_check(board.current_player)


# =============================================================================
# Difficulty Settings
# =============================================================================
DIFFICULTY_CONFIG: Dict[str, Dict] = {
    '小白': {'depth': 2, 'time_limit': 0.5},
    '初级': {'depth': 3, 'time_limit': 1.0},
    '中级': {'depth': 4, 'time_limit': 2.0},
    '高级': {'depth': 5, 'time_limit': 4.0},
    '大师': {'depth': 6, 'time_limit': 8.0},
}


# =============================================================================
# Global Engine Instance
# =============================================================================
_engine: Optional[SearchEngine] = None


def get_search_engine() -> SearchEngine:
    """Get the global search engine instance.
    
    Returns:
        The singleton SearchEngine instance.
    """
    global _engine
    if _engine is None:
        _engine = SearchEngine(tt_size_mb=128)
    return _engine


def search_best_move(
    board: Board,
    difficulty: str = '中级'
) -> Optional[Move]:
    """Search for the best move at given difficulty.
    
    Args:
        board: Current board position.
        difficulty: Difficulty level.
    
    Returns:
        Best move found.
    """
    config = DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG['中级'])
    engine = get_search_engine()
    
    return engine.search(
        board,
        depth=config['depth'],
        time_limit=config['time_limit']
    )
