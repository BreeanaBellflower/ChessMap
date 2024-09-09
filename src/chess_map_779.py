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

    def board_to_cmr(self, board):
        pieces_cmr = np.zeros((64, 12), dtype=int)
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                pieces_cmr[square] = self.piece_to_binary[piece.symbol()]
            else:
                pieces_cmr[square] = self.piece_to_binary['.']

        additional_cmr = np.zeros(11, dtype=int)
        additional_cmr[0] = 0 if board.turn == chess.WHITE else 1
        additional_cmr[1] = 1 if board.has_kingside_castling_rights(chess.WHITE) else 0
        additional_cmr[2] = 1 if board.has_queenside_castling_rights(chess.WHITE) else 0
        additional_cmr[3] = 1 if board.has_kingside_castling_rights(chess.BLACK) else 0
        additional_cmr[4] = 1 if board.has_queenside_castling_rights(chess.BLACK) else 0
        if board.ep_square is not None:
            ep_square_bin = format(board.ep_square, '06b')
            additional_cmr[5:11] = np.array(list(map(int, ep_square_bin)))

        return np.concatenate((pieces_cmr.flatten(), additional_cmr))

    def split_cmr(self, cmr):
        pieces_cmr = cmr[:768].reshape((64, 12))
        additional_cmr = cmr[768:]
        return pieces_cmr, additional_cmr

    def cmr_to_board(self, cmr):
        pieces_cmr, additional_cmr = self.split_cmr(cmr)
        board = chess.Board(None)
        for square in chess.SQUARES:
            piece_data = tuple(pieces_cmr[square])
            if piece_data != tuple(self.piece_to_binary['.']):
                piece_symbol = self.binary_to_piece[piece_data]
                board.set_piece_at(square, chess.Piece.from_symbol(piece_symbol))

        board.turn = chess.WHITE if additional_cmr[0] == 0 else chess.BLACK
        castling_rights = additional_cmr[1:5]
        board.clean_castling_rights()
        if castling_rights[0] == 1:
            board.castling_rights |= chess.BB_H1
        if castling_rights[1] == 1:
            board.castling_rights |= chess.BB_A1
        if castling_rights[2] == 1:
            board.castling_rights |= chess.BB_H8
        if castling_rights[3] == 1:
            board.castling_rights |= chess.BB_A8

        en_passant_square = int(''.join(map(str, additional_cmr[5:11])), 2)
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

    def cmr_to_fen(self, cmr):
        board = self.cmr_to_board(cmr)
        return board.fen()

    def visualize_board(self, cmr):
        board = self.cmr_to_board(cmr)
        return str(board)

if __name__ == "__main__":
    fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    ]

    converter = ChessMap779()
    for i, fen in enumerate(fens):
        board = chess.Board(fen)
        cmr = converter.board_to_cmr(board)
        cmr_board = converter.cmr_to_board(cmr)
        fen_board_array = converter.board_to_array(board)
        cmr_board_array = converter.board_to_array(cmr_board)
        print("move number", i)
        print("original from fen to board")
        print(board)
        print("converted from fen to cmr to board")
        print(cmr_board)
        print("fen representation of original baord")
        print(board.fen())
        print("fen representation of cmr board (notice the lack of move number)")
        print(cmr_board.fen())
        print("================================================")
        assert np.array_equal(fen_board_array, cmr_board_array), f"Board mismatch at move {i}"
    
    for i, fen in enumerate(fens):
        board = chess.Board(fen)
        cmr = converter.board_to_cmr(board)
        print("cmr representation of board")
        print("move number", i)
        piece_board, rights = converter.split_cmr(cmr)
    
        print("Piece board representation:")
        print(piece_board)

        print("Castling and en passant rights:")
        print(rights)
        print("================================================")