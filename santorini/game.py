import random as random

class Coord:
    def __init__(self,x,y):
        self.x = x
        self.y = y

class Turn:
    def __init__(self,turn_string):
        while len(turn_string)<5:
            turn_string+='0'
        self.worker = turn_string[0]
        self.coordW = Coord(int(turn_string[1]),int(turn_string[2]))
        self.coordB = Coord(int(turn_string[3]),int(turn_string[4]))

class Worker:
    def __init__(self,type,tile,player,coord):
        self.type = type
        self.tile = tile
        self.tile.add_Worker(self)
        self.player = player
        self.coord = coord

class Tile:
    def __init__(self):
        self.tower = 0
        self.worker = None

    def add_Worker(self,worker):
        self.worker = worker

    def remove_Worker(self):
        self.worker = None

    def build(self):
        if self.tower<4:
            if self.worker is None:
                self.tower+=1
            else:
                raise ValueError('tried to build on worker tile')
        else:
            raise ValueError('wrong position for worker')

class Game():
    def __init__(self):
        self.board = [[None for i in range(5)]for i in range(5)]
        for x in range(5):
            for i in range(5):
                self.board[x][i] = Tile()
        self.stage = 0
        self.player = 0
        self.workers = []
        self.winner = 0
        self.allmoves = []
        workertypes = ['m', 'w']
        for t in workertypes:
            for i in range(25):
                for j in range(25):
                    self.allmoves.append(t+str((i%5))+str((i//5))+str((j%5))+str((j//5)))

    def get_board(self):
        state = []
        towers = []
        players = []
        for x in range(5):
            for i in range(5):
                towers.append(self.board[x][i].tower)
        for x in range(5):
            for i in range(5):
                playerNumber = 0
                if self.board[x][i].worker is not None:

                    if self.board[x][i].worker.type == 'm':
                        playerNumber = 1
                    else:
                        playerNumber = 2
                    if self.board[x][i].worker.player == 1:
                        playerNumber = playerNumber * -1
                players.append(playerNumber)
        state.append(towers)
        state.append(players)
        return state

    def allowed_moves(self):
        moves = []
        player_workers = []
        player_workers.append(self.get_worker('m',self.player))
        player_workers.append(self.get_worker('w',self.player))
        for worker in player_workers:
            height = worker.tile.tower
            for x in self.neighbouring_fields(worker.coord.x,worker.coord.y):
                target_tile = self.board[x.x][x.y]
                if (target_tile.tower - height) < 2 and target_tile.worker is None and target_tile.tower < 4:
                    for i in self.neighbouring_fields(x.x, x.y):
                        build_tile = self.board[i.x][i.y]
                        if build_tile.tower < 4 and build_tile.worker is None or build_tile == worker.tile:
                            moves.append(worker.type + str(x.x) + str(x.y) + str(i.x) + str(i.y))
        return moves

    def neighbouring_fields(self,x,y):
        fields = []
        if x > 0:
            fields.append(Coord(x-1, y))
            if y > 0:
                fields.append(Coord(x-1, y-1))
        if y > 0:
            fields.append(Coord(x, y-1))
        if x < 5:
            fields.append(Coord(x+1, y))
            if y > 0:
                fields.append(Coord(x+1, y-1))
            if y < 5:
                fields.append(Coord(x+1, y+1))
        if y < 5:
            fields.append(Coord(x, y+1))
            if x > 0:
                fields.append(Coord(x-1, y+1))
        return fields

    def get_worker(self,type,player):
        worker = None
        for x in self.workers:
            if x.type == type and x.player == player:
                 worker = x
        if worker is None:
            raise ValueError('Worker not found')
        return worker

    def move(self,input):
        turn = Turn(input)
        if self.stage == 0:
            worker = Worker(turn.worker,self.board[turn.coordW.x][turn.coordW.y],self.player, Coord(turn.coordW.x,turn.coordW.y))
            self.workers.append(worker)
            if self.workers.__len__()>=4:
                self.stage = 1
                print("Entering Stage 1")
            self.player = (self.player+1)%2

        elif self.stage == 1:

            self.walk(turn.worker,turn.coordW.x,turn.coordW.y)
            self.board[turn.coordB.x][turn.coordB.y].build()
            self.player = (self.player + 1) % 2

    def walk(self,worker_type,xPos,yPos):
        worker = self.get_worker(worker_type,self.player)
        worker.tile.remove_Worker()
        self.board[xPos][yPos].add_Worker(worker)
        worker.coord.x = xPos
        worker.coord.y = yPos
        if self.board[xPos][yPos].tower == 3:
            self.winner = self.player

    def build(self,x,y):
        self.board[x][y].build()
