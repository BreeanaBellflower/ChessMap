import pytest
from src.chess_map_267 import ChessMap267
import chess
import numpy as np
import hashlib

def test_array_consistency():
    fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    ]

    for i, fen in enumerate(fens):
        board = chess.Board(fen)
        cm267 = ChessMap267.board_to_cm267(board)
        cm267_board = ChessMap267.cm267_to_board(cm267)
        fen_board_array = ChessMap267.board_to_array(board)
        cm267_board_array = ChessMap267.board_to_array(cm267_board)
        assert np.array_equal(fen_board_array, cm267_board_array), f"Board mismatch at move {i}"

def test_cm267_to_fen_consistency():
    fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    ]

    for i, fen in enumerate(fens):
        board = chess.Board(fen)
        cm267 = ChessMap267.board_to_cm267(board)
        cm267_board = ChessMap267.cm267_to_board(cm267)
        fen_board_array = ChessMap267.board_to_array(board)
        cm267_board_array = ChessMap267.board_to_array(cm267_board)
        # move numbers not preserved in castle representation, remove from fen
        assert np.array_equal(fen_board_array, cm267_board_array), f"Board mismatch at move {i}"
        assert board.fen().split()[:-3] == cm267_board.fen().split()[:-3], f"FEN mismatch at move {i}"

def test_en_passant():
    fens = [
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
    ]

    for i, fen in enumerate(fens):
        board = chess.Board(fen)
        cm267 = ChessMap267.board_to_cm267(board)
        cm267_board = ChessMap267.cm267_to_board(cm267)
        assert board.ep_square == cm267_board.ep_square, f"En passant square mismatch at move {i}"

def test_castling_rights():
    fens = [
        "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
        "r3k2r/8/8/8/8/8/8/R3K2R b kq - 0 1",
        "r3k2r/8/8/8/8/8/8/R3K2R w KQ - 0 1",
        "r3k2r/8/8/8/8/8/8/R3K2R b k - 0 1",
    ]

    for i, fen in enumerate(fens):
        board = chess.Board(fen)
        cm267 = ChessMap267.board_to_cm267(board)
        cm267_board = ChessMap267.cm267_to_board(cm267)
        assert board.castling_rights == cm267_board.castling_rights, f"Castling rights mismatch at move {i}"

def test_extract_metadata():
    game = type('Game', (object,), {'headers': {'Event': 'Test Event', 'Site': 'Test Site'}})()
    metadata = ChessMap267.extract_metadata(game)
    assert metadata == {'Event': 'Test Event', 'Site': 'Test Site'}

def test_generate_game_id():
    metadata = {
        'Event': 'Test Event',
        'Site': 'Test Site',
        'Date': '2023.10.01',
        'Round': '1',
        'White': 'Player1',
        'Black': 'Player2'
    }
    game_id = ChessMap267.generate_game_id(metadata)
    expected_id_string = 'Test Event_Test Site_2023.10.01_1_Player1_Player2'
    expected_game_id = hashlib.md5(expected_id_string.encode()).hexdigest()
    assert game_id == expected_game_id

def test_cm267_to_fen():
    fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    ]

    for fen in fens:
        board = chess.Board(fen)
        cm267 = ChessMap267.board_to_cm267(board)
        fen_from_cm267 = ChessMap267.cm267_to_fen(cm267)
        assert fen_from_cm267.split(' ')[:-3] == fen.split(' ')[:-3], f"FEN mismatch"

def test_visualize_board():
    fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    board = chess.Board(fen)
    cm267 = ChessMap267.board_to_cm267(board)
    board_str = ChessMap267.visualize_board(cm267)
    print(board)
    expected_board_str = """r n b q k b n r
p p p p . p p p
. . . . . . . .
. . . . p . . .
. . . . P . . .
. . . . . . . .
P P P P . P P P
R N B Q K B N R"""
    assert board_str == expected_board_str
