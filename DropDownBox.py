import pygame, Button

class DropDownBox:
    def __init__(self, options, x, y, col, bgCol, isInteractive, font):
        self.options  = options
        self.selected = 0
        self.x = x
        self.y = y
        self.col = col
        self.bgCol = bgCol
        self.active = False
        self.isInteractive = isInteractive
        
        self.buttons = []
        maxWidth = 0
        for o in range(len(self.options)):
            self.buttons.append(Button.Button(self.x, y, font, self.bgCol, self.options[o]))
            self.buttons[o].setShowOutline(False)
            
            #make next button show up under
            y = self.buttons[o].rect.y + self.buttons[o].rect.h + 10

            if self.buttons[o].rect.w > maxWidth:
                maxWidth = self.buttons[o].rect.w
        
        for b in range(len(self.buttons)):
            self.buttons[b].rect.w = maxWidth
        
        totalHeight = y - self.y

        self.rect = pygame.Rect(self.x, self.y, maxWidth, totalHeight)
    
    def draw(self, window, point, col, notPossibleOptions):
        if self.active:
            #draw and determine if should highlight because cursor is over it
            pygame.draw.rect(window, self.bgCol, self.rect)

            for b in self.buttons:
                if b.collidePoint(point) and not b.text in notPossibleOptions:
                    b.changeBoxColor(col)

                b.draw(window)
                b.changeBoxColor(self.bgCol)
            
            pygame.draw.rect(window, self.col, self.rect, 5)
        
        elif self.isInteractive:
            self.buttons[self.selected].setShowOutline(True)
            if self.buttons[self.selected].collidePoint(point):
                    self.buttons[self.selected].changeBoxColor(col)
            self.buttons[self.selected].draw(window)

            self.buttons[self.selected].changeBoxColor(self.bgCol)
            self.buttons[self.selected].setShowOutline(False)
        else:
            self.buttons[self.selected].draw(window)
    
    def setActive(self, active):
        if self.isInteractive:
            self.active = active
    
    def getSelected(self):
        return self.buttons[self.selected].text

    def click(self, point, notPossibleOptions):
        #change made in selection
        change = False
        #get selected box
        if self.active:
            newIndex = self.selected
            for b in range(len(self.buttons)):
                if self.buttons[b].collidePoint(point):
                    newIndex = b
                    break
            
            if not newIndex == self.selected and not self.buttons[newIndex].text in notPossibleOptions:
                oldSelectedText = self.buttons[self.selected].text
                self.buttons[self.selected].changeText(self.buttons[newIndex].text)
                self.buttons[newIndex].changeText(oldSelectedText)
                
                #re update the width for the swapped buttons
                self.buttons[newIndex].rect.w = self.rect.w
                self.buttons[self.selected].rect.w = self.rect.w
                change = True

            #end active as new pick has either been determined or clicked off of it unless unusable option
            if not self.buttons[newIndex].text in notPossibleOptions:
                self.active = False
        elif self.isInteractive:
            if self.buttons[self.selected].collidePoint(point):
                self.active = True
        
        return change
    
    #swap out the selected content for another content
    def swapSelected(self, text):
        self.buttons[self.selected].changeText(text)
        self.buttons[self.selected].rect.w = self.rect.w
    
    def setInteractive(self, interactive):
        self.isInteractive = interactive
