import numpy as np
import chess
import hashlib

class ChessMap779:
    def __init__(self):
        self.piece_to_binary = {
            '.': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
            'P': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]),
            'N': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]),
            'B': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]),
            'R': np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]),
            'Q': np.array([0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]),
            'K': np.array([0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]),
            'p': np.array([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]),
            'n': np.array([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]),
            'b': np.array([0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
            'r': np.array([0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
            'q': np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
            'k': np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        }
        # additional cm779 bits are:
        # 0: 0 if white to move, 1 if black to move
        # 1: 1 if white has kingside castling rights, 0 otherwise
        # 2: 1 if white has queenside castling rights, 0 otherwise
        # 3: 1 if black has kingside castling rights, 0 otherwise
        # 4: 1 if black has queenside castling rights, 0 otherwise
        # 5-10: the bit representation of the en passant square

        self.binary_to_piece = {tuple(v): k for k, v in self.piece_to_binary.items()}

    def extract_metadata(self, game):
        return {key: value for key, value in game.headers.items()}

    def generate_game_id(self, metadata):
        # Create a unique game ID based on available metadata
        id_components = [
            metadata.get('Event', ''),
            metadata.get('Site', ''),
            metadata.get('Date', ''),
            metadata.get('Round', ''),
            metadata.get('White', ''),
            metadata.get('Black', '')
        ]
        id_string = '_'.join(filter(None, id_components))
        return hashlib.md5(id_string.encode()).hexdigest()

    def board_to_cm779(self, board):
        pieces_cm779 = np.zeros((64, 12), dtype=int)
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                pieces_cm779[square] = self.piece_to_binary[piece.symbol()]
            else:
                pieces_cm779[square] = self.piece_to_binary['.']

        additional_cm779 = np.zeros(11, dtype=int)
        additional_cm779[0] = 0 if board.turn == chess.WHITE else 1
        additional_cm779[1] = 1 if board.has_kingside_castling_rights(chess.WHITE) else 0
        additional_cm779[2] = 1 if board.has_queenside_castling_rights(chess.WHITE) else 0
        additional_cm779[3] = 1 if board.has_kingside_castling_rights(chess.BLACK) else 0
        additional_cm779[4] = 1 if board.has_queenside_castling_rights(chess.BLACK) else 0
        if board.ep_square is not None:
            ep_square_bin = format(board.ep_square, '06b')
            additional_cm779[5:11] = np.array(list(map(int, ep_square_bin)))

        return np.concatenate((pieces_cm779.flatten(), additional_cm779))

    def split_cm779(self, cm779):
        pieces_cm779 = cm779[:768].reshape((64, 12))
        additional_cm779 = cm779[768:]
        return pieces_cm779, additional_cm779

    def cm779_to_board(self, cm779):
        pieces_cm779, additional_cm779 = self.split_cm779(cm779)
        board = chess.Board(None)
        for square in chess.SQUARES:
            piece_data = tuple(pieces_cm779[square])
            if piece_data != tuple(self.piece_to_binary['.']):
                piece_symbol = self.binary_to_piece[piece_data]
                board.set_piece_at(square, chess.Piece.from_symbol(piece_symbol))

        board.turn = chess.WHITE if additional_cm779[0] == 0 else chess.BLACK
        castling_rights = additional_cm779[1:5]
        board.clean_castling_rights()
        if castling_rights[0] == 1:
            board.castling_rights |= chess.BB_H1
        if castling_rights[1] == 1:
            board.castling_rights |= chess.BB_A1
        if castling_rights[2] == 1:
            board.castling_rights |= chess.BB_H8
        if castling_rights[3] == 1:
            board.castling_rights |= chess.BB_A8

        en_passant_square = int(''.join(map(str, additional_cm779[5:11])), 2)
        if en_passant_square < 64:
            board.ep_square = en_passant_square

        return board

    def board_to_array(self, board):
        array = []
        for rank in range(8):
            row = []
            for file in range(8):
                square = chess.square(file, 7 - rank)
                piece = board.piece_at(square)
                if piece is None:
                    row.append('.')
                else:
                    row.append(piece.symbol())
            array.append(row)
        return array

    def cm779_to_fen(self, cm779):
        board = self.cm779_to_board(cm779)
        return board.fen()

    def visualize_board(self, cm779):
        board = self.cm779_to_board(cm779)
        return str(board)
