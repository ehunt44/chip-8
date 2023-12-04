import numpy as np
import random
from time import time
import gamedisplay
from const import *
#from const import DO_OUTPUT, LIMIT_FRAMERATE, MAX_FRAMERATE, RES_Y, RES_X, INCREMENT_I_LOAD, SHIFT_Y, RNG_SEED, SHOW_FRAMETIME, SHOW_INSTRUCTIONS
import countdowns

if DO_OUTPUT:
    import pygame

random.seed(RNG_SEED)


mainMem = np.array([0 for i in range(0xFFF + 1)], dtype=np.uint8)

regV0_F = np.array([0 for i in range(0xF + 1)], dtype=np.uint8)
regI = np.array([0], dtype=np.uint16)
pC = np.array([512], dtype=np.uint16)

stack = np.array([0 for i in range(0xF + 1)], dtype=np.uint16)
sP = np.array([0], dtype=np.uint8)
    
pressedKeys = np.array([], dtype=np.uint8)

screenData = np.array([[0 for i in range(RES_Y)] for i in range(RES_X)], dtype=np.bool_)
spriteData = np.array([], dtype=np.bool_)

lastFrameTime = 0
lastTime = time()

frames = 0

if DO_OUTPUT:
    pyScreen, pxArray = gamedisplay.Init_Pygame()
    gamedisplay.Init_Display(pxArray)
timers = countdowns.Hz60(2, 'timer-2', 0, 0)
timers.start()

def main():
    initMemory()
    

    while 1:

        # check if pygame window is closed
        if DO_OUTPUT:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Close_Porgram()

        # get next instruction
        inst = Fetch_Instruction(pC, mainMem)
        
        if SHOW_INSTRUCTIONS:
            print(f'instruction: {inst}, dec instruction: {int(inst[::2], 16)}:{int(inst[2::], 16)}, instruction PC: {pC[0] - 2}, PC: {pC[0]}\n------------------')

        if inst != '0000':
            # execute instruction
            try:
                opcodeDict[inst[0]](inst)
            except KeyError:
                input('Unknown instruction')



# load game and character data into main mem
def initMemory():
    global mainMem

    # put character data in the first 512 bytes of main memory
    charFile = open('E:\Games\chip-8\charset', 'rb')
    charData = charFile.read()
    charFile.close()

    for index in range(len(charData)):
        mainMem[index] = charData[index]

    # test files:
    # delay_timer_test.ch8
    # SCTEST
    # bc_test.ch8
    # test_opcode.ch8
    # puts game data at the offset 0x200 (512 bytes)
    gameFile = open(GAME, 'rb')
    gameData = gameFile.read()
    gameFile.close()

    for index in range(len(gameData)):
        mainMem[index + 0x200] = gameData[index]

# get the next instruction to perform
def Fetch_Instruction(pC, mainMem):

    byte1 = np.base_repr(mainMem[pC[0]], 16)
    byte2 = np.base_repr(mainMem[pC[0] + 1], 16)
    pC += np.uint16(2)

    while len(byte1) < 2:
        byte1 = '0' + byte1
    while len(byte2) < 2:
        byte2 = '0' + byte2

    return byte1+byte2

def Close_Porgram():
    pygame.quit()
    timers.Stop()
    exit()




def CLS(inst):
    '''# 00E0
    # Clear the display.'''
    global screenData, pxArray, spriteData

    screenData.fill(False)
    if DO_OUTPUT:
        gamedisplay.Init_Display(pxArray)


def Return(inst):
    '''# 00EE
    # Return from a subroutine.'''
    global sP,pC,stack
    
    pC[0] = (stack[sP[0]])
    sP[0] -= 1

def JumpAddr(inst):
    '''# 1nnn
    # Jump to location nnn.'''
    global pC

    pC[0] = int(inst[1::], 16)

def CallAddr(inst):
    '''# 2nnn
    # Call subroutine at nnn.'''
    global sP,stack,pC
    
    sP[0] += 1
    stack[sP] = pC[0]
    pC[0] = int(inst[1::], 16)

def SkipEquelByte(inst):
    '''# 3xkk
    # Skip next instruction if Vx = kk.'''
    global pC, regV0_F
    
    if regV0_F[int(inst[1], 16)] == int(inst[2::], 16):
        pC[0] += 2

def SkipNotEquelByte(inst):
    '''# 4xkk
    # Skip next instruction if Vx != kk.'''
    global pC, regV0_F

    if regV0_F[int(inst[1], 16)] != int(inst[2::], 16):
        pC[0] += 2

def SkipEquelVy(inst):
    '''# 5xy0
    # Skip next instruction if Vx = Vy.'''
    global pC, regV0_F

    if regV0_F[int(inst[1], 16)] == regV0_F[int(inst[2], 16)]:
        pC[0] += 2

def LoadVxByte(inst):
    '''# 6xkk
    # Set Vx = kk.'''
    global regV0_F

    regV0_F[int(inst[1], 16)] = int(inst[2::], 16)

def AddVxByte(inst):
    '''# 7xkk
    # Set Vx = Vx + kk.'''
    global regV0_F
    
    regV0_F[int(inst[1], 16)] += int(inst[2::], 16)

def LoadVxVy(inst):
    '''# 8xy0
    # Set Vx = Vy.'''
    global regV0_F

    regV0_F[int(inst[1], 16)] = regV0_F[int(inst[2], 16)]

def VxORVy(inst):
    '''# 8xy1
    # Set Vx = Vx OR Vy'''
    global regV0_F

    regV0_F[int(inst[1], 16)] = np.bitwise_or(regV0_F[int(inst[1], 16)], regV0_F[int(inst[2], 16)])

def VxANDVy(inst):
    '''# 8xy2
    # Set Vx = Vx AND Vy'''
    global regV0_F
    
    regV0_F[int(inst[1], 16)] = np.bitwise_and(regV0_F[int(inst[1], 16)], regV0_F[int(inst[2], 16)])

def VxXORVy(inst):
    '''# 8xy3
    # Set Vx = Vx XOR Vy.'''
    global regV0_F

    regV0_F[int(inst[1], 16)] = np.bitwise_xor(regV0_F[int(inst[1], 16)], regV0_F[int(inst[2], 16)])

def VxPlusVy(inst):
    '''# 8xy4
    # Set Vx = Vx + Vy, set VF = carry.'''
    global regV0_F

    added = regV0_F[int(inst[1], 16)] + regV0_F[int(inst[2], 16)]

    if added < regV0_F[int(inst[1], 16)]:
        regV0_F[0xF] = 1

    regV0_F[int(inst[1], 16)] = added

def VxMinusVy(inst):
    '''# 8xy5
    # Set Vx = Vx - Vy, set VF = NOT borrow.'''
    global regV0_F

    if regV0_F[int(inst[1], 16)] >= regV0_F[int(inst[2], 16)]:
        regV0_F[0xF] = 1
    else:
        regV0_F[0xF] = 0

    regV0_F[int(inst[1], 16)] -= regV0_F[int(inst[2], 16)]

def BitshiftRight(inst):
    '''# 8xy6
    # Set Vx = Vx SHR 1.'''
    global regV0_F

    if not SHIFT_Y:
        regV0_F[0xF] = int(np.binary_repr(regV0_F[int(inst[1], 16)])[-1])
        regV0_F[int(inst[1], 16)] = np.right_shift(regV0_F[int(inst[1], 16)], 1)

    if SHIFT_Y:
        regV0_F[0xF] = int(np.binary_repr(regV0_F[int(inst[2], 16)])[-1])
        regV0_F[int(inst[1], 16)] = np.right_shift(regV0_F[int(inst[2], 16)], 1)

def VyMinusVx(inst):
    '''# 8xy7
    # Set Vx = Vy - Vx, set VF = NOT borrow.'''
    global regV0_F

    if regV0_F[int(inst[2], 16)] >= regV0_F[int(inst[1], 16)]:
        regV0_F[0xF] = 1
    else:
        regV0_F[0xF] = 0

    regV0_F[int(inst[1], 16)] = regV0_F[int(inst[2], 16)] - regV0_F[int(inst[1], 16)]

def BitshiftLeft(inst):
    '''# 8xyE
    # Set Vx = Vx SHL 1.'''
    global regV0_F

    if not SHIFT_Y:
        regV0_F[0xF] = int(np.binary_repr(regV0_F[int(inst[1], 16)], 8)[0])
        regV0_F[int(inst[1], 16)] = np.left_shift(regV0_F[int(inst[1], 16)], 1)

    if SHIFT_Y:
        regV0_F[0xF] = int(np.binary_repr(regV0_F[int(inst[2], 16)], 8)[0])
        regV0_F[int(inst[1], 16)] = np.left_shift(regV0_F[int(inst[2], 16)], 1)

def SkipNotEquelVy(inst):
    '''# 9xy0
    # Skip next instruction if Vx != Vy.'''
    global regV0_F, pC

    if regV0_F[int(inst[1], 16)] != regV0_F[int(inst[2], 16)]:
        pC[0] += 2

def SetIValue(inst):
    '''# Annn
    # Set I = nnn.'''
    global regI, regV0_F

    regI[0] = int(inst[1::], 16)

def JumpPlusV0(inst):
    '''# Bnnn
    # Jump to location nnn + V0.'''
    global pC, regV0_F

    pC[0] = int(inst[1::], 16) + regV0_F[0x0]

def RNG(inst):
    '''# Cxkk
    # Set Vx = random byte AND kk.'''
    global regV0_F

    regV0_F[int(inst[1], 16)] = np.bitwise_and(random.randint(0,255), int(inst[2::], 16))

def Draw(inst):
    '''# Dxyn
    # Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.'''
    global regV0_F, regV0_F, screenData, regI, spriteData, pxArray, lastFrameTime, lastTime, frames

    frameStart = time()

    collision = False
    x = regV0_F[int(inst[1], 16)]
    y = regV0_F[int(inst[2], 16)]

    spriteData = np.array([[0 for i in range(8)] for i in range(int(inst[3], 16))], dtype=np.bool_)
    
    for row in range(int(inst[3], 16)):
        screenByteStr = ''
        
        # read screen data row from where sprite will be drawn
        for collumn in range(8):
            screenByteStr += str(int(screenData[(collumn + x) % RES_X][(row + y) % RES_Y]))
        screenByte = int(screenByteStr, 2)
        
        # byte of sprite row to be displayed
        spriteByte = mainMem[regI + row]


        # xor spirte byte and screen byte
        xORByte = int(np.bitwise_xor(spriteByte, screenByte))

        # check for collision
        #if not collision and not (xORByte == spriteByte or xORByte == screenByte):
            #collision = True

        spriteByteStr = np.binary_repr(spriteByte[0], 8)
        if not collision:
            for bit in range(8):
                if (screenByteStr[bit] == '1') and (spriteByteStr[bit] == '1'):
                    collision = True
                    break

        # create string of xor byte to be drawn
        xORByteStr = np.binary_repr(xORByte, 8)

        
        # add xor byte string to screen data
        for collumn in range(8):
            screenData[(x + collumn) % RES_X][(y + row) % RES_Y] = int(xORByteStr[collumn])
            spriteData[row][collumn] = int(xORByteStr[collumn])


    if collision:
        regV0_F[0xF] = 1
    else:
        regV0_F[0xF] = 0

    if DO_OUTPUT:
        gamedisplay.Draw_Sprite_Display(pxArray, spriteData, x, y)
        pygame.display.flip()

        if LIMIT_FRAMERATE:
            # halt emulation until next frame
            while time() - lastFrameTime <= (1/MAX_FRAMERATE):
                pass

        lastFrameTime = time()

        if SHOW_FRAMETIME:
            print(f'frametime: {time() - frameStart:.5f}')

        if SHOW_FPS:
            frames += 1
            if time() - lastTime >= 1:
                lastTime = time()
                print(frames)
                frames = 0



    


def SkipPressed(inst):
    '''# Ex9E
    # Skip next instruction if key with the value of Vx is pressed.'''
    global regV0_F, pC

    if DO_OUTPUT:
        pressedKeys = gamedisplay.Get_Input()

        if regV0_F[int(inst[1], 16)] in pressedKeys:
            pC += 2

def SkipNotPressed(inst):
    '''# ExA1
    # Skip next instruction if key with the value of Vx is not pressed.'''
    global pC, regV0_F

    if DO_OUTPUT:
        pressedKeys = gamedisplay.Get_Input()

        if regV0_F[int(inst[1], 16)] not in pressedKeys:
            pC += 2
    else:
        pC += 2

def VxDelayTimer(inst):
    '''# Fx07
    # Set Vx = delay timer value.'''
    global regV0_F

    regV0_F[int(inst[1], 16)] = timers.Get_Delay_Time()

def WaitForKey(inst):
    '''# Fx0A
    # Wait for a key press, store the value of the key in Vx.'''
    global regV0_F

    if DO_OUTPUT:
        pressedKeys = gamedisplay.Get_Input()

        while len(pressedKeys) == 0:
                for event in pygame.event.get():
                    pressedKeys = gamedisplay.Get_Input()
                    if event.type == pygame.QUIT:
                        Close_Porgram()
    else:
        pressedKeys = [0]
        

    regV0_F[int(inst[1], 16)] = pressedKeys[0]

def SetDelayTimer(inst):
    '''# Fx15
    # Set delay timer = Vx.'''
    global regV0_F

    timers.Set_Delay_Time(regV0_F[int(inst[1], 16)])

def SetSoundTimer(inst):
    '''# Fx18
    # Set sound timer = Vx.'''
    global regV0_F
    
    timers.Set_Sound_Time(regV0_F[int(inst[1], 16)])

def IPlusVx(inst):
    '''# Fx1E
    # Set I = I + Vx.'''
    global regI, regV0_F

    regI[0] += regV0_F[int(inst[1], 16)]

def SpriteLocation(inst):
    '''# Fx29
    # Set I = location of sprite for digit Vx.'''
    global regI, regV0_F

    regI[0] = regV0_F[int(inst[1], 16)] * 5

def BCD(inst):
    '''# Fx33
    # Store BCD representation of Vx in memory locations I, I+1, and I+2.'''
    global regI, regV0_F, mainMem

    VxStr = str(regV0_F[int(inst[1], 16)])

    while len(VxStr) < 3:
        VxStr = '0' + VxStr

    mainMem[regI] = int(VxStr[0])
    mainMem[regI + 1] = int(VxStr[1])
    mainMem[regI + 2] = int(VxStr[2])

def RegToMem(inst):
    '''# Fx55
    # Store registers V0 through Vx in memory starting at location I.'''
    global regI, regV0_F, mainMem

    if INCREMENT_I_LOAD:
        for index in range(0, (int(inst[1], 16)) + 1):
            mainMem[regI] = regV0_F[index]
            regI += 1

    if not INCREMENT_I_LOAD:
        for index in range(0, (int(inst[1], 16)) + 1):
            mainMem[regI + index] = regV0_F[index]

def MemToReg(inst):
    '''# Fx65
    # Read registers V0 through Vx from memory starting at location I.'''
    global regI, regV0_F, mainMem

    if INCREMENT_I_LOAD:
        for index in range(0, (int(inst[1], 16)) + 1):
            regV0_F[index] = mainMem[regI]
            regI += 1

    if not INCREMENT_I_LOAD:
        for index in range(0, (int(inst[1], 16)) + 1):
            regV0_F[index] = mainMem[regI + index]




def dict0(inst):
    opcodeDict0[inst[3]](inst)

def dict8(inst):
    opcodeDict8[inst[3]](inst)

def dictE(inst):
    opcodeDictE[inst[3]](inst)

def dictF(inst):
    opcodeDictF[inst[2::]](inst)

opcodeDict = {'0':dict0,'1':JumpAddr, '2':CallAddr, '3':SkipEquelByte, '4':SkipNotEquelByte,
    '5':SkipEquelVy, '6':LoadVxByte, '7':AddVxByte, '8':dict8, '9':SkipNotEquelVy, 'A':SetIValue, 'B':JumpPlusV0, 'C':RNG, 'D':Draw, 'E':dictE, 'F':dictF}

opcodeDict0 = {'0':CLS, 'E':Return}

opcodeDict8 = {'0':LoadVxVy, '1':VxORVy, '2':VxANDVy, '3':VxXORVy, '4':VxPlusVy, '5':VxMinusVy, '6':BitshiftRight, '7':VyMinusVx, 'E':BitshiftLeft}

opcodeDictE = {'E':SkipPressed, '1':SkipNotPressed}

opcodeDictF = {'07':VxDelayTimer, '0A':WaitForKey, '15':SetDelayTimer, '18':SetSoundTimer, '1E':IPlusVx, '29':SpriteLocation, '33':BCD, '55':RegToMem, '65':MemToReg}

if __name__ == '__main__':
    main()