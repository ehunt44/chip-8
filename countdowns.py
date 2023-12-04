import time
import threading

class Hz60 (threading.Thread):
    def __init__(self, threadID, name, delayTime, soundTime):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

        self.__delayTimer = delayTime
        self.__soundTimer = soundTime
        self.__running = True

    def run(self):
        print(f'{self.name} started')
        while self.__running:
            time.sleep(1/60)
            if self.__delayTimer > 0:
                self.__delayTimer -= 1
            if self.__soundTimer > 0:
                self.__soundTimer -= 1
        print(f'{self.name} killed')

    def Get_Delay_Time(self):
        return self.__delayTimer

    def Set_Delay_Time(self, delayTime):
        self.__delayTimer = delayTime

    def Get_Sound_Time(self):
        return self.__soundTimer

    def Set_Sound_Time(self, soundTime):
        self.__soundTimer = soundTime

    def Stop(self):
        self.__running = False