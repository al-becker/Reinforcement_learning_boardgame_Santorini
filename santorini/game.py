import random as random
from typing import List

class Coord:
	def __init__(self,x,y):
		self.x = x
		self.y = y

	def __str__( self ):
		return "(" + chr(ord('a')+self.x) + "|" + str(self.y+1) + ")"

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
		worker.tile = self

	def remove_Worker(self):
		self.worker = None

	def build(self):
		if self.tower<4:
			if self.worker is None:
				self.tower+=1
			else:
				raise ValueError('tried to build on worker tile')
		else:
			raise ValueError('can\'t build on complete tower')

class Move:
	# Set start and build to None to describe an initial worker placement move
	def __init__( self, start, to, build ):
		"""

		:type start: Coord or None
		:type to: Coord
		:type build: Coord or None
		"""
		self.start = start
		self.to = to
		self.build = build

	def __str__( self ):
		if self.start is None:
			return "Move from " + str(self.start) + " to " + str(self.to) + ", building at " + str(self.build) + "."
		else:
			return "Placing worker at " + str(self.to) + "."

class Game:
	board: List[ List[ Tile ] ]

	def __init__(self):
		random.seed() # initialize with system time

		self.board = [[None for i in range(5)]for i in range(5)]
		for x in range(5):
			for y in range(5):
				self.board[x][y] = Tile()
		self.stage = 0
		self.active_player = 0
		self.workers = []
		self.winner = None
		self.playedturns = 0
		self.allmoves = []
		workertypes = ['m', 'w']
		for t in workertypes:
			for i in range(25):
				for j in range(25):
					self.allmoves.append(t+str((i%5))+str((i//5))+str((j%5))+str((j//5)))

	def get_tile( self, coordinates: Coord ) -> Tile:
		return self.board[ coordinates.x ][ coordinates.y ]

	def get_current_state(self):
		state = []
		towers = [[None for i in range(5)]for i in range(5)]
		workers = [[None for i in range(5)]for i in range(5)]
		for x in range(5):
			for y in range(5):
				towers[x][y]=self.board[x][y].tower
		for x in range(5):
			for y in range(5):
				worker_number = 0
				if self.board[x][y].worker is not None:

					if self.board[x][y].worker.type == 'm':
						worker_number = 1
					else:
						worker_number = 2
					if self.board[x][y].worker.player == 1:
						worker_number = worker_number * -1
				workers[x][y]=worker_number
		state.append(towers)
		state.append(workers)
		return state

	def set_up_randomly(self):
		current_worker_count = len(self.workers)
		assert self.stage == 0 and  current_worker_count < 4

		possible_placements = []
		for x in range( 5 ):
			for y in range( 5 ):
				possible_placements.append( Move( None, Coord( x, y), None ) )

		picked_placements = random.sample( possible_placements, 4 - current_worker_count )
		for picked in picked_placements:
			print( str(picked) )
			self.move(picked)


	def get_allowed_moves( self ):
		moves = []
		player_workers = []
		player_workers.append( self.get_worker('m', self.active_player ) )
		player_workers.append( self.get_worker('w', self.active_player ) )
		for worker in player_workers:
			height = worker.tile.tower
			for x in self.neighbouring_fields(worker.coord.x,worker.coord.y):
				target_tile = self.board[x.x][x.y]
				if (target_tile.tower - height) < 2 and target_tile.worker is None and target_tile.tower < 4:
					for i in self.neighbouring_fields(x.x, x.y):
						build_tile = self.board[i.x][i.y]
						if build_tile.tower < 4 and (build_tile.worker is None or build_tile == worker.tile):
							moves.append(worker.type + str(x.x) + str(x.y) + str(i.x) + str(i.y))
		if len(moves) == 0: self.winner = (self.active_player + 1) % 2
		return moves

	def neighbouring_fields(self,x,y):
		fields = []
		if x > 0:
			fields.append(Coord(x-1, y))
			if y > 0:
				fields.append(Coord(x-1, y-1))
		if y > 0:
			fields.append(Coord(x, y-1))
		if x < 4:
			fields.append(Coord(x+1, y))
			if y > 0:
				fields.append(Coord(x+1, y-1))
			if y < 4:
				fields.append(Coord(x+1, y+1))
		if y < 4:
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

	def get_worker( self, coordinates ):
		return self.get_tile( coordinates ).worker

	def move(self, move):
		if self.stage == 0:
			assert move.start is None and move.build is None

			placed_worker = Worker("m", self.get_tile( move.to ), self.active_player, move.to )
			self.workers.append( placed_worker )

			if len(self.workers) >= 4:
				self.stage = 1
				print("Entering Stage 1")
			self.switch_active_player()

		elif self.stage == 1:
			self.walk( move.start, move.to )
			self.get_tile( move.build ).build()
			if self.active_player == 1: self.playedturns += 1
			self.switch_active_player()

	def switch_active_player( self ):
		self.active_player = (self.active_player + 1) % 2

	def walk(self, start, to ):
		worker = self.get_worker( start )
		start_tile = self.get_tile( start )
		to_tile = self.get_tile( to )
		start_tile.remove_Worker()
		to_tile.add_Worker(worker)
		worker.coord = to
		if start_tile.tower == 2 and to_tile.tower == 3:
			self.winner = self.active_player

	def build(self,x,y):
		self.board[x][y].build()

	def move( self, start, to, build ):
		constructed_move = Move( start, to, build )
		self.move( constructed_move )
