#Chess Engine

'''Stores all info about current state of the game'''
'''Determines valid moves at the current state'''
'''Keep a move log to undo and redo moves'''

class GameState():
    def __init__(self):  
        # chess board representation 
        # 8*8 2-D list
        # "--" represents blank board
        self.startFEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        self.board = [
                ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
                ]
                #maps each piece to the possible moves function for that piece
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B':self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.inCheck = False #if the current player is on check
        self.checkmate = False
        self.stalemate = False
        self.pins = [] #pinned pieces
        self.checks = []
     
    def handleCastling(self,playerClicks):
        #white king side castling
        if playerClicks[0] == (7,4) and playerClicks[1] == (7,7) and not self.inCheck:
            if(self.board[7][5] == "--" and self.board[7][6] == "--" and not self.squareUnderAttack(7,6)):
                kingMove = Move(playerClicks[0],(7,6),self.board)
                rookMove = Move(playerClicks[1],(7,5), self.board)
                self.makeMove(kingMove)
                self.makeMove(rookMove)
        
        # white queen side castling
        if playerClicks[0] == (7,4) and playerClicks[1] == (7,0) and not self.inCheck:
            if(self.board[7][3] == "--" and self.board[7][2] == "--" and self.board[7][1] == "--" and not self.squareUnderAttack(7,2)):
                kingMove = Move(playerClicks[0],(7,2),self.board)
                rookMove = Move(playerClicks[1],(7,3), self.board)
                self.makeMove(kingMove)
                self.makeMove(rookMove) 
                
        #black king side castling
        if playerClicks[0] == (0,4) and playerClicks[1] == (0,7) and not self.inCheck:
            if(self.board[0][5] == "--" and self.board[0][6] == "--" and not self.squareUnderAttack(0,6)):
                kingMove = Move(playerClicks[0],(0,6),self.board)
                rookMove = Move(playerClicks[1],(0,5), self.board)
                self.makeMove(kingMove)
                self.makeMove(rookMove)
                
        # black queen side castling
        if playerClicks[0] == (0,4) and playerClicks[1] == (0,0) and not self.inCheck:
            if(self.board[0][3] == "--" and self.board[0][2] == "--" and self.board[0][1] == "--" and not self.squareUnderAttack(0,2)):
                kingMove = Move(playerClicks[0],(0,2),self.board)
                rookMove = Move(playerClicks[1],(0,3), self.board)
                self.makeMove(kingMove)
                self.makeMove(rookMove) 
        
    #takes a move as parameter, and executes the move by changing the board state
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--" # blank at piece moved
        self.board[move.endRow][move.endCol] = move.pieceMoved # move piece at this location
        self.moveLog.append(move) #log the move
        self.whiteToMove = not self.whiteToMove # swap player turn 
        
        #update location of king piece
        if(move.pieceMoved == "wK"):
            self.whiteKingLocation = (move.endRow, move.endCol)
        if(move.pieceMoved == "bK"):
            self.blackKingLocation = (move.endRow, move.endCol)
            
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        
    #undo a move
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop() 
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #swith turns
            
        #update location of king piece
        if(move.pieceMoved == "wK"):
            self.whiteKingLocation = (move.startRow, move.startCol)
        elif(move.pieceMoved == "bK"):
            self.blackKingLocation = (move.startRow, move.startCol)
   
    # checks for check-mates
    def getValidMoves(self, r, c):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkPinsandChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
            
        if self.inCheck: # if king is in check
            if (len(self.checks) == 1): # if only 1 check, block check or move king
                moves = self.getallPossiblemoves(r,c)
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                checkingPiece = self.board[checkRow][checkCol] # enemy piece causing check
                validSquares = [] # squares that pieces can move to block check
                if(checkingPiece == 'N'):
                    validSquares = [(checkRow,checkCol)]
                else:
                    
                    for i in range(1,8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) # check[2], check[3] gives the direction of the check,
                        validSquares.append(validSquare) #  keep checking in the directions, add valid squares
                        if(validSquare[0] == checkRow and validSquare[1] == checkCol):
                            break
                        
                #moves that does not block check or move king are invalid
                for i in range(len(moves) -1, -1, -1): # go through the list backwards
                    if moves[i].pieceMoved[1] != 'K': # if piecemoves is not king, then move that piece to a valid square
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else: # double check, king must move   
                self.getKingMoves(kingRow, kingCol, moves)
        else:# every move is valid if king is not in check
            moves = self.getallPossiblemoves(r,c)
        
        # checks for checkmate or stalemate
        if len(moves) == 0:
            if(self.inCheck): 
                self.checkmate = True
                print("checkmate")
            else:
                 self.stalemate = True
                 
        return moves
    
    
    # all possible moves w/o considering checks
    def getallPossiblemoves(self, r, c):
        moves = []
        piece = self.board[r][c][1]  
       # print(self.moveFunctions[piece])
        self.moveFunctions[piece](r, c, moves) # calls all the move functions for the selected piece                   
        return moves
    
    def getalltheMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves
                
    # determine if the enemy can attack square r,c
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove # switch turn to opposition POV
        oppMoves = self.getalltheMoves() # generate opponent's move
        self.whiteToMove = not self.whiteToMove # switch back to ourselves
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False
    
    #generates list of all the pieces causing checks and pinned pieces, and checks if the king is in check or not
    def checkPinsandChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + direction[0] * i
                endCol = startCol + direction[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    end_piece = self.board[endRow][endCol]
                    if end_piece[0] == allyColor and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (endRow, endCol, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemyColor:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "p" and (
                                (enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
                
        #check for knight checks
        knightMoves = ((-2,-1),(-2,1),(-1,-2), (-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <= 7 and 0 <=endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow,endCol,m[0],m[1]))
        return inCheck, pins, checks
                    
                                
                            
     
    #get all valid  moves for a pawn
    def getPawnMoves(self, r, c, moves):
        # note: black pawns are on row 1, white pawns on row 6  
        
        # handle pinned pieces so that they cannot move when pinned
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        # logic for white pawn moves
        if(self.whiteToMove): 
            if(self.board[r-1][c] == "--"): #row above the pawn is empty
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r,c), (r-1,c), self.board)) # 1 sq move
                    if((r == 6) and (self.board[r-2][c] == "--")): # checks if white pawn has not moved previously for 2 sq moves
                        moves.append(Move((r,c),(r-2,c), self.board)) # 2 sq pawn move

            #pawn capture logic to its left
            if(c-1 >= 0):
                if(self.board[r-1][c-1][0] == 'b'): #black piece to be captured 
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append(Move((r,c), (r-1,c-1), self.board))
            
            #pawn capture logic to its right
            if(c+1 <= 7):
                if(self.board[r-1][c+1][0] == 'b'):
                    if not piecePinned or pinDirection == (-1,1):
                        moves.append(Move((r,c), (r-1,c+1), self.board))
                    
        #logic for black pawn moves          
        else:
            if(self.board[r+1][c] == "--"): # 1 sq move
                if not piecePinned or pinDirection == (1,0):
                    moves.append(Move((r,c),(r+1,c), self.board))
                    if((r == 1) and self.board[r+2][c] == "--"): # 2 sq move
                        moves.append(Move((r,c),(r+2,c), self.board))
                    
            #pawn capture logic to its left
            if(c+1 <= 7):
                if(self.board[r+1][c+1][0] == 'w'): #white piece to be captured
                    if not piecePinned or pinDirection == (1,1):
                        moves.append(Move((r,c), (r+1, c+1), self.board))
            
            #pawn capture logic to its right
            if(c -1 >=0):
                if(self.board[r+1][c-1][0] == 'w'):
                    if not piecePinned or pinDirection == (1,-1):
                        moves.append(Move((r,c), (r+1, c-1), self.board))
                    
                    
    def getKnightMoves(self, r, c, moves): 
        # handle pinned pieces so that they cannot move when pinned
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
            
        #check if the places Knight can move are empty and not out of bounds
        validMoves = ((-2,-1), (-2,1), (-1,2), (1,-2), (2,1), (2,-1), (1,2),(-1,-2))
        oppositeColor = 'b' if self.whiteToMove else 'w'
        for v in validMoves:
            row = r + v[0]
            col = c + v[1]
            if ((0 <= row < 8) and (0 <= col < 8)):
                if not piecePinned:
                    endPiece = self.board[row][col]
                    if((endPiece[0] == oppositeColor) or (endPiece == "--")):
                        moves.append(Move((r,c), (row,col), self.board))
                
     
    def getBishopMoves(self, r, c, moves): 
        #handle pinned pieces so that they cannot move when pinned
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        direction = ((-1,-1), (-1,1), (1,-1), (1,1))
        oppositeColor = 'b' if self.whiteToMove else 'w'
        for d in direction:
            for i in range(1,8):
                row = r + d[0] * i
                col = c + d[1] * i
                if ((0 <= row < 8) and (0 <= col < 8)): # checking bounds
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[row][col]
                        if(endPiece == "--"): # empty cell
                            moves.append(Move((r,c), (row, col), self.board))
                        elif(endPiece[0] == oppositeColor): #grab enemy piece
                            moves.append(Move((r,c), (row,col), self.board))
                            break
                        else:
                            break
                else:
                    break
                
    
    def getQueenMoves(self, r, c, moves):  
        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)
    
    def getKingMoves(self, r, c, moves):  
        rowMoves = (-1, -1 , -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol) # change king's location temporarily
                    else:
                        self.blackKingLocation = (endRow, endCol)
                        
                    #check for checks/pins
                    inCheck, pins, checks = self.checkPinsandChecks()
                    
                    #if not in check after we have checked for pins and checks
                    if not inCheck:
                        moves.append(Move((r,c),(endRow,endCol), self.board)) # valid move
                        
                    # reset king  to the original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)
                
    
    def getRookMoves(self, r, c, moves):
        # handle pinned pieces so that they cannot move when pinned
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': # cant remove queen as pinned queen can also capture rook
                    self.pins.remove(self.pins[i])
                break
        direction = ((-1,0), (0,-1), (1,0), (0,1)) # up left down right 
        oppositeColor = 'b' if self.whiteToMove else 'w'
        for d in direction:
           for i in range(1,8):
               row = r + d[0] * i
               col = c + d[1] * i
               if((0 <= row < 8) and (0 <= col < 8)):
                   if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                       endPiece = self.board[row][col]
                       if(endPiece == "--"):
                           moves.append(Move((r,c),(row,col), self.board))
                       elif(endPiece[0] == oppositeColor):
                           moves.append((Move((r,c), (row,col), self.board)))
                           break
                       else:
                           break
               else:
                    break
        
class Move():
    # co-ordinates(row, col) mapping to chess(row, col) notations
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0 }
    rowsToRanks = {v: k for k, v in ranksToRows.items()} #reverse above dictionary
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7 }
    colsToFiles = {v: k for k, v in filesToCols.items()}
    
    #constructor
    def __init__(self, startSq, endSq, board):
       #gs = GameState()
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endRow]
        #self.pieceMoved = gs.startFEN[self.startCol + gs.startFEN.find("/", self.startRow -1)]
        #self.pieceCaptured = gs.startFEN[self.endRow + gs.startFEN.find("/", self.endRow -1)]
        
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7) # pawn promotion logic                      
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol #unique ID given to each move
        
    #comparing obj to another obj
    def __eq__(self, other):
        if(isinstance(other, Move)):
            #if starting row, col and ending row, col are same for both moves, they are equal
            return(self.moveID == other.moveID)
        return False
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
   
        
        
            