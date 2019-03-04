import game as g
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
    print(game.get_board())
    print(game.allowed_moves())
    x = input("pos worker 4")
    game.move(x)
