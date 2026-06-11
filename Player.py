import pygame, math

#death sound
pygame.mixer.init()
deathSound = pygame.mixer.Sound("Characters/dead.mp3")

#constants
#characters
NONE   = "NONE"
RED    = "RED"
GREEN  = "GREEN"
YELLOW = "YELLOW"
BLUE   = "BLUE"

#spawns, change to tuples later for spawn position
SPAWN_A = "A"
SPAWN_B = "B"
SPAWN_C = "C"
SPAWN_D = "D"
SPAWN_A_COORD = (60, 60)
SPAWN_B_COORD = (640, 60)
SPAWN_C_COORD = (60, 640)
SPAWN_D_COORD = (640, 640)

#character width and height for image
#pos = center of circle
CHARACTER_SIZE      = 60
HALF_CHARACTER_SIZE = CHARACTER_SIZE / 2
LASER_SIZE          = 30
HALF_LASER_SIZE     = LASER_SIZE / 2

#ROTAION of lasers and guns
LASER_ROTATION_SPEED = 90

class Laser:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
    
    def move(self, speed):
        pass

class Player:
    def __init__(self):
        self.name = NONE
        self.character = NONE
        self.spawn = NONE
        self.active = False
        
        self.x = 0
        self.y = 0
        self.angle = 0.0
        self.gunAngle = 0.0
        self.maxHealth = 0
        self.health = 0
        self.speed = 0
        self.lSpeed = 0
        self.damage = 0
        self.timesShot = 0

        self.death = 0
        self.kills = 0

        self.lasers = []

        self.img = ""
        self.lImg = ""
        self.shot = ""
    
    def changeUserName(self, name):
        self.name = name

    def changeCharacter(self, character):
        self.character = character
    
    def changeSpawn(self, spawn):
        self.spawn = spawn
    
    def loadCharacter(self):
        with open("Characters/" + self.character + ".txt", "r") as f:
            for l in f:
                data = l.split(":")

                if data == "":
                    pass
                elif data[0] == "SPEED":
                    self.speed = int(data[1])
                elif data[0] == "HEALTH":
                    self.maxHealth = int(data[1])
                    self.health = int(data[1])
                elif data[0] == "DAMAGE":
                    self.damage = int(data[1])
                elif data[0] == "LSPEED":
                    self.lSpeed = int(data[1])
        
        self.img = pygame.transform.scale(pygame.image.load("Characters/" + self.character + ".png"), (CHARACTER_SIZE, CHARACTER_SIZE))
        self.lImg = pygame.transform.scale(pygame.image.load("Characters/" + self.character + ".png"), (LASER_SIZE, LASER_SIZE))

        self.shot = pygame.mixer.Sound("Characters/" + self.character + ".mp3")

        self.mask = pygame.mask.from_surface(self.img)
        self.lMask = pygame.mask.from_surface(self.lImg)

        self.setSpawn()
        self.active = True

    def setSpawn(self):
        if self.spawn == SPAWN_A:
            self.x, self.y = SPAWN_A_COORD
        elif self.spawn == SPAWN_B:
            self.x, self.y = SPAWN_B_COORD
        elif self.spawn == SPAWN_C:
            self.x, self.y = SPAWN_C_COORD
        else:
            self.x, self.y = SPAWN_D_COORD
    
    def gunPos(self):
        x = CHARACTER_SIZE*math.cos(math.radians(self.angle)) + self.x
        y = CHARACTER_SIZE*math.sin(math.radians(self.angle)) + self.y
        return x, y

    def draw(self, window):
        #draw lasers
        for l in self.lasers:
            rotatedImg = pygame.transform.rotate(self.lImg, self.gunAngle)
            newRect = rotatedImg.get_rect(center=self.lImg.get_rect(topleft =(l.x - HALF_LASER_SIZE, l.y - HALF_LASER_SIZE)).center)
            window.blit(rotatedImg, newRect)
        
        #draw gun
        x, y = self.gunPos()
        rotatedImg = pygame.transform.rotate(self.lImg, self.gunAngle)
        newRect = rotatedImg.get_rect(center=self.lImg.get_rect(topleft =(x - HALF_LASER_SIZE, y - HALF_LASER_SIZE)).center)
        window.blit(rotatedImg, newRect)

        #draw player
        rotatedImg = pygame.transform.rotate(self.img, self.angle*-1)
        newRect = rotatedImg.get_rect(center=self.img.get_rect(topleft =(self.x - HALF_CHARACTER_SIZE, self.y - HALF_CHARACTER_SIZE)).center)
        window.blit(rotatedImg, newRect)

    def rotate(self, point):
        x, y = point

        x -= self.x
        y -= self.y

        y = y*-1

        hyp = math.sqrt(x**2 + y**2)
        
        if not hyp == 0:
            self.angle = math.degrees(math.atan2(x/hyp, y/hyp)) - 90

    def rotateGun(self, dt):
        self.gunAngle += LASER_ROTATION_SPEED * dt
        if self.gunAngle > 360:
            self.gunAngle -= 360

    #returns the amount of hits and return ids of lasers that hit to be removed
    def collide(self, othersLasers, otherMask):
        hitCounter = 0
        ids = []

        for l in range(len(othersLasers)):
            offset = (othersLasers[l].x - self.x, othersLasers[l].y - self.y)
            if self.mask.overlap(otherMask, offset):
                hitCounter += 1
                ids.append(l)

        return hitCounter, ids

    #returns true if dead
    def takeDamage(self, damageTaken):
        die = False
        self.health -= damageTaken
        
        if self.health <= 0:
            #respawn
            self.health = self.maxHealth
            self.setSpawn()
            self.death += 1

            #play sound
            deathSound.play()
            return True
        
        return False

    def fire(self):
        x, y, = self.gunPos()
        self.lasers.append(Laser(x, y, self.angle))
        self.shot.play()
        self.timesShot += 1

    def moveLasers(self, dt):
        for l in range(len(self.lasers)):
            self.lasers[l].x += self.lSpeed*math.cos(math.radians(self.lasers[l].angle)) * dt
            self.lasers[l].y += self.lSpeed*math.sin(math.radians(self.lasers[l].angle)) * dt

    def removeLasers(self, windowX, windowY):
        l = len(self.lasers) - 1
        while l >= 0:
            if self.lasers[l].x + HALF_LASER_SIZE < 0 or self.lasers[l].x - HALF_LASER_SIZE > windowX or self.lasers[l].y + HALF_LASER_SIZE < 0 or self.lasers[l].y - HALF_LASER_SIZE > windowY:
                del self.lasers[l]
            l -= 1
            
    def removeLaserAtIndex(self, id):
        del self.lasers[id]

    def move(self, x, y, dt, windowX, windowY):
        self.x += self.speed*x*dt
        self.y += self.speed*y*dt

        if self.x + HALF_CHARACTER_SIZE > windowX:
            self.x = windowX - HALF_CHARACTER_SIZE
        elif self.x - HALF_CHARACTER_SIZE < 0:
            self.x = HALF_CHARACTER_SIZE
        
        if self.y + HALF_CHARACTER_SIZE > windowY:
            self.y = windowY - HALF_CHARACTER_SIZE
        elif self.y - HALF_CHARACTER_SIZE < 0:
            self.y = HALF_CHARACTER_SIZE
    
    def exit(self):
        self.active = False
    
    def getDeaths(self):
        return self.death

    def getKills(self):
        return self.kills
    
    def getPoints(self):
        return self.kills - self.death