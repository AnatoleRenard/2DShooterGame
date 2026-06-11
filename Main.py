#Activate environment: cd .. && source pygame-env/bin/activate && cd Shooter
#Run program: python3 Main.py

import pygame, threading, Player, Sock, Server, Button, TextBox, DropDownBox, CheckBox
from pygame.locals import*

#constants
WIDTH = 700
HEIGHT = 700
FONT_SIZE = 30
MAX_USERNAME_LENGTH = 16
MAX_IP_LENGTH = 15
MAX_PORT_LENGTH = 4

#colors
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
BLACK = (0, 0, 0)

#dropdown options
CHARACTER_DROPDOWN = [Player.NONE, Player.RED, Player.GREEN, Player.YELLOW, Player.BLUE]
SPAWN_DROPDOWN = [Player.NONE, Player.SPAWN_A, Player.SPAWN_B, Player.SPAWN_C, Player.SPAWN_D]

#setup pygame
pygame.init()
gameClock = pygame.time.Clock()
window = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont("Courier New Bold", FONT_SIZE)
clock = pygame.time.Clock()

#pygame helper functions
def drawText(text, window, font, x, y):
    textobj = font.render(text, 1, (0, 0, 0))
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    window.blit(textobj, textrect)

def cleanSocket(socket):
    #clean up client
    socket.close()

#functions for different parts of the game
#gets username and ip adress and determines if program will be host or client
def homeScreen(window, font):
    #set window name
    pygame.display.set_caption("Homescreen")

    isHosting = False
    hostPicked = False
    run = True

    name = TextBox.TextBox(font, BLACK, "Username: ", 10, 10, True, MAX_USERNAME_LENGTH)
    ip = TextBox.TextBox(font, BLACK, "Ip: ", 10, name.rect.y + name.rect.h + 15, False, MAX_IP_LENGTH)
    port = TextBox.TextBox(font, BLACK, "Port: ", 10, ip.rect.y + ip.rect.h + 15, False, MAX_PORT_LENGTH)

    serverButton = Button.Button(10, port.rect.y + port.rect.h + 17, font, WHITE, "Host")
    clientButton = Button.Button(serverButton.rect.x + serverButton.rect.w + 15, serverButton.rect.y, font, WHITE, "Client")
    nextButton   = Button.Button(10, serverButton.rect.y + serverButton.rect.h + 10, font, WHITE, "Next")

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return name.text, ip.text, port.text, isHosting, True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.active:
                        name.setActive(False)
                        ip.setActive(True)
                    elif ip.active:
                        ip.setActive(False)
                        port.setActive(True)
                    elif port.active:
                        port.setActive(False)
                
                elif event.key == pygame.K_ESCAPE:
                    return name.text, ip.text, port.text, isHosting, True
                
                elif event.key == pygame.K_BACKSPACE:
                    name.removeText()
                    ip.removeText()
                    port.removeText()
            
                elif not event.key == pygame.K_SPACE:
                    if event.unicode.isprintable():
                        name.addText(event.unicode)
                        ip.addText(event.unicode)
                        port.addText(event.unicode)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if clientButton.collidePoint(pygame.mouse.get_pos()):
                    clientButton.changeBoxColor(GRAY)
                    hostPicked = True
                    isHosting = False
                
                elif serverButton.collidePoint(pygame.mouse.get_pos()):
                    serverButton.changeBoxColor(GRAY)
                    hostPicked = True
                    isHosting = True
                
                elif nextButton.collidePoint(pygame.mouse.get_pos()):
                    if hostPicked and not name.isEmpty() and not ip.isEmpty() and not port.isEmpty() and not name.text == "NONE":
                        run = False
                
                if name.collidePoint(pygame.mouse.get_pos()):
                    name.setActive(True)
                else:
                    name.setActive(False)
                
                if ip.collidePoint(pygame.mouse.get_pos()):
                    ip.setActive(True)
                else:
                    ip.setActive(False)

                if port.collidePoint(pygame.mouse.get_pos()):
                    port.setActive(True)
                else:
                    port.setActive(False)
        
        if clientButton.collidePoint(pygame.mouse.get_pos()):
            clientButton.changeBoxColor(GRAY)
        elif isHosting or not hostPicked:
            clientButton.changeBoxColor(WHITE)

        if serverButton.collidePoint(pygame.mouse.get_pos()):
            serverButton.changeBoxColor(GRAY)
        elif not isHosting:
            serverButton.changeBoxColor(WHITE)

        if nextButton.collidePoint(pygame.mouse.get_pos()):
            nextButton.changeBoxColor(GRAY)
        else:
            nextButton.changeBoxColor(WHITE)

        window.fill(WHITE)        
        
        name.draw(window)

        ip.draw(window)

        port.draw(window)
        
        serverButton.draw(window)

        clientButton.draw(window)

        nextButton.draw(window)

        pygame.display.update()

    return name.text, ip.text, port.text, isHosting, False

def waitingRoom(window, socket, username):
    #set window name
    pygame.display.set_caption("Waiting Room: " + username)

    #create players list
    players = [Player.Player(), Player.Player(), Player.Player(), Player.Player()]

    #get id and send username to server
    id = int(socket.connect()[2])
    socket.send(username)

    #receive other player data if any
    mesage = socket.receive()

    #math for ui
    yEveryLine = 30 #ten from bottom of last line
    xUser = 250 #ten from longest username possible
    xCharacter = 145 #ten from longest character
    xSpawn = 85 #ten from longest spawn

    #buttons, dropdowns
    helperButtons = []
    usernameButtons = []
    characterDropDowns = []
    spawnDropDowns = []
    readyChecks = []

    baseX = 10
    baseY = 10
    x = baseX
    y = baseY

    #helpers
    helperButtons.append(Button.Button(x, y, font, WHITE, "User"))
    helperButtons[0].setShowOutline(False)
    x += xUser
    helperButtons.append(Button.Button(x, y, font, WHITE, "Character"))
    helperButtons[1].setShowOutline(False)
    x += xCharacter
    helperButtons.append(Button.Button(x, y, font, WHITE, "Spawn"))
    helperButtons[2].setShowOutline(False)
    x += xSpawn
    helperButtons.append(Button.Button(x, y, font, WHITE, "Ready"))
    helperButtons[3].setShowOutline(False)

    #players
    for p in range(Server.MAX_PLAYERS):
        #update x and y axis
        x = baseX
        y += yEveryLine

        #user
        usernameButtons.append(Button.Button(x, y, font, WHITE, players[p].name))
        usernameButtons[p].setShowOutline(False)
        x += xUser

        #character
        characterDropDowns.append(DropDownBox.DropDownBox(CHARACTER_DROPDOWN, x, y, BLACK, WHITE, True, font))
        if not id == p:
            characterDropDowns[p].setInteractive(False)
        x += xCharacter

        #spawn
        spawnDropDowns.append(DropDownBox.DropDownBox(SPAWN_DROPDOWN, x, y, BLACK, WHITE, True, font))
        if not id == p:
            spawnDropDowns[p].setInteractive(False)
        x += xSpawn

        #ready checkbox
        readyChecks.append(CheckBox.CheckBox(x + 20, y + 2, 25, 25, WHITE, False, True))
        if not id == p:
            readyChecks[p].setInteractive(False)

    #loop to wait for other players in game to join and ready up
    notPossibleSpawns = ""
    notPossibleChar = ""
    run = True
    while run:
        messageSent = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                socket.send(Server.EXIT)
                messageSent = True
                return players, id, False, True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    socket.send(Server.EXIT)
                    messageSent = True
                    return players, id, False, False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not characterDropDowns[id].buttons[characterDropDowns[id].selected].text == Player.NONE and not spawnDropDowns[id].buttons[spawnDropDowns[id].selected].text == Player.NONE:
                    change = readyChecks[id].click(pygame.mouse.get_pos())
                    if change and readyChecks[id].getActive():
                        socket.send(Server.READY_CHANGE + ",T")
                        characterDropDowns[id].setInteractive(False)
                        spawnDropDowns[id].setInteractive(False)
                        messageSent = True
                    elif change and not readyChecks[id].getActive():
                        socket.send(Server.READY_CHANGE + ",F")
                        characterDropDowns[id].setInteractive(True)
                        spawnDropDowns[id].setInteractive(True)
                        messageSent = True
                
                change = characterDropDowns[id].click(pygame.mouse.get_pos(), notPossibleChar)
                if change:
                    socket.send(Server.NEW_CHARACTER + "," + characterDropDowns[id].getSelected())
                    messageSent = True
                
                change = spawnDropDowns[id].click(pygame.mouse.get_pos(), notPossibleSpawns)
                if change:
                    socket.send(Server.NEW_SPAWN + "," + spawnDropDowns[id].getSelected())
                    messageSent = True

        #send and get updates from server
        if not messageSent:
            socket.send(Server.NOTHING)
        message = socket.receive()

        notPossibleSpawns = ""
        notPossibleChar = ""
        if message == "":
            pass
        elif message[0] == "T": #exit
            return players, id, False, True
        elif message[len(message) - 1] == "T": #everyone ready
            return players, id, True, False
        else: #update players
            messageParts = message.split(",")

            playerIndex = 0
            startIndex = 1
            #use message parts that is designated to updating player status and ui
            while playerIndex < Server.MAX_PLAYERS:
                #update username
                players[playerIndex].name = messageParts[(playerIndex*Server.DIFFERENT_INDICES)+startIndex+Server.USERNAME_INDEX]
                usernameButtons[playerIndex].changeText(messageParts[(playerIndex*Server.DIFFERENT_INDICES)+startIndex+Server.USERNAME_INDEX])

                #update character
                players[playerIndex].character = messageParts[(playerIndex*Server.DIFFERENT_INDICES)+startIndex+Server.CHARACTER_INDEX]
                characterDropDowns[playerIndex].swapSelected(messageParts[(playerIndex*Server.DIFFERENT_INDICES)+startIndex+Server.CHARACTER_INDEX])
                if not players[playerIndex].character == Player.NONE and not playerIndex == id:
                    notPossibleChar += players[playerIndex].character

                #update spawn
                players[playerIndex].spawn = messageParts[(playerIndex*Server.DIFFERENT_INDICES)+startIndex+Server.SPAWN_INDEX]
                spawnDropDowns[playerIndex].swapSelected(messageParts[(playerIndex*Server.DIFFERENT_INDICES)+startIndex+Server.SPAWN_INDEX])
                if not players[playerIndex].spawn == Player.NONE and not playerIndex == id:
                    notPossibleSpawns += players[playerIndex].spawn

                #update buttons for player
                text = messageParts[(playerIndex*Server.DIFFERENT_INDICES)+startIndex+Server.READY_INDEX]
                if text == "T":
                    readyChecks[playerIndex].setActive(True)
                elif text == "F":
                    readyChecks[playerIndex].setActive(False)

                #next player index
                playerIndex += 1        
        
        #update screen
        window.fill(WHITE)

        #helpers
        for h in helperButtons:
            h.draw(window)

        #username
        for u in usernameButtons:
            u.draw(window)
        
        #character
        for c in range(len(characterDropDowns)):
            if not c == id:
                characterDropDowns[c].draw(window, pygame.mouse.get_pos(), GRAY, notPossibleChar)
        characterDropDowns[id].draw(window, pygame.mouse.get_pos(), GRAY, notPossibleChar) #gets draw over
        
        #spawn
        for s in range(len(spawnDropDowns)):
            if not s == id:
                spawnDropDowns[s].draw(window, pygame.mouse.get_pos(), GRAY, notPossibleSpawns)
        spawnDropDowns[id].draw(window, pygame.mouse.get_pos(), GRAY, notPossibleSpawns)
        
        #ready
        for r in readyChecks:
            r.draw(window, pygame.mouse.get_pos(), GRAY)

        pygame.display.update()

    return players, id, False, False

def game(window, players, id):
    #set window name
    pygame.display.set_caption("In Game: " + players[id].name)

    #get mouse pos and lock it
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    #load all players characters
    for p in players:
        if not p.name == Player.NONE:
            p.loadCharacter()
    
    leftRight = upDown = 0

    run = True
    leaderBoard = False
    while run:
        #get delta time
        dt = clock.tick(30) / 1000

        #get inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
                socket.send(Server.EXIT)
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    socket.send(Server.EXIT)
                    pygame.event.set_grab(False)
                    pygame.mouse.set_visible(True)
                    return False
                elif event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_z:
                    upDown = -1
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a or event.key == pygame.K_q:
                    leftRight = -1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    upDown = 1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    leftRight = 1
                elif event.key == pygame.K_l:
                    leaderBoard = True
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_z:
                    if not upDown == 1:
                        upDown = 0
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a or event.key == pygame.K_q:
                    if not leftRight == 1:
                        leftRight = 0
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if not upDown == -1:
                        upDown = 0
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if not leftRight == -1:
                        leftRight = 0
                elif event.key == pygame.K_l:
                    leaderBoard = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    #left button
                    players[id].fire()

        #send/receive data
        players[id].move(leftRight, upDown, dt, WIDTH, HEIGHT)
        players[id].rotate(pygame.mouse.get_pos())
        message = Server.INPUT + "," + str(players[id].x) + "," + str(players[id].y) + "," + str(players[id].timesShot) + "," +  str(players[id].angle)
        socket.send(message)
        message = socket.receive()
        
        if message == "":
            pass
        elif message[0] == "T":#exit
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
            return False
        elif message[0] == "F":
            messageParts = message.split(",")
            #movement and apply firing
            for p in range(len(players)):
                if not p == id:
                    players[p].x = float(messageParts[(p*Server.DIFFERENT_INDICES_IN_GAME)+Server.MOVE_X_INDEX+1])
                    players[p].y = float(messageParts[(p*Server.DIFFERENT_INDICES_IN_GAME)+Server.MOVE_Y_INDEX+1])
                    players[p].angle = float(messageParts[(p*Server.DIFFERENT_INDICES_IN_GAME)+Server.ANGLE+1])

                    if int(messageParts[(p*Server.DIFFERENT_INDICES_IN_GAME)+Server.FIRE_INDEX+1]) > players[p].timesShot:
                        players[p].fire()
                    
                if messageParts[((p*Server.DIFFERENT_INDICES_IN_GAME)+Server.EXIT_INDEX+1)] == "T":
                    players[p].exit()
                
                players[p].rotateGun(dt)
                
                #move lasers
                players[p].moveLasers(dt)

        #check for hits after everything moved
        for p in range(len(players)):
            for l in range(len(players)):
                if not p == l and players[p].active and players[l].active:
                    hitCounter, ids = players[p].collide(players[l].lasers, players[l].lMask)

                    died = players[p].takeDamage(hitCounter*players[l].damage)
                    if died:
                        players[l].kills += 1

                    idsTakenOff = 0
                    for i in ids:
                        players[l].removeLaserAtIndex(i - idsTakenOff)
                        idsTakenOff += 1

        #draw everything
        window.fill(WHITE)

        for p in players:
            #remove lasers then draw
            if p.active:
                p.removeLasers(WIDTH, HEIGHT)
                p.draw(window)
        
        if leaderBoard:
            index = 0
            for p in players:
                if not p.name == Player.NONE:
                    drawText("User: " + p.name + " Character: " + p.character + " Health: " + str(p.health) + "/" + str(p.maxHealth) + " Points: " + str(p.getPoints()), window, font , 10, 10+(30*index))
                    index += 1
        
        pygame.display.update()
    
    pygame.event.set_grab(False)
    pygame.mouse.set_visible(True)

    return False

#game
while True:
    #show homescreen for game
    username, ipAdress, port, isHosting, exitGame = homeScreen(window, font)
    if exitGame:
        break

    #setup server if needed and close event for closing server properly
    closeEvent = threading.Event()
    serverThread = threading.Thread(target=Server.createServerAndRun, args=(closeEvent, int(port))) #does nothing while not called
    if isHosting:
        serverThread.start()
    
    #setup client and waiting room
    socket = Sock.Sock(ipAdress, int(port))
    players, id, gameLaunched, exitGame = waitingRoom(window, socket, username)

    if exitGame: 
        #clean client and server
        closeEvent.set()
        cleanSocket(socket)
        break

    #play game
    if gameLaunched:
        exitGame = game(window, players, id)
    
    if exitGame:
        #clean client and server
        cleanSocket(socket)
        closeEvent.set()
        break

    #clean up server and client and restart game
    cleanSocket(socket)
    closeEvent.set()
    
pygame.quit()