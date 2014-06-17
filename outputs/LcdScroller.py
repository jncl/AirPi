from time import sleep
import threading

# add logging support
import logging
mod_log = logging.getLogger('airpi.LcdScroller')

class LcdScroller(threading.Thread):
    def __init__(self, lcdpanel, rows, cols, data):
        self.log = logging.getLogger('airpi.LcdScroller')
        threading.Thread.__init__(self)
        self.running = False
        self.lcd = lcdpanel
        self.rows = rows
        self.cols = cols
        self.data = data

    def run(self):
        self.running = True
        start = (0, 0, 0, 0)
        finish = (self.cols - 1, self.cols - 1, self.cols - 1, self.cols - 1)
        # s1 = s2 = s3 = s4 = 0
        # f1 = f2 = f3 = f4 = self.cols - 1
        while self.running:
            # scroll through the data
            for i in range(self.rows):
                if finish[i] <= len(self.data[i]):
                    disp_str = self.data[i][start[i]:finish[i]]
                else:
                    disp_str = self.data[i][start[i]:len(self.data[i])] + self.data[i][:finish[i] - len(self.data[i])]

                self.lcd.display_string(disp_str, i + 1)
                if start[i] > len(self.data[i]):
                    start[i] = 0
                    finish[i] = self.cols - 1
            sleep(0.4)

            # self.lcd.display_string(self.data[0][s1:f1], 1)
            # self.lcd.display_string(self.data[1][s2:f2], 2)
            # self.lcd.display_string(self.data[2][s3:f3], 3)
            # self.lcd.display_string(self.data[3][s4:f4], 4)

            # s1 += 1; s2 += 1; s3 += 1; s4 += 1
            # f1 += 1; f2 += 1; f3 += 1; f4 += 1
            # if s1 > len(self.data[0]):
            #     s1 = 0
            #     f1 = self.cols - 1
            # if s21> len(self.data[1]):
            #     s2 = 0
            #     f2 = self.cols - 1
            # if s3 > len(self.data[2]):
            #     s3 = 0
            #     f3 = self.cols - 1
            # if s4 > len(self.data[3]):
            #     s4 = 0
            #     f4 = self.cols - 1

    def stopScroller(self):
        self.running = False

    def updData(self, data):
        self.data = data
