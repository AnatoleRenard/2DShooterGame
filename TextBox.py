import pygame

class TextBox:
    def __init__(self, font, col, prompt, x, y, active, maxChar):
        self.font = font
        self.col = col
        self.prompt = prompt
        self.fontSizeW, self.fontSizeH = font.size("A")
        self.active = active
        self.maxChar = maxChar
        self.text = ""
        self.rect = pygame.Rect(x, y, self.fontSizeW*(self.maxChar + len(self.prompt)), self.fontSizeH)

    def changeColor(self, newCol):
        self.col = newCol
    
    def setActive(self, newActive):
        self.active = newActive

    def addText(self, text):
        if len(self.text) < self.maxChar and self.active:
            self.text += text
    
    def removeText(self):
        if self.active:
            self.text = self.text[:-1]

    def draw(self, window):
        window.blit(self.font.render(self.prompt + self.text, True, self.col), (self.rect.x, self.rect.y))
        if self.active and len(self.text) < self.maxChar:
            w, h = self.font.size(self.prompt + self.text)
            pygame.draw.rect(window, self.col, (self.rect.x + w, self.rect.y, self.fontSizeW, self.fontSizeH))

    def collidePoint(self, point):
        return self.rect.collidepoint(point)

    def getLength(self):
        return len(self.text)

    def isEmpty(self):
        return len(self.text) == 0