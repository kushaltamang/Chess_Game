#Chess AI
#Mohit Tamang

''' Main file, responsible for handling user input and render current GameState object'''
import pygame as pg
import chess_engine

#Global vars
WIDTH = HEIGHT = 512
DIMENSION = 8 # 8*8 board
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15 #for animation
IMAGES = {} #dict for storing images

#load chess piece images. note: do this only once
def loadPieceImages():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("chess_images/" + piece + ".png"), (SQ_SIZE,SQ_SIZE))
        
def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    #create game state object
    gs = chess_engine.GameState()
    validMoves = [] 
    moveMade = False #flag for when a valid move is made
    animate = False # flag var for when animation should be done
    gameOver = False
    running = True
    whiteKingmoved = blackKingmoved = False
    loadPieceImages()    
    sqSelected = () #keep track of last user click(row, col)
    playerClicks = [] #keeps track of player clicks (current click and destination click) eg: [(6,5), (4,4)]
    while(running):
        #to quit game
        for e in pg.event.get():            
            if(e.type == pg.QUIT):
                running = False
                pg.quit()
                
            #get locaton of clicks on the board
            elif(e.type == pg.MOUSEBUTTONDOWN): 
                if not gameOver:
                    location = pg.mouse.get_pos() # gets (x,y) location opf the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    
                    # handes if the user clicks the same square twice
                    if(sqSelected == (row,col)):
                        sqSelected = () #deselect
                        playerClicks = [] #clear player clicks
                        
                    # for a valid move, do this
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected) #append 1st and 2nd clicks
                        
                    if(len(playerClicks) == 1):
                        if(gs.board[row][col] != "--"):
                            validMoves = gs.getValidMoves(row,col)
                            
                    #after the second click, move the piece selected
                    if (len(playerClicks) == 2):
                        move = chess_engine.Move(playerClicks[0], playerClicks[1], gs.board) #user generates a move here
                        print(playerClicks)
                        if move in validMoves:
                            gs.makeMove(move)
                            moveMade = True
                            animate = True
                            sqSelected = () # reset clicks
                            playerClicks = []
                            
                        # handles castling    
                        elif((playerClicks[0] == (7,4) and playerClicks[1] == (7,7)) or (playerClicks[0] == (7,4) and playerClicks[1] == (7,0)) or
                             (playerClicks[0] == (0,4) and playerClicks[1] == (0,7)) or (playerClicks[0] == (0,4) and playerClicks[1] == (0,0))):
                            gs.handleCastling(playerClicks)
                            gs.whiteToMove = not gs.whiteToMove # swap player turn 
                            moveMade = True
                            sqSelected = () # reset clicks
                            playerClicks = []
                            
                       
                        else:
                            playerClicks = [sqSelected]
                            if(gs.board[row][col] != "--"):
                                validMoves = gs.getValidMoves(row,col)
             
            #******** KEY HANDLERS *************#
            #undo the move when 'z' is pressed      
            elif(e.type == pg.KEYDOWN):
                if(e.key == pg.K_z):
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    
            # reset the board when 'r' pressed
                if(e.key == pg.K_r): 
                    gs = chess_engine.GameState()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
        
        #add animation when a move is made
        if moveMade:
            if animate:
                moveAnimation(gs.moveLog[-1], screen, gs.board, clock)
            #validMoves = gs.getValidMoves(row,col)
            moveMade = False
            animate = False
                    
        drawGameState(screen, gs, validMoves, sqSelected) 
        
        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                showText(screen, "CHECKMATE: Black wins")
            else:
                showText(screen, "CHECKMATE: White wins")
        elif gs.stalemate:
            gameOver = True
            showText(screen, "STALEMATE")
            
        clock.tick(MAX_FPS)
        pg.display.flip()

#draw all graphics required on the current game state
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) #draw squares on board
    highlightSq(screen,gs,validMoves, sqSelected)
    drawPieces(screen, gs.board) #draw pieces

#draw squares to make it look like a board 
#this needs to be drawn before drawing pieces
def drawBoard(screen):
    #top left sqaure is always white
    # row num + col num = even (for white squares)
    global colors
    colors = [pg.Color("white"), pg.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            square_color = colors[( (r+c) % 2 )] #picks the color
            pg.draw.rect(screen, square_color, pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''#draw all the pieces on top of the board using the FEN string
def drawPieces(screen, FEN):
    r = c = 0
    for s in FEN: 
        piece = s #grab our piece from GameState > board
        # "/" means skip to the new row
        if(piece == "/"):
            r = r + 1
            c = 0
        else:
            #uppercase denotes white piece
            if(piece.isupper()):
                piece = "w" + piece
            #number denotes how many spaces/columns to skip
            if(piece.isnumeric()):
                c = c + int(piece)
            #grab the piece from images dictionary using key(piece)
            else:
                screen.blit(IMAGES[piece], pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                c = c + 1
'''
#draw pieces using the board
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if(piece != "--"):
                screen.blit(IMAGES[piece], pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
           
# move highlighting
def highlightSq(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r,c = sqSelected
       
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight sdelected sq
            highlight_sq = pg.Surface((SQ_SIZE, SQ_SIZE))
            highlight_sq.set_alpha(100)
            highlight_sq.fill(pg.Color('green'))
            screen.blit(highlight_sq, (c*SQ_SIZE, r*SQ_SIZE))
            
            # highlight moves of the selected piece
            highlight_sq.fill(pg.Color('brown'))
            for move in validMoves:
               if move.startRow == r and move.startCol == c:
                   screen.blit(highlight_sq, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
            
# move animation
def moveAnimation(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSq = 5 # lower the number, faster the move animation
    frameCount = (abs(dR) + abs(dC)) * framesPerSq
    for frame in range(frameCount + 1):
        r,c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        
        #erase piece moved from the ending sq
        color = colors[(move.endRow + move.endCol) % 2]
        endSq = pg.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pg.draw.rect(screen,color, endSq)
        
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pg.display.flip()
        clock.tick(60)
        
# game over text
def showText(screen, text):
    font = pg.font.SysFont("chicago", 40, True, False)
    textObj = font.render(text, 0, pg.Color('white'))
    textLocation = pg.Rect(0,0, WIDTH, HEIGHT).move(WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2)  
    screen.blit(textObj, textLocation)
    textObj = font.render(text, 0, pg.Color('black'))
    screen.blit(textObj, textLocation.move(2,2))
    
if __name__ == "__main__":
    main()


