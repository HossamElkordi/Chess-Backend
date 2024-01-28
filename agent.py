import chess
import numpy as np
import tensorflow as tf

class GameBoard:
    def __init__(self, mode, fen=None) -> None:
        if fen is None:
            self.board : chess.BaseBoard = chess.Board()
        else:
            self.board : chess.BaseBoard = chess.Board(fen=fen)
        self.pieces: dict = {l: i for i, l in enumerate(list('rnbqkpRNBQKP.'))}
        if mode == 'Single Player':
            self.scoring_model: tf.keras.model = tf.keras.models.load_model('model')
    
    def board2D(self):
        bb = str(self.board).replace(' ', '').split('\n')
        return [list(b) for b in bb]

    def one_hot_encode_peice(self, p) -> np.ndarray:
        arr = np.zeros(len(self.pieces))
        arr[self.pieces[p]] = 1
        return arr
    
    def encode_board(self) -> np.ndarray:
        board_str = str(self.board)
        board_str = board_str.replace(' ', '')
        board_list = []
        for row in board_str.split('\n'):
            row_list = []
            for piece in row:
                row_list.append(self.one_hot_encode_peice(piece))
            board_list.append(row_list)
        return np.array(board_list)
    
    def legal_moves_all(self) -> list:
        ret = []
        for move in self.board.legal_moves:
            ret.append(str(move))
        return ret
    
    def legal_moves_from(self, start: str) -> list:
        ret = []
        for move in self.board.legal_moves:
            move = str(move)
            if move[:2] == start:
                ret.append(move[2:])
        return ret
    
    def make_move(self, move: str) -> None:
        self.board.push_san(move)

    def unmake_move(self) -> None:
        self.board.pop()

    def who(self):
        return self.board.turn

    def score_all_possible_moves(self):
        moves, boards = [], []
        for move in self.board.legal_moves:
            move = str(move)
            moves.append(move)
            self.make_move(move)
            boards.append(self.encode_board())
            self.unmake_move()
        if len(moves) == 0:
            return None
        boards = np.stack(boards)
        scores = self.scoring_model.predict(boards, verbose=0)[:, 0]
        return list(zip(moves, scores))
    
class Agent:
    def __init__(self, diff) -> None:
        if diff == 'easy':
            self.depth = 1
        elif diff == 'medium':
            self.depth = 2
        elif diff == 'hard':
            self.depth = 3
    
    def choose_move(self, board: GameBoard) -> str:
        scores = board.score_all_possible_moves()
        if scores is None:
            return None
        else:
            return max(scores, key=lambda x: x[1])[0] if board.who() == chess.BLACK else max(-scores, key=lambda x: x[1])[0]


class Game:
    def __init__(self, mode, diff=None) -> None:
        self.mode = mode
        self.board = GameBoard(mode=mode)
        if mode == 'Single Player':
            self.agent = Agent(diff=diff)
        
    def play(self, move: str = None):
        if move is None:
            assert self.mode == 'Single Player' and self.board.who() == chess.BLACK
            move = self.agent.choose_move(self.board)
        self.board.make_move(move)
        