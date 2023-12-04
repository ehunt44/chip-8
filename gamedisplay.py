import pygame
from const import RES_X, RES_SCALE, RES_Y, ALLOWED_KEYS, KEY_DICT, ON_COLOR, OFF_COLOR, BG_COLOR


# create pygame window
def Init_Pygame():
    gameWindow = pygame.display.set_mode((RES_X * RES_SCALE, RES_Y * RES_SCALE))
    pygame.key.set_repeat(1, 1)
    pixelArray = pygame.PixelArray(gameWindow)
    pygame.init()
    return gameWindow, pixelArray

# unused old update entire display at once code
def Draw_Entire_Display(pxArray, screenData):
    pxArray[0:RES_X*RES_SCALE, 0:RES_Y*RES_SCALE] = BG_COLOR

    for xPixel in range(RES_X):
        for yPixel in range(RES_Y):
            if screenData[xPixel][yPixel] == 1:
                if RES_SCALE >= 3:
                    pxArray[(xPixel * RES_SCALE)+1:((xPixel + 1) * RES_SCALE)-1, (yPixel * RES_SCALE)+1:((yPixel + 1) * RES_SCALE)-1] = ON_COLOR
                else:
                    pxArray[xPixel * RES_SCALE:(xPixel + 1) * RES_SCALE, yPixel * RES_SCALE:(yPixel + 1) * RES_SCALE] = ON_COLOR
            else:
                if RES_SCALE >= 3:
                    pxArray[(xPixel * RES_SCALE)+1:((xPixel + 1) * RES_SCALE)-1, (yPixel * RES_SCALE)+1:((yPixel + 1) * RES_SCALE)-1] = OFF_COLOR
                else:
                    pxArray[xPixel * RES_SCALE:(xPixel + 1) * RES_SCALE, yPixel * RES_SCALE:(yPixel + 1) * RES_SCALE] = OFF_COLOR

    pygame.display.flip()

# creates the background grid
def Init_Display(pxArray):
    pxArray[0:RES_X*RES_SCALE, 0:RES_Y*RES_SCALE] = BG_COLOR

    for xPixel in range(RES_X):
        for yPixel in range(RES_Y):
            if RES_SCALE >= 3:
                pxArray[(xPixel * RES_SCALE)+1:((xPixel + 1) * RES_SCALE)-1, (yPixel * RES_SCALE)+1:((yPixel + 1) * RES_SCALE)-1] = OFF_COLOR
            else:
                pxArray[xPixel * RES_SCALE:(xPixel + 1) * RES_SCALE, yPixel * RES_SCALE:(yPixel + 1) * RES_SCALE] = OFF_COLOR

    pygame.display.flip()

# draw sprite to screen
def Draw_Sprite_Display(pxArray, spriteData, x, y):
    for row in spriteData:
        for xindex in range(8):
            xPixel = row[xindex]
            xStart = (x + xindex)%RES_X
            xEnd = xStart + 1

            yStart = y%RES_Y
            yEnd = yStart + 1
        
            if xPixel == 1:
                if RES_SCALE >= 3:
                    pxArray[(xStart*RES_SCALE)+1:(xEnd*RES_SCALE)-1, (yStart*RES_SCALE)+1:(yEnd*RES_SCALE)-1] = ON_COLOR
                else:
                    pxArray[xStart*RES_SCALE:xEnd*RES_SCALE, yStart*RES_SCALE:yEnd*RES_SCALE] = ON_COLOR
            else:
                if RES_SCALE >= 3:
                    pxArray[(xStart*RES_SCALE)+1:(xEnd*RES_SCALE)-1, (yStart*RES_SCALE)+1:(yEnd*RES_SCALE)-1] = OFF_COLOR
                else:
                    pxArray[xStart*RES_SCALE:xEnd*RES_SCALE, yStart*RES_SCALE:yEnd*RES_SCALE] = OFF_COLOR
        y += 1

# return a list of all allowed keys that are pressed
def Get_Input():
    pressedKeys = []

    keys = pygame.key.get_pressed()
    for index in range(len(keys)):
        if keys[index] > 0 and index in ALLOWED_KEYS:
            pressedKeys.append(index)

    return [KEY_DICT[key] for key in pressedKeys]