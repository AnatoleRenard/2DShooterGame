import pygame

class Button:
    def __init__(self, x, y, font, col, text):
        self.font = font
        self.col  = col
        self.text = text
        self.w, self.h = self.font.size(self.text)
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, self.w + 10, self.h + 10)

        self.showOutline = True
        self.showBackgroundCol = True
        
        self.textCol = (0, 0, 0)
        self.outlineCol = (0, 0, 0)

    def draw(self, window):
        tx = self.rect.x + (self.rect.width - self.w) // 2
        ty = self.rect.y + (self.rect.height - self.h) // 2

        if self.showBackgroundCol:
            pygame.draw.rect(window, self.col, self.rect)
        if self.showOutline:
            pygame.draw.rect(window, self.outlineCol, self.rect, 5)
        window.blit(self.font.render(self.text, True, self.textCol), (tx, ty))
    
    def changeBoxColor(self, newCol):
        self.col = newCol
    
    def changeTextCol(self, newCol):
        self.textCol = newCol
    
    def changeOutlineCol(self, newCol):
        self.outlineCol = newCol
    
    def changeText(self, text):
        self.text = text
        #update rectangle arround button
        self.w, self.h = self.font.size(self.text)
        self.rect = pygame.Rect(self.x, self.y, self.w + 10, self.h + 10)

    def setShowOutline(self, show):
        self.showOutline = show
    
    def setShowBackgroundCol(self, show):
        self.showBackgroundCol = show
    
    def collidePoint(self, point):
        return self.rect.collidepoint(point)
