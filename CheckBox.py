import pygame

checkMark = pygame.image.load("checkMark.png")

class CheckBox:
    def __init__(self, x, y, w, h, col, active, isInteractive):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.isInteractive = isInteractive
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.img = pygame.transform.scale(checkMark, (self.w, self.h))
        self.col = col

        self.active = active
    
    def draw(self, window, point, col):
        if self.isInteractive:
            if self.rect.collidepoint(point):
                pygame.draw.rect(window, col, self.rect)
            else:
                pygame.draw.rect(window, self.col, self.rect)

        
        if self.active:
            window.blit(self.img, (self.x, self.y))
        
        pygame.draw.rect(window, (0, 0, 0), self.rect, 5)
    
    def click(self, point):
        if self.rect.collidepoint(point) and self.isInteractive:
            self.active = not self.active
            return True
        return False
    
    def setActive(self, active):
        self.active = active
    
    def setInteractive(self, interactive):
        self.isInteractive = interactive

    def getActive(self):
        return self.active