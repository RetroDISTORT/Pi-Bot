import time
import random
import sys              # Required for loading special modules

sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/display')
from menu         import Menu
from canvas       import Canvas


#def loadWorld():


#def saveWorld():

def cellFunction(state, neighbors, survive, spawn):
    if state == 1:
        return 1 if neighbors in survive else 0
    
    if state == 0:
        return 1 if neighbors in spawn else 0
        
    return 0


def newDay(world, survive, spawn):
    height   = len(world)
    width    = len(world[0])
    newWorld = createEmptyWorld(width,height)
    
    for y in range(height):
        for x in range(width):
            newStatus = cellFunction(world[y][x], neighbors(x,y,world), survive, spawn)
            newWorld[y].pop(x)
            newWorld[y].insert(x, newStatus)
    
    clone(newWorld, world)

    
def clone(from_world, to_world):
    height   = len(from_world)
    width    = len(from_world[0])
    
    for y in range(height):
        for x in range(width):
            to_world[y].pop(0)
            to_world[y].insert(width,from_world[y][x])

            
def neighbors(x,y,world):
    height = len(world)
    width  = len(world[0])
    count  = 0
    debug  = 0

    for check_y in range(y-1,y+2):
        for check_x in range(x-1,x+2):
            if not (check_x == x and check_y == y):                
                count += 1 if world[check_y if check_y < height else 0][check_x if check_x < width else 0] == 1 else 0    
    return count


def createEmptyWorld(width, height):
    return [[0] * width for i in range(height)]


def createRandomWorld(width, height, seed=random, population=50):
    random.seed(seed)
    return [[1 if random.randint(0,100) < population else 0  for i in range(width)] for j in range(height)]


def startGame(display, menu, ruleSurvive, ruleSpawn, seed):
    world        = createRandomWorld(50, 50, seed = 5, population = 99)
    liveHistory  = [50*50]*40
    day          = 0
    
    while(True):
        drawWorld( 0, 7, display, world, liveHistory, day)
        newDay(world, ruleSurvive, ruleSpawn)
        day += 1

        
def drawWorld(x, y, display, world, liveHistory, day):
    live   = 0
    width  = len(world[0])
    height = len(world)
    
    for row in range(height):
        for col in range(width):
            if world[row][col] == 1:
                live+=1
                display.addPoint(x+col,y+row)

    liveHistory.append(live)
    liveHistory.pop(0)
    display.addText(60, 20, "Live:" + str(live))
    display.addText(60, 30, "Day:" + str(day))
    display.addGraph(60, 0, 40, 20, liveHistory)
    display.drawCanvas()
    

def gameSettings(display, menu):
    ruleSurvive = [2,3,7,8,9]
    ruleSpawn   = [3,8]
    seed        = "random"

    while True:
        selected = menu.displayMenu(['Start Random', 'Load World', 'Survive Rules', 'Spawn Rules', 'Random Seed', 'Back'])

        if selected == 'Start Random':
            startGame(display, menu, ruleSurvive, ruleSpawn, seed)

        if selected == 'Load World':
            menu.displayMessage("This feature is not available yet")

        if selected == 'Survive Rules':
            menuOptions = [[str(i), i in ruleSurvive] for i in range(0,10)] + ['Back']
            while True:
                select, menuOptions = menu.displayMenu(menuOptions, True)
                if select == 'Back':
                    break
                else:
                    if int(select) in ruleSurvive:
                        ruleSurvive.remove(int(select))
                    else:
                        ruleSurvive.append(int(select))
                    menuOptions[0][1] = int(select) in ruleSurvive
                
                
        if selected == 'Spawn Rules':
            menuOptions = [[str(i), i in ruleSpawn] for i in range(0,10)] + ['Back']
            while True:
                select, menuOptions = menu.displayMenu(menuOptions, True)
                if select == 'Back':
                    break
                else:
                    if int(select) in ruleSpawn:
                        ruleSpawn.remove(int(select))
                    else:
                        ruleSpawn.append(int(select))
                    menuOptions[0][1] = int(select) in ruleSpawn

        if selected == 'Load World':
            menu.displayMessage("This feature is not available yet")
            
        if selected == 'Back':
            return
        
    
def gameMenu(display, menu):
    titleFont = display.loadFont('/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', 32)
    pressed   = []
    
    while True:
        display.addRectangle(0,0,128,32,0,255)
        display.addText(30, -5, "LIFE", fill=0, font=titleFont)
        display.addText(90, 40, "Start")
        display.addText(10, 40, "Exit")
        display.drawCanvas()
        while len(pressed)==0:
            pressed = menu.getInput()
            if 'up' in pressed:
                menu.displayOff()
                return
            if 'down' in pressed:
                gameSettings(display, menu)


def main():
    display  = Canvas() 
    menu     = Menu()
    menu.setGPIO()
    gameMenu(display, menu)

        
if __name__ == "__main__":
    main()
