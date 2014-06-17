from time import sleep
import threading

# add logging support
import logging
mod_log = logging.getLogger('airpi.LcdScroller')

class LcdScroller(threading.Thread):
    def __init__(self, lcdpanel, rows, cols, delay, data):
        self.log = logging.getLogger('airpi.LcdScroller')
        threading.Thread.__init__(self)
        self.running = False
        self.lcd = lcdpanel
        self.rows = rows
        self.cols = cols
        self.delay = delay
        self.data = data
        self.backlight = 1

    def run(self):
        self.running = True
        start = [0, 0, 0, 0]
        finish = [self.cols - 1, self.cols - 1, self.cols - 1, self.cols - 1]
        while self.running:
            self.log.debug("Start/Finish: {0} {1}".format(start, finish))
            # scroll through the data
            disp_str = u""
            for i in range(self.rows):
                if finish[i] <= len(self.data[i]):
                    disp_str = self.data[i][start[i]:finish[i]]
                else:
                    disp_str = self.data[i][start[i]:len(self.data[i])] + self.data[i][:finish[i] - len(self.data[i])]

                self.log.debug(u"Display string: {0} {1} {2}".format(disp_str, i + 1, self.backlight))
                self.lcd.display_string(disp_str, i + 1, bl=self.backlight)
                start[i] += 1
                finish[i] += 1
                if start[i] > len(self.data[i]):
                    start[i] = 0
                    finish[i] = self.cols - 1
            sleep(self.delay)

    def stopScroller(self):
        self.running = False

    def updData(self, data, bl):
        self.data = data
        self.backlight = bl