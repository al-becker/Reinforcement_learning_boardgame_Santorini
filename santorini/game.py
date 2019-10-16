import random as random
from typing import List


class Coord:
    def __init__(self, x, y):
        assert 5 > x > -1
        self.x = x
        assert 5 > y > -1
        self.y = y

    def __str__(self):
        return "(" + str(self.x + 1) + "|" + str(self.y + 1) + ")"


class Turn:
    def __init__(self, turn_string):
        while len(turn_string) < 5:
            turn_string += '0'
        self.worker = turn_string[0]
        self.coordW = Coord(int(turn_string[1]), int(turn_string[2]))
        self.coordB = Coord(int(turn_string[3]), int(turn_string[4]))

    def __str__(self):
        return self.worker + self.coordW + self.coordB;


class Worker:
    def __init__(self, gender, owner):
        self.gender = gender
        self.owner = owner

    def __str__(self):
        return self.gender + self.owner;


class Tile:
    def __init__(self, coord):
        self.tower = 0
        self.worker = None
        self.coord = coord
        self.neighbours = []

    def build(self):
        if self.tower < 4:
            if self.worker is None:
                self.tower += 1
            else:
                raise ValueError('tried to build on worker tile')
        else:
            raise ValueError('can\'t build on complete tower')

    def __str__(self):
        return self.coord + " (" + self.tower + ") " + self.worker;


class Move:
    # Set start and build to None to describe an initial worker placement move
    def __init__(self, start, to, build):
        """

		:type start: Coord or None
		:type to: Coord
		:type build: Coord or None
		"""
        self.start = start
        self.to = to
        self.build = build

    def __str__(self):
        if self.start is not None:
            return "Move from " + str(self.start) + " to " + str(self.to) + ", building at " + str(self.build) + "."
        else:
            return "Placing worker at " + str(self.to) + "."

    def serialize(self):
        return ((str(self.start.x) if self.start is not None else "9") +
                (str(self.start.y) if self.start is not None else "9") +
                str(self.to.x) +
                str(self.to.y) +
                (str(self.build.x) if self.build is not None else "9") +
                (str(self.build.y) if self.build is not None else "9"))

    def deserialize(self, data: str):
        assert len(data) == 6

        if data[0] == 9:
            self.start = None
        else:
            self.start = Coord(int(data[0]), int(data[1]))

        self.to = Coord(int(data[2]), int(data[3]))

        if data[4] == 9:
            self.build = None
        else:
            self.build = Coord(int(data[4]), int(data[5]))


class Game:
    board: List[List[Tile]]

    def __init__(self):
        random.seed()  # initialize with system time

        self.board = [[None for i in range(5)] for i in range(5)]
        for x in range(5):
            for y in range(5):
                self.board[x][y] = Tile(Coord(x, y))
        self.initialize_neighbours()
        self.stage = 0
        self.active_player = 0
        self.workers = []
        self.winner = None
        self.playedturns = 0

        self.allmoves = []
        for tile_column in self.board:
            for current_tile in tile_column:
                for move_tile in current_tile.neighbours:
                    for build_tile in move_tile.neighbours:
                        self.allmoves.append(Move(current_tile.coord, move_tile.coord, build_tile.coord))

    def get_tile(self, coordinates: Coord) -> Tile:
        return self.board[coordinates.x][coordinates.y]

    def get_current_state(self):
        state = []
        towers = [[None for i in range(5)] for i in range(5)]
        workers = [[None for i in range(5)] for i in range(5)]
        for x in range(5):
            for y in range(5):
                towers[x][y] = self.board[x][y].tower
        for x in range(5):
            for y in range(5):
                worker_number = 0
                local_worker = self.get_tile(Coord(x, y)).worker
                if local_worker is not None:
                    if local_worker.gender == 'm':
                        worker_number = 1
                    else:
                        worker_number = 2
                    if local_worker.owner == 1:
                        worker_number = worker_number * -1
                workers[x][y] = worker_number
        state.append(towers)
        state.append(workers)
        return state

    def set_up_randomly(self):
        current_worker_count = len(self.workers)
        assert self.stage == 0 and current_worker_count < 4

        possible_placements = []
        for x in range(5):
            for y in range(5):
                possible_placements.append(Move(None, Coord(x, y), None))

        picked_placements = random.sample(possible_placements, 4 - current_worker_count)
        for picked in picked_placements:
            print("Plancement move: " + str(picked))
            self.move(picked)

        return picked_placements

    def get_allowed_moves(self):
        # TODO: set this up for stage 0
        assert self.stage == 1 or self.stage == 2

        moves = []
        for tile_column in self.board:
            for current_tile in tile_column:
                if current_tile.worker is not None and current_tile.worker.owner == self.active_player:
                    for move_tile in current_tile.neighbours:
                        if move_tile.tower < 4 and move_tile.worker is None and move_tile.tower <= current_tile.tower + 1:
                            for build_tile in move_tile.neighbours:
                                if build_tile.tower < 4 and (build_tile.worker is None or build_tile == current_tile):
                                    moves.append(Move(current_tile.coord, move_tile.coord, build_tile.coord))

        if len(moves) == 0:
            self.winner = (self.active_player + 1) % 2
            self.stage = 2
        return moves

    def initialize_neighbours(self):
        for tile_column in self.board:
            for current_tile in tile_column:
                # print( "Neighbours for " + str(current_tile.coord) )
                for neighbour_column in self.board:
                    for neighbour_candidate in neighbour_column:
                        dx = abs(current_tile.coord.x - neighbour_candidate.coord.x)
                        dy = abs(current_tile.coord.y - neighbour_candidate.coord.y)
                        if dx <= 1 and dy <= 1 and not (dx == 0 and dy == 0):
                            current_tile.neighbours.append(neighbour_candidate)
                            # print( "--- added " + str( neighbour_candidate.coord ) )
                            assert len(current_tile.neighbours) < 9

    def move(self, move):
        if self.stage == 0:
            assert move.start is None and move.build is None

            worker_type = "m" if len(self.workers) % 2 == 0 else "w"
            placed_worker = Worker(worker_type, self.active_player)
            self.workers.append(placed_worker)

            assert self.get_tile(move.to).worker is None
            self.get_tile(move.to).worker = placed_worker

            if self.active_player == 0 and len(self.workers) >= 2:
                self.switch_active_player()

            if len(self.workers) >= 4:
                self.stage = 1
                print("Entering Stage 1")
                self.switch_active_player()

        elif self.stage == 1:
            self.walk(move.start, move.to)
            self.build(move.build)
            if self.active_player == 1: self.playedturns += 1
            self.switch_active_player()

        else:
            raise NameError("Can't make moves when the game is over")

    def move_coords(self, start, to, build):
        constructed_move = Move(start, to, build)
        self.move(constructed_move)

    def walk(self, start, to):
        start_tile = self.get_tile(start)
        to_tile = self.get_tile(to)
        assert start_tile.worker is not None

        to_tile.worker = start_tile.worker
        start_tile.worker = None

        if start_tile.tower == 2 and to_tile.tower == 3:
            self.winner = self.active_player
            self.stage = 2

    def build(self, coord):
        self.get_tile(coord).build()

    def switch_active_player(self):
        self.active_player = (self.active_player + 1) % 2
