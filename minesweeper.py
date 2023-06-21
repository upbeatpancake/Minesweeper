from tkinter import *
from tkinter import messagebox
import random

class mineCell(Label):
    '''represents a Minesweeper cell'''

    def __init__(self, master, coord):
        '''mineCell(master, coord) -> mineCell
        creates a new blank mineCell with (row,column) coord'''
        Label.__init__(self, master, height=1, width=2, text='',\
                       bg = 'white', font=('Arial', 18), relief='raised')
        # attributes
        self.master = master # the grid
        self.coord = coord # (x,y) coordinate tuple
        self.number = 0 # 0 represents an empty cell
                        # num will be changed once bombs are placed
        self.bomb = False # starts as not a bomb
        self.exposed = False # player doesn't know what's in the cell
        self.flagged = False
        self.neighbors = [] # list of adjacent cells
        master.find_neighbors(self)
        self.clickable = True
        
        # set up listeners
        self.bind('<Button-1>', self.expose)
        self.bind('<Button-3>', self.flag)

    def get_coord(self):
        '''mineCell.get_coord() -> tuple
        returns the (row, column) coordinate of the cell'''
        return self.coord

    def get_num(self):
        '''mineCell.get_num() -> int
        returns the number in the cell (0 if empty, 9 if bomb)'''
        return self.number

    def is_bomb(self):
        '''mineCell.is_bomb() -> boolean
        returns True if the cell holds a bomb
        False if not'''
        return self.bomb

    def is_flagged(self):
        '''mineCell.is_flagged() -> boolean
        returns True if the cell is flagged
        False if not'''
        return self.flagged

    def is_exposed(self):
        '''mineCell.is_exposed() -> boolean
        returns True if the player clicked on the cell to see its contents
        False if not'''
        return self.exposed

    def expose(self, event):
        '''mineCell.expose() -> None
        shows the player what is in the cell'''
        # if the game is over
        if self.clickable == False:
            return

        # if the cell is flagged
        if self.flagged == True:
            return # they can't click it

        # if the player clicked a bomb!
        if self.bomb == True:
            self.master.show_loss()
            return 

        # cell can only be exposed if it hasn't been already
        if self.exposed == False:
            self.exposed = True
            self['bg'] = "gray"
            self['relief'] = 'sunken'
            if self.number != 0: # if the cell is a num
                self['text'] = self.number
                self['fg'] = self.color
            else: # if the cell is blank
                self.master.auto_expose(self)

        # check for a win
        if self.master.check_win():
            self.master.show_win()

    def computer_expose(self):
        '''mineCell.computer_expose() -> int
        shows the player what is in the cell
        returns the number that is revealed (0 if empty, 9 if bomb)'''
        self.exposed = True
        self['bg'] = "gray"
        self['relief'] = 'sunken'
        # if the cell isn't blank or a bomb
        if self.number != 0 and self.number != 9:
            self['text'] = self.number
            self['fg'] = self.color
                
            
    def flag(self, event):
        '''mineCell.flag() -> None
        does NOT check if the cell is covered/can be flagged
        updates the cell text to an asterisk'''
        # if the game is over
        if self.clickable == False:
            return

        # player can only flag if cell is hidden
        if self.exposed == False:
            # if the cell is unflagged
            if self.flagged == False:
                self['text'] = "*" # flag it
                self.flagged = True
                self.master.flagsLeft -= 1 # update the label
                self.master.flagsLeftLabel['text'] = str(self.master.flagsLeft)
                
            # if the cell is already flagged
            else:
                self['text'] = ""
                self.flagged = False
                self.master.flagsLeft += 1 # update the label
                self.master.flagsLeftLabel['text'] = str(self.master.flagsLeft)

        
    def set_num(self):
        '''mineCell.set_num() -> None
        determines and sets the PERMANENT number in a cell
        based on the bombs placed at the beginning'''
        if self.is_bomb():
            self.number = 9
            return
        
        bombCount = 0 # counter
        for coord in self.neighbors:
            cell = self.master.cells[coord] # for each cell
            if cell.bomb == True: # if it's a bomb
                bombCount += 1 # increment counter
        self.number = bombCount # set the cell's number

    def set_color(self):
        '''mineCell.set_color() -> None
        sets the cell's color according to its num'''
        if self.is_bomb():
            return
        
        self.color = ['','blue','darkgreen','red','purple',\
                      'maroon','cyan','black','dim gray'][self.number]
        
class mineGrid(Frame):
    '''object for a Minesweeper grid'''

    def __init__(self, master, width, height, numBombs):
        '''mineGrid(master, rows, columns)
        creates a new blank Minesweeper grid'''

        # attributes
        self.rows = height
        self.columns = width
        self.numBombs = numBombs
        self.flagsLeft = numBombs

        # initialize a new Frame
        Frame.__init__(self, master, bg='black')
        self.grid()
        
        # create the cells
        self.cells = {} # set up dictionary for cells
         
        for r in range(height):
            for c in range(width):
                coord = (c, r) 
                # create the cell and add it to the attribute list
                self.cells[coord] = mineCell(self, coord) 
                self.cells[coord].grid(row=r, column=c)
        
        # this label shows how many flags are left
        self.flagsLeftLabel = Label(master=self, height=1, width=3, text=str(numBombs), bg='white', font=('Arial', 16 ))
        self.flagsLeftLabel.grid(row=height, column=0, columnspan=width)
        
        self.set_bombs(numBombs) # place the bombs!

        # set the nums and colors
        for coord in self.cells:
            cell = self.cells[coord]
            self.find_neighbors(cell)
            cell.set_num()
            self.cells[coord].set_color()
        

    def find_neighbors(self, cell):
        '''mineCell.find_neighbors() -> List
        updates the neighbors attribute 
        each item in the list is a coordinate tuple
        that represents an adjacent cell
        returns cell.neighbors list'''
        centerCoord = cell.get_coord() # coords of the central cell

        rowSame = centerCoord[1]
        columnSame = centerCoord[0]
        rowUp = rowSame + 1
        rowDown = rowSame - 1
        columnRight = columnSame + 1
        columnLeft = columnSame - 1
        
        cell.neighbors = [(columnRight, rowSame), (columnLeft, rowSame), \
                          (columnSame, rowUp), (columnSame, rowDown), \
                          (columnRight, rowUp), (columnLeft, rowDown), \
                          (columnLeft, rowUp), (columnRight, rowDown)]

        tempList = cell.neighbors[:] 
        for copyPair in tempList:
            if copyPair[0] < 0 or copyPair[1] < 0 or copyPair[0] >= self.columns or copyPair[1] >= self.rows:
                cell.neighbors.remove(copyPair) # remove out-of-grid cells

        return cell.neighbors

    def find_cell_neighbors(self, coordList):
        '''mineGrid.find_cell_neighbors() -> List
        coordList is a list of COORDS of adjacent cells
        returns list of CELLS that are adjacent to the given cell'''
        returnList = []
        for cellCoords in coordList:
            cell = self.cells[cellCoords]
            returnList.append(cell)
        return returnList

    def set_bombs(self, bombs):
        '''mineGrid.set_bombs(bombs) -> None
        adds numBombs random hidden bombs to the board'''
        self.bombList = []
        usedList = [] # stores used coords of bombs
        coordOne = [i for i in range(self.rows)]
        coordTwo = [j for j in range(self.columns)] 
        bombColumn = None
        bombRow = None
        for k in range(bombs):
            # keep choosing a new row and column if it's a repeat
            # or choose a new r and c for the first bomb
            while (bombColumn, bombRow) in usedList or len(usedList) == 0:
                bombRow = coordOne[random.randint(0,len(coordOne)-1)]
                bombColumn = coordTwo[random.randint(0,len(coordTwo)-1)]
                if len(usedList) == 0: # if it's the first bomb
                    break # keep it
            usedList.append((bombColumn, bombRow))
            
            bombCell = self.cells[(bombColumn, bombRow)] # find the bomb cell
            bombCell.bomb = True
            bombCell.number = 9
            self.bombList.append(bombCell) # add it to the bombList
            

    def reveal_bombs(self):
        '''mineGrid.reveal_bombs() -> None
        exposes all remaining bombs in red'''
        for bomb in self.bombList:
            bomb['bg'] = "red"
            bomb['text'] = "*"

    def check_win(self):
        '''mineGrid.check_win() -> boolean
        checks if the player exposed all non-bombs'''
        # player needs to expose goalExposes cells
        goalExposes = self.rows*self.columns - self.numBombs
        exposes = 0 # counter

        for coord in self.cells:
            cell = self.cells[coord]
            if cell.bomb == False and cell.exposed == True:
                exposes += 1
        return exposes == goalExposes

    def show_win(self):
        '''mineGrid.show_win() -> None
        reveals a "you won" message to the player :)'''
        messagebox.showinfo('Minesweeper','Congratulations -- you won!',parent=self)
        self.freeze_cells()
        

    def show_loss(self):
        '''mineGrid.show_loss() -> None
        reveals a "you lose" message to the player
        reveals bombs'''
        messagebox.showerror('Minesweeper','KABOOM! You lose.',parent=self)
        self.reveal_bombs()
        self.freeze_cells()
        
        
    def auto_expose(self, cell):
        '''mineGrid.auto_expose(cell) -> None
        automatically exposes the cells adjacent to an empty cell
        if an exposed cell is also empty, the process is repeated
        until no empty cells are surrounded by unexposed cells'''

        blankCells = [] # stores newly exposed blank adjacent cells
        coordList = self.find_neighbors(cell) # list of adjacent cells' coords
        adjacentCells = [] # list of unexposed adjacent cells

        # add to adjacentCells
        for tempCell in self.find_cell_neighbors(coordList):
            if tempCell.exposed == False:
                adjacentCells.append(tempCell)

        # so the method ends
        if len(adjacentCells) == 0:
                return
            
        for cell in adjacentCells: # for each unexposed adjacent cell
            cell.computer_expose() # expose it
            if cell.number == 0: # if it's blank
                blankCells.append(cell) # add to the list

        # recursive part
        for emptyCell in blankCells:
            mineGrid.auto_expose(self, emptyCell)

                
    def freeze_cells(self):
        '''mineGrid.freeze_cells() -> None
        makes it so none of the cells can be clicked
        used after the game ends'''
        for coord in self.cells:
            self.cells[coord].clickable = False
            
# main loop for the game
def play_minesweeper(rows, columns, bombs):
    '''minesweeper()
    plays minesweeper'''
    root = Tk()
    root.title('Minesweeper')
    mg = mineGrid(root, rows, columns, bombs)
    root.mainloop()        
        
play_minesweeper(12, 10, 15) 
