import socket, threading

"""
Message Wait Room Format:
EXIT_STATUS(bool),
playersWaitRoom(fullList),
EVERYONE_READY(bool)

Message Game Format:
EXIT_STATUS(bool),
playersGame(fullList)
PLAYER_EXIT(bool)
"""

#constants for Server
IP = "0.0.0.0"
MAX_PLAYERS = 4
MAX_RECV = 1024
ENCODING = "utf-8"

#messages
#always valid
EXIT    = "0"
NOTHING = "4"
#wait room
NEW_CHARACTER = "1"
NEW_SPAWN     = "2"
READY_CHANGE  = "3"
#in game
INPUT = "5"

#global variables
#queu to give player an id, E = Empty, T = Taken, C = Closed(in game), L = Left(in game)
positionsTaken = ["E", "E", "E", "E"]
#players list to keep track of charcater and username and spawn
#usage username, character, spawn, ready status
USERNAME_INDEX  = 0
CHARACTER_INDEX = 1
SPAWN_INDEX = 2
READY_INDEX = 3
DIFFERENT_INDICES = 4
playersWaitRoom = ["NONE", "NONE", "NONE", "F", "NONE", "NONE", "NONE", "F", "NONE", "NONE", "NONE", "F", "NONE", "NONE", "NONE", "F",]
#players list to keep track of inputs
#moveX, moveY, Fire, mouseX, mouseY, player exit
MOVE_X_INDEX  = 0
MOVE_Y_INDEX  = 1
FIRE_INDEX    = 2
ANGLE         = 3
EXIT_INDEX    = 4
DIFFERENT_INDICES_IN_GAME = 5
playersInGame = ["0", "0", "0", "0", "F", "0", "0", "0", "0", "F", "0", "0", "0", "0", "F", "0", "0", "0", "0", "F",]

def client(conn, id, closeEvent, writeLock):
    global positionsTaken
    global playersWaitRoom

    try:
        #get client their id
        conn.sendall(bytes("F," + str(id) + ",F", encoding=ENCODING))
        username = conn.recv(MAX_RECV).decode(ENCODING)

        print("Client " + username + " Connected!")

        #write to memory with block to properly update
        with writeLock:
            playersWaitRoom[id*DIFFERENT_INDICES+USERNAME_INDEX] = username
            message = ""
            for i in playersWaitRoom:
                message += i
            conn.sendall(bytes(message, encoding=ENCODING))

        #waiting room
        run = True
        clientExit = False
        while run:
            message = conn.recv(MAX_RECV).decode(ENCODING)

            messageParts = message.split(",")
            
            if message == "":
                pass
            elif message[0] == EXIT:
                clientExit = True
                run = False
            elif message[0] == NEW_CHARACTER:
                with writeLock:
                    playersWaitRoom[id*DIFFERENT_INDICES+CHARACTER_INDEX] = messageParts[1]
                    print("Write " + messageParts[1] + " to index " + str(id*DIFFERENT_INDICES+CHARACTER_INDEX) + " for " + username)
            elif message[0] == NEW_SPAWN:
                with writeLock:
                    playersWaitRoom[id*DIFFERENT_INDICES+SPAWN_INDEX] = messageParts[1]
                    print("Write " + messageParts[1] + " to index " + str(id*DIFFERENT_INDICES+SPAWN_INDEX) + " for " + username)
            elif message[0] == READY_CHANGE:
                with writeLock:
                    playersWaitRoom[id*DIFFERENT_INDICES+READY_INDEX] = messageParts[1]
                    print("Write " + messageParts[1] + " to index " + str(id*DIFFERENT_INDICES+READY_INDEX) + " for " + username)

            #send updated player data
            with writeLock:
                everyoneReady = False

                #check if everyone ready
                counter = 0
                playersIn = 0
                i = READY_INDEX
                while i < len(playersWaitRoom):
                    if playersWaitRoom[i] == "T":
                        counter += 1
                    i += DIFFERENT_INDICES
                
                for p in positionsTaken:
                    if p == "T" or p == "C" or p == "L":
                        playersIn += 1
                
                if counter == playersIn:
                    everyoneReady = True

                #check exit status and update all data
                message = ""

                if closeEvent.is_set():
                    message += "T,"
                    run = False
                    clientExit = True
                else:
                    message += "F,"

                for i in playersWaitRoom:
                    message += i
                    message += ","
                
                if everyoneReady:
                    message += "T"
                else:
                    message += "F"
                
                #send updated data
                conn.sendall(bytes(message, encoding=ENCODING))

                if everyoneReady:
                    run = False
        
        if clientExit:
            with writeLock:
                playersWaitRoom[id*DIFFERENT_INDICES+USERNAME_INDEX] = "NONE"
                playersWaitRoom[id*DIFFERENT_INDICES+CHARACTER_INDEX] = "NONE"
                playersWaitRoom[id*DIFFERENT_INDICES+SPAWN_INDEX] = "NONE"
                playersWaitRoom[id*DIFFERENT_INDICES+READY_INDEX] = "F"
                positionsTaken[id] = "E"
            conn.close()
        
            print("Client " + username + " Disconected!")
            return
            
        #play game
        with writeLock:
            positionsTaken[id] = "C"
        
        run = True
        while run:
            message = conn.recv(MAX_RECV).decode(ENCODING)

            if message == "":
                pass
            elif message[0] == EXIT:
                run = False
            elif message[0] == INPUT:
                messageParts = message.split(",")
                with writeLock:
                    playersInGame[id*DIFFERENT_INDICES_IN_GAME+MOVE_X_INDEX] = messageParts[MOVE_X_INDEX+1]
                    playersInGame[id*DIFFERENT_INDICES_IN_GAME+MOVE_Y_INDEX] = messageParts[MOVE_Y_INDEX+1]
                    playersInGame[id*DIFFERENT_INDICES_IN_GAME+ANGLE] = messageParts[ANGLE+1]
                    playersInGame[id*DIFFERENT_INDICES_IN_GAME+FIRE_INDEX] = messageParts[FIRE_INDEX+1]
            
            #send updated data
            with writeLock:
                 #check exit status and update all data
                message = ""

                if closeEvent.is_set() or not run:
                    message += "T,"
                    run = False
                else:
                    message += "F,"
                
                #update players in game
                for p in playersInGame:
                    message += p
                    message += ","
                
                #send data
                conn.sendall(bytes(message, encoding=ENCODING))


        #exit
        with writeLock:
            #clean up player in game
            playersInGame[id*DIFFERENT_INDICES_IN_GAME+MOVE_X_INDEX] = "0"
            playersInGame[id*DIFFERENT_INDICES_IN_GAME+MOVE_Y_INDEX] = "0"
            playersInGame[id*DIFFERENT_INDICES_IN_GAME+FIRE_INDEX]   = "F"
            playersInGame[id*DIFFERENT_INDICES_IN_GAME+ANGLE]      = "0"
            playersInGame[id*DIFFERENT_INDICES_IN_GAME+EXIT_INDEX]   = "T"

            #player wait room clean up
            playersWaitRoom[id*DIFFERENT_INDICES+USERNAME_INDEX]  = "NONE"
            playersWaitRoom[id*DIFFERENT_INDICES+CHARACTER_INDEX] = "NONE"
            playersWaitRoom[id*DIFFERENT_INDICES+SPAWN_INDEX] = "NONE"
            playersWaitRoom[id*DIFFERENT_INDICES+READY_INDEX] = "F"
            positionsTaken[id] = "E"
        
        print("Client " + username + " Disconnected!")
        conn.close()

        
    except socket.error as e:
        print(e)

def createServerAndRun(closeEvent, port):
    global positionsTaken

    #make sure exit status is clean
    playersInGame[0*DIFFERENT_INDICES_IN_GAME+EXIT_INDEX] = "F"
    playersInGame[1*DIFFERENT_INDICES_IN_GAME+EXIT_INDEX] = "F"
    playersInGame[2*DIFFERENT_INDICES_IN_GAME+EXIT_INDEX] = "F"
    playersInGame[3*DIFFERENT_INDICES_IN_GAME+EXIT_INDEX] = "F"

    #keep track of threads to close properly
    threads = []

    #block writing to memory
    writeLock = threading.Lock()

    #create socket, bind it and listen for players
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #allow quick rebind incase program previously crashed and server is still running
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    try:
        sock.bind((IP, port))
    except socket.error as e:
        print(e)
    
    sock.listen(MAX_PLAYERS)
    #set timeout for how long the socket will wait for a player, in the accept function
    sock.settimeout(1.0)
    print("Server Created!")

    #wait for players to join game
    run = True
    while run:
        try:
            id = 0
            positionOpen = False
            
            #get connection
            conn, addr = sock.accept()

            #get position and id
            for p in range(len(positionsTaken)):
                if positionsTaken[p] == "E":
                    with writeLock:
                        positionOpen = True
                        positionsTaken[p] = "T"
                    break
                id += 1
            
            #if has a position start client thread
            if positionOpen:
                threads.insert(id, threading.Thread(target=client, args=(conn, id, closeEvent, writeLock)))
                threads[id].start()
        
        #no player has connect in 1 second so check if close server
        except socket.timeout:
            #on closing Event from client that is running server
            if closeEvent.is_set():
                run = False
                
                #clean up positions
                for p in range(len(positionsTaken)):
                    positionsTaken[p] = "E"
    
    #finish cleaning up server
    sock.close()
    print("Server Closed!")
