import reversi
import sys

if __name__ == '__main__':
    server_address = sys.argv[1]
    bot_move_number = int(sys.argv[2])

    if bot_move_number != 1 and bot_move_number != 2:
        raise Exception("Bot numbers needs to be 1 or 2")
    
    mode = 0
    
    if sys.argv[3]:
        mode = int(sys.argv[3])
    
    if not mode in list(range(5)):
        raise Exception("Mode needs to be between 0 and 4")

    reversi_game = reversi.ReversiGame(server_address, bot_move_number, mode)
    reversi_game.play()
