import game as g
import numpy as np

game = g.Game()
#x = input("pos worker 1")
game.move("m0000")
#x = input("pos worker 2")
game.move("m0100")
#x = input("pos worker 3")
game.move("w1000")
#x = input("pos worker 4")
game.move("w1100")

while True:
    print(np.matrix(game.get_board()[0]))
    print(np.matrix(game.get_board()[1]))
    print(game.allowed_moves())

    if(game.winner is not 0 or not game.allowed_moves()) :
        winner = game.player
        if game.winner is not 0:
            winner = game.winner
        print("We have a winner Player " + str(winner))

    x = input("Player " + str(game.player+1) + " ")
    game.move(x)
