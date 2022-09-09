import pygame
import requests

hieght = 610; width=550
background_color = (250,255,255)
original_grid_element_color = (0, 0, 200)
solved_grid_element_color =(255,0,70)
insert_grid_element_color =(0,0,0)
sudoku_colour=(242, 255, 255)
win = pygame.display.set_mode((width,hieght))
buffer = 5
backtracks = 0
#x varies from entry1 to entry2 - 1, y varies from entry3 to entry4 - 1
sectors = [ [0, 3, 0, 3], [3, 6, 0, 3], [6, 9, 0, 3],
            [0, 3, 3, 6], [3, 6, 3, 6], [6, 9, 3, 6],
            [0, 3, 6, 9], [3, 6, 6, 9], [6, 9, 6, 9] ]

#This functiom selects difficulty of the sudoku
def gridDifficulty(choice):
    if(choice=="easy"):
        response = requests.get("https://sugoku.herokuapp.com/board?difficulty=easy")
    elif(choice=="medium"):
        response = requests.get("https://sugoku.herokuapp.com/board?difficulty=medium")
    elif(choice=="hard"):
        response = requests.get("https://sugoku.herokuapp.com/board?difficulty=hard")
    return response

#This procedure allows user to input values in the grid
def insert(position,gridCheck):
    i,j = position[1], position[0]
    myfont = pygame.font.SysFont('Comic Sans MS', 35)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if(gridOriginal[i-1][j-1] != 0):
                    return
                if(event.key == 48): #checking with 0
                    gridUser[i-1][j-1] = event.key - 48
                    pygame.draw.rect(win, sudoku_colour, (position[0]*50 + buffer, position[1]*50+ buffer,50 -2*buffer , 50 - 2*buffer))
                    pygame.display.update()
                    return
                if(0 < event.key - 48 <10):  #We are checking for valid input
                    pygame.draw.rect(win, sudoku_colour, (position[0]*50 + buffer, position[1]*50+ buffer,50 -2*buffer , 50 - 2*buffer))
                    value = myfont.render(str(event.key-48), True, insert_grid_element_color)
                    win.blit(value, (position[0]*50 +15, position[1]*50))
                    gridUser[i-1][j-1] = event.key - 48
                    pygame.display.update()
                    return
                return

#draws grid lines and imports pictures
def drawGrid(grid):
        myfont = pygame.font.SysFont('Comic Sans MS', 35)
        win.fill(background_color)
        solve_pic = pygame.image.load('Pictures/solvebutton.jpg').convert_alpha()
        solve_pic = pygame.transform.scale(solve_pic, (100, 100))
        win.blit(solve_pic,(400,500))
        goback_pic = pygame.image.load('Pictures/goback.jpg').convert_alpha()
        goback_pic = pygame.transform.scale(goback_pic, (170, 84))
        win.blit(goback_pic,(30,484))
        redo_pic = pygame.image.load('Pictures/redo.png').convert_alpha()
        redo_pic = pygame.transform.scale(redo_pic, (30, 30))
        win.blit(redo_pic,(470,18))
        pygame.display.flip()
        pygame.draw.rect(win, sudoku_colour, (50, 50, 450, 450))

        for i in range(0,10):
            if(i%3 == 0):
                pygame.draw.line(win, (0,0,0), (50 + 50*i, 50), (50 + 50*i ,500 ), 4 )
                pygame.draw.line(win, (0,0,0), (50, 50 + 50*i), (500, 50 + 50*i), 4 )

            pygame.draw.line(win, (0,0,0), (50 + 50*i, 50), (50 + 50*i ,500 ), 2 )
            pygame.draw.line(win, (0,0,0), (50, 50 + 50*i), (500, 50 + 50*i), 2 )
        pygame.display.update()

        for i in range(0, len(grid[0])):
            for j in range(0, len(grid[0])):
                if(0<grid[i][j]<10):
                    value = myfont.render(str(grid[i][j]), True, original_grid_element_color)
                    win.blit(value, ((j+1)*50 + 15, (i+1)*50 ))
        pygame.display.update()

#This procedure finds the next empty square to fill on the Sudoku grid
def findNextCellToFill(grid):
    #Look for an unfilled grid location
    for x in range(0, 9):
        for y in range(0, 9):
            if grid[x][y] == 0:
                return x,y
    return -1,-1

#This procedure checks if setting the (i, j) square to e is valid
def isValid(grid, i, j, e):
    rowOk = all([e != grid[i][x] for x in range(9)])
    if rowOk:
        columnOk = all([e != grid[x][j] for x in range(9)])
        if columnOk:
            #finding the top left x,y co-ordinates of
            #the section or sub-grid containing the i,j cell
            secTopX, secTopY = 3 *(i//3), 3 *(j//3)
            for x in range(secTopX, secTopX+3):
                for y in range(secTopY, secTopY+3):
                    if grid[x][y] == e:
                        return False
            return True
    return False

#This procedure makes implications based on existing numbers on squares
def makeImplications(grid, i, j, e):

    global sectors
    myfont = pygame.font.SysFont('Comic Sans MS', 35)

    grid[i][j] = e
    display(i,j,e)
    impl = [(i, j, e)]

    for k in range(len(sectors)):
            sectinfo = []

            #find missing elements in ith sector
            vset = {1, 2, 3, 4, 5, 6, 7, 8, 9}
            for x in range(sectors[k][0], sectors[k][1]):
                for y in range(sectors[k][2], sectors[k][3]):
                    if grid[x][y] != 0:
                        vset.remove(grid[x][y])

            #attach copy of vset to each missing square in ith sector
            for x in range(sectors[k][0], sectors[k][1]):
                for y in range(sectors[k][2], sectors[k][3]):
                    if grid[x][y] == 0:
                        sectinfo.append([x, y, vset.copy()])

            for m in range(len(sectinfo)):
                sin = sectinfo[m]
                #find the set of elements on the row corresponding to m and remove them
                rowv = set()
                for y in range(9):
                    rowv.add(grid[sin[0]][y])
                left = sin[2].difference(rowv)

                #find the set of elements on the column corresponding to m and remove them
                colv = set()
                for x in range(9):
                    colv.add(grid[x][sin[1]])
                left = left.difference(colv)

                #check if the vset is a singleton
                if len(left) == 1:
                    val = left.pop()
                    if isValid(grid, sin[0], sin[1], val):
                        grid[sin[0]][sin[1]] = val
                        display(sin[0],sin[1],val)
                        impl.append((sin[0], sin[1], val))

    return impl

#doesn't fill the screen grids
def makeImplications1(grid, i, j, e):

    global sectors

    grid[i][j] = e
    impl = [(i, j, e)]

    done = False

    #Keep going till you stop finding implications
    while not done:
        done = True

        for k in range(len(sectors)):

            sectinfo = []

            #find missing elements in ith sector
            vset = {1, 2, 3, 4, 5, 6, 7, 8, 9}
            for x in range(sectors[k][0], sectors[k][1]):
                for y in range(sectors[k][2], sectors[k][3]):
                    if grid[x][y] != 0:
                        vset.remove(grid[x][y])

            #attach copy of vset to each missing square in ith sector
            for x in range(sectors[k][0], sectors[k][1]):
                for y in range(sectors[k][2], sectors[k][3]):
                    if grid[x][y] == 0:
                        sectinfo.append([x, y, vset.copy()])

            for m in range(len(sectinfo)):
                sin = sectinfo[m]

                #find the set of elements on the row corresponding to m and remove them
                rowv = set()
                for y in range(9):
                    rowv.add(grid[sin[0]][y])
                left = sin[2].difference(rowv)

                #find the set of elements on the column corresponding to m and remove them
                colv = set()
                for x in range(9):
                    colv.add(grid[x][sin[1]])
                left = left.difference(colv)

                #check if the vset is a singleton
                if len(left) == 1:
                    val = left.pop()
                    if isValid(grid, sin[0], sin[1], val):
                        grid[sin[0]][sin[1]] = val
                        impl.append((sin[0], sin[1], val))
                        done = False

    return impl

#This procedure undoes all the implications
def undoImplications(grid, impl):
    for i in range(len(impl)):
        grid[impl[i][0]][impl[i][1]] = 0
    return

#This procedure solves the sudoku
def solveSudoku(grid, i = 0, j = 0):

    global backtracks

    #find the next empty cell to fill
    i, j = findNextCellToFill(grid)
    if i == -1:
        return True

    for e in range(1, 10):
        #Try different values in i, j location
        if isValid(grid, i, j, e):
            if backtracks>800 or a==1:
                impl = makeImplications1(grid, i, j, e)
            else:
                impl = makeImplications(grid, i, j, e)
            if solveSudoku(grid, i, j):
                return True
            #Undo the current cell for backtracking
            backtracks += 1
            undoImplications(grid, impl)

    return False

#This procedure checks if the sudoku user has solved is correct
def check(grid):
    for i in range(0, len(grid[0])):
      for j in range(0, len(grid[0])):
          if(gridUser==grid):
              myfont = pygame.font.SysFont('Comic Sans MS', 35)
              win.fill((0,255,0))
              value = myfont.render("solved", True, (255,0,0))
              win.blit(value, (100, 300 ))
              pygame.display.update()
              pygame.time.delay(7000)
              main()

#This procedure fills the grids on screen to retry
def clearGrid(grid):
    for i in range(0, len(grid)):
      for j in range(0, len(grid[0])):
          if(gridOriginal[i][j]==0):
             pygame.draw.rect(win, sudoku_colour, ((j+1)*50 + buffer, (i+1)*50+ buffer,50 -2*buffer , 50 - 2*buffer))
             pygame.display.update()

#This procedure fills the grids on screen
def display(i,j,e):
    myfont = pygame.font.SysFont('Comic Sans MS', 35)
    value = myfont.render(str(e), True, solved_grid_element_color)
    pygame.draw.rect(win, sudoku_colour, ((j+1)*50 + buffer, (i+1)*50+ buffer,50 -2*buffer , 50 - 2*buffer))
    win.blit(value, ((j+1)*50 + 15, (i+1)*50 ))
    pygame.display.update()

#This procedure prints the sudoku in the terminal
def printSudoku(grid):
    numrow = 0
    for row in grid:
        if numrow % 3 == 0 and numrow != 0:
            print (' ')
        print (row[0:3], ' ', row[3:6], ' ', row[6:9])
        numrow += 1
    return

#executes final left stuff
def finish(grid):
    myfont = pygame.font.SysFont('Comic Sans MS', 35)
    solveSudoku(grid)
    for i in range(0, len(grid[0])):
      for j in range(0, len(grid[0])):
        if(gridOriginal[i][j]==0):
          e=grid[i][j]
          display(i,j,e)
    printSudoku(grid)
    print ('Backtracks = ', backtracks)

def main():
    global gridOriginal
    global gridUser
    global a
    a=1
    pygame.init()
    pygame.display.set_caption("Sudoku")
    myfont = pygame.font.SysFont('Comic Sans MS', 35)
    win.fill((0,0,0))
    pygame.display.update()
    choice=""

    select_pic = pygame.image.load('Pictures/choice.jpg').convert_alpha()
    select_pic = pygame.transform.scale(select_pic, (350, 350))
    win.blit(select_pic,(100,120))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pos = pygame.mouse.get_pos()
                if  (100<pos[0]<445) and (120<pos[1]<230):
                     choice="easy";break
                elif (100<pos[0]<445) and (230<pos[1]<345):
                     choice="medium";break
                elif (100<pos[0]<445) and (345<pos[1]<465):
                     choice="hard";break
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        if choice=="":continue
        break
    response=gridDifficulty(choice)
    grid = response.json()['board']
    gridOriginal = [[grid[x][y] for y in range(len(grid[0]))] for x in range(len(grid))]
    gridUser = [[grid[x][y] for y in range(len(grid[0]))] for x in range(len(grid))]
    gridCheck = [[grid[x][y] for y in range(len(grid[0]))] for x in range(len(grid))]
    drawGrid(grid)
    solveSudoku(gridCheck)
    printSudoku(gridCheck)
    a=0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pos = pygame.mouse.get_pos()
                if (50<pos[0]<500) and (50<pos[1]<500):
                     insert((pos[0]//50, pos[1]//50),gridCheck)
                     check(gridCheck)
                elif (380<pos[0]<497) and  (500<pos[1]<617):
                     finish(grid)
                elif (470<pos[0]<500) and  (20<pos[1]<50):
                     clearGrid(grid)
                elif (50<pos[0]<180) and  (500<pos[1]<540):
                     main()
            if event.type == pygame.QUIT:
                pygame.quit()
                return

main()
