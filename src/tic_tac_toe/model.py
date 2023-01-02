from abc import ABC, abstractmethod
from enum import Enum
from typing import Sequence, Iterable, Generator


class Symbol(Enum):
    X = 'x'
    O = 'o'


def all_equal(lis: Iterable):
    iterator = iter(lis)
    try:
        cv = next(iterator)
        while True:
            if next(iterator) != cv:
                return False
    except StopIteration:
        return True



class GameBoard:
    def __init__(self, size: int):
        self.game_board: list[list] = []  # Column major order
        self.board_size = size

    def initialize_game_board(self):
        size = self.board_size
        self.game_board = []
        for i in range(size):
            self.game_board.append([None] * size)

    def clear(self):
        self.game_board = []
        self.initialize_game_board()

    def __setitem__(self, key, value):
        if type(key) is tuple:
            self.game_board[key[0]][key[1]] = value
        else:
            raise NotImplementedError('Use a tuple to set an item on the GameBoard')

    def __getitem__(self, item):
        if type(item) is slice:
            raise NotImplementedError('What are you doing dumbass?')
        if type(item) is tuple:
            return self.game_board[item[0]][item[1]]
        else:
            return self.game_board[item]

    def __iter__(self):
        for column in self.game_board:
            for item in column:
                yield item

    def place_on_board(self, position: tuple[int, int], symbol: Symbol):
        if self[position] is not None:
            raise ValueError(f'There is already a symbol in position {position}')
        self[position] = symbol

    def __str__(self):
        return str(self.game_board)


class Player:
    def __init__(self, name:str, symbol: Symbol):
        self.name = name
        self.symbol = symbol


class TicTacToeGame:
    def __init__(self, game_board: GameBoard):
        self.board = game_board
        self.players: list[Player] = []
        self.current_player = None
        self.current_player_idx = 0
        self.winner = -1
        self.winning_path = None

    def initialize(self):
        self.board.initialize_game_board()
        self.winner = -1
        self.winning_path = None

    def set_player_turn(self, player: Player):
        self.current_player = player

    def register_turn(self, position: tuple[int, int]):
        if self.is_game_over():
            raise ValueError('Game is over, no placing peices')
        player = self.current_player

        self.board.place_on_board(position, player.symbol)

        try:
            state = self.evaluate_game_state()
            if isinstance(state, Symbol):
                self.game_over(player)
            else:
                self.current_player_idx += 1
                self.current_player_idx %= len(self.players)
                self.current_player = self.players[self.current_player_idx]
        except ValueError:
            self.game_over(None)

    def test_if_path_won(self, path: list[tuple[int,int]]):
        board = self.board
        if all_equal(board[x] for x in path):
            symbol = board[path[0]]
            if isinstance(symbol, Symbol):
                return symbol

    def generate_paths(self) -> Generator[list[tuple[int, int]], None, None]:
        '''
        :raise: ValueError when the game is stalemated
        :return:
        '''
        board = self.board
        size = board.board_size

        for i in range(size):
            yield list((i, j) for j in range(size))
            yield list((j, i) for j in range(size))

        #assuming the gameboard is square
        yield list((i,i) for i in range(size))
        yield list((i, (size-1)-i) for i in range(size))

    def evaluate_game_state(self) -> Symbol | None:
        for path in self.generate_paths():
            if (v:=self.test_if_path_won(path)) is not None:
                self.winning_path = path
                return v

        for val in self.board:
            if val is None:
                return

        raise ValueError('Draw!')

    def game_over(self, winner: Player | None):
        self.winner = winner

    def set_players(self, players: Sequence[Player]):
        self.players = players
        self.current_player = players[0]

    def is_game_over(self) -> bool:
        return self.winner != -1


class TicTacToeGameView(ABC):
    @abstractmethod
    def emit_player_names_set(self, names: tuple[str, str]):
        pass

    @abstractmethod
    def emit_player_move_choice(self, choice: tuple[int, int]):
        pass

    @abstractmethod
    def emit_initialized(self):
        pass

    @abstractmethod
    def recv_game_won(self, winner: str):
        pass

    @abstractmethod
    def recv_game_draw(self):
        pass

    @abstractmethod
    def recv_player_selection_state(self):
        pass

    @abstractmethod
    def recv_game_begin_state(self):
        pass

    @abstractmethod
    def recv_move_inquery(self):
        pass

    @abstractmethod
    def recv_game_board_updated(self, game_board: GameBoard, coordinate=None):
        pass

    @abstractmethod
    def recv_player_turn_begin(self, player: Player):
        pass


class TicTacToeGameViewModel(ABC):
    def __init__(self, game: TicTacToeGame, view: TicTacToeGameView):
        self.game = game
        self.view = view


class ConsoleTicTacToeGameView(TicTacToeGameView):
    def __init__(self):
        self.send_buffer = []
        self.current_player: Player | None = None
        self.emit_initialized()

    def emit_initialized(self):
        self.send_buffer.append('init')

    def print_game_board(self, board: GameBoard):
        for row_idx in range(board.board_size):
            row = [column[row_idx] for column in board.game_board]
            print(row)

    def emit_player_names_set(self, names: tuple[str, str]):
        self.send_buffer.append(names)

    def emit_player_move_choice(self, position: tuple[int, int]):
        self.send_buffer.append(position)

    def recv_game_won(self, winner: Player):
        print(f'Congratulations! {winner.name} is the winner!')

    def recv_game_draw(self):
        print('Draw!! No one has won . . .')

    def recv_player_selection_state(self):
        player1 = input('Please enter player1\'s name: ')
        player2 = input('Please neter player2\'s name: ')
        self.emit_player_names_set((player1, player2))

    def recv_game_begin_state(self):
        pass

    def recv_move_inquery(self):
        column_choice = int(input(f'{self.current_player.name}, which column would you like to put your game piece? '))
        row_choice = int(input(f'{self.current_player.name}, which row would you like to put your game piece? '))
        self.emit_player_move_choice((column_choice, row_choice))

    def recv_game_board_updated(self, game_board: GameBoard, coordinate=None):
        self.print_game_board(game_board)

    def recv_player_turn_begin(self, player: Player):
        self.current_player = player


class ConsoleTicTacToeGameViewModel(TicTacToeGameViewModel):
    def __init__(self, game: TicTacToeGame, view: ConsoleTicTacToeGameView):
        super(ConsoleTicTacToeGameViewModel, self).__init__(game, view)
        self.view: ConsoleTicTacToeGameView = view

    def do_game_loop(self):
        assert 'init' == self.view.send_buffer.pop(0)
        self.view.recv_player_selection_state()
        players = self.view.send_buffer.pop(0)
        self.game.set_players(tuple(Player(x, s) for x,s in zip(players, Symbol)))
        self.view.recv_game_board_updated(self.game.board)
        while not self.game.is_game_over():
            self.view.recv_player_turn_begin(self.game.current_player)
            self.view.recv_move_inquery()
            position = self.view.send_buffer.pop(0)
            self.game.register_turn(position)
            self.view.recv_game_board_updated(self.game.board)
        if self.game.winner is None:
            self.view.recv_game_draw()
        else:
            self.view.recv_game_won(self.game.current_player)


if __name__ == '__main__':
    game = TicTacToeGame(GameBoard(3))
    view = ConsoleTicTacToeGameView()
    vm = ConsoleTicTacToeGameViewModel(game, view)
    vm.do_game_loop()
