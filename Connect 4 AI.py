import numpy as np
import random
import pygame
import sys
import math
import os
import time

#sounds links
# https://www.bfxr.net/
# EmpySpace: https://opengameart.org/content/empty-space



#----------------------------------------------------------------------------------------------------------------------------------
#                                               Initialize variables we'r going to need
#----------------------------------------------------------------------------------------------------------------------------------

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255, 255, 255)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

width = 700
height = 600

pygame.mixer.init() #Initialize pygame sound
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
								#Creating Game Message
#------------------------------------------------------------------------------------------------------------------------
def text_objects(text, font) : #Function to obtain Rectangles for Winning or Lost message

    textSurface = font.render(text, True, WHITE)
    return textSurface, textSurface.get_rect()

def message_display(text): # Function for displaying message


    font = pygame.font.SysFont('arial',50)
    TextSurf, TextRect = text_objects(text, font)
    TextRect.center = ((width/2),(height/2))

    screen.blit(TextSurf, TextRect)

    pygame.display.update()#update the whole window if it has no parameters

    time.sleep(2)




def AI_Wins(): #When AI wins
    message_display('AI WINS!!! ')

def Player_Wins(): #When Player wins
	message_display('Congratulations You Win')

#------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#     								 To Load Sound to the game
#----------------------------------------------------------------------------------------------
music_dir = os.path.dirname(__file__) # the file itself where we saving the program
snd_folder = os.path.join(music_dir, 'sound') # Loading te folder where the sounds are located

#--------------------------------------------------------------------------------------------
#							Background Sound
#--------------------------------------------------------------------------------------------
pygame.mixer.music.load(os.path.join(snd_folder, "empySpace.mp3"))
pygame.mixer.music.set_volume(0.4)# To lower the volume of the music

#-------------------------------------------
#           New piece Sound
#-------------------------------------------
New_Piece = pygame.mixer.Sound(os.path.join(snd_folder, 'new_piece.wav')) # sound for a new player piece
Game_over_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'game_over.wav')) # play it when AI wins -> Meaning we lost
#----------------------------------------------------------------------------------------------
#                           To Load Images to the Game
#----------------------------------------------------------------------------------------------

game_folder = os.path.dirname(__file__) # the file itself where we saving the program
img_folder = os.path.join(game_folder, "images") # Loading the folder where the images are located

#-------------------------------------------------------------------------------------------------
#                                 Class for Player Pieces
#-------------------------------------------------------------------------------------------------
class piece_P(pygame.sprite.Sprite):
	"""docstring for Player"""
	def __init__(self, posx, posy):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(os.path.join(img_folder, "P.png")) # Player Image
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect() #To know where to place the image
		self.rect.x = posx #X-azis
		self.rect.y = posy #Y-azis

class piece_AI(pygame.sprite.Sprite):
	"""docstring for Player"""
	def __init__(self, posx, posy):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(os.path.join(img_folder, "AI.png")) # AI image
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()# #To know where to place the image
		self.rect.x = posx #X-azis
		self.rect.y = posy #Y-azis



#------------------------------------------------------------------------------------------------------------------------

def making_2D_array():
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def place_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_array(board):
	print(np.flip(board, 0))#to have the array with 7 column print right

def winning_move(board, piece): #Function that checks for every posibble winning situation
	# Check horizontal locations for win
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(3, ROW_COUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

#-------------------------------------------------------------------------------------------------------------------------------------------------
#   window is an array and WINDOW_LENGTH is of value 4 that let us check how many piece of a kind we have vertically horizontally and diagonal
#-------------------------------------------------------------------------------------------------------------------------------------------------

def evaluate_window(window, piece):
	score = 0
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

#----------------------------------------------------------------------------------------------------------------------------
#               Score has the value of the best move acordingly to have we set up our grading system
#                       This helps the AI to make the next move
#----------------------------------------------------------------------------------------------------------------------------

def score_position(board, piece):
	score = 0

	## Score center column
	center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	## Score Horizontal
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(COLUMN_COUNT-3):
			window = row_array[c:c+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score Vertical
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score posiive sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	return score

def is_terminal_node(board): #Node or situations where the game can END
	return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

#----------------------------------------------------------------------------------------------------------------------------------
#                               Minimax Function using alpha beta pruning
#----------------------------------------------------------------------------------------------------------------------------------

def minimax(board, depth, alpha, beta, maximizingPlayer):
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal:
			if winning_move(board, AI_PIECE):
				return (None, 100000000000000)
			elif winning_move(board, PLAYER_PIECE):
				return (None, -10000000000000)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, score_position(board, AI_PIECE))
	if maximizingPlayer:
		value = -math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			place_piece(b_copy, row, col, AI_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			place_piece(b_copy, row, col, PLAYER_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):

	valid_locations = get_valid_locations(board)
	best_score = -10000
	best_col = random.choice(valid_locations)
	for col in valid_locations:
		row = get_next_open_row(board, col)
		temp_board = board.copy()
		place_piece(temp_board, row, col, piece)
		score = score_position(temp_board, piece)
		if score > best_score:
			best_score = score
			best_col = col

	return best_col

def draw_board_with_pieces(board):
	tablero = pygame.image.load(os.path.join(img_folder, "tablero.jpg")).convert()
	screen.blit(tablero, (0,0))

	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			if board[r][c] == PLAYER_PIECE:
				ficha_P = piece_P(int((c*SQUARESIZE+SQUARESIZE/2) - width_off), height-int(offset + r*SQUARESIZE+SQUARESIZE/2))
				all_sprites.add(ficha_P)
			elif board[r][c] == AI_PIECE:
				ficha_AI = piece_AI(int((c*SQUARESIZE+SQUARESIZE/2) - width_off), height-int(offset + r*SQUARESIZE+SQUARESIZE/2))
				all_sprites.add(ficha_AI)


	pygame.display.update()

board = making_2D_array()
print_array(board)
game_over = False

pygame.init()
pygame.mixer.music.play(loops = -1) # to play it over n over again

SQUARESIZE = 95
offset = 55
width_off = 19 # for other image width_off is 22



size = (width, height)


screen = pygame.display.set_mode(size)
draw_board_with_pieces(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER, AI)

all_sprites = pygame.sprite.Group() # Group where we put all the pieces to be drawn



while not game_over:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		pygame.display.update()




		if event.type == pygame.MOUSEBUTTONDOWN:
			tablero = pygame.image.load(os.path.join(img_folder, "tablero.jpg")).convert()
			screen.blit(tablero, (0,0))
			# Ask for Player 1 Input
			if turn == PLAYER:
				New_Piece.play()
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE))

				if is_valid_location(board, col):
					row = get_next_open_row(board, col)
					place_piece(board, row, col, PLAYER_PIECE)


					if winning_move(board, PLAYER_PIECE):
						Ai_Wons = False
						game_over = True

					turn += 1
					turn = turn % 2



					print_array(board)
					draw_board_with_pieces(board)
					pygame.display.update()
					all_sprites.draw(screen)
					pygame.display.flip()



	# # Ask for Player 2 Input
	if turn == AI and not game_over:
		col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

		if is_valid_location(board, col):
			#pygame.time.wait(2000) #if AI plays too quick we can use this to see its moves
			row = get_next_open_row(board, col)
			place_piece(board, row, col, AI_PIECE)

			if winning_move(board, AI_PIECE):
				Ai_Wons = True
				game_over = True

			print_array(board)
			draw_board_with_pieces(board)
			pygame.display.update()
			all_sprites.draw(screen)
			pygame.display.flip()

			turn += 1
			turn = turn % 2


	if game_over:
		Game_over_sound.play()
		if Ai_Wons:
			AI_Wins()
		else:
			Player_Wins()
		pygame.time.wait(3000)
		pygame.quit()
		quit()
