from time import sleep
import threading

class LcdScroller(threading.Thread):
    def __init__(self, lcdpanel, line, data):
        threading.Thread.__init__(self)
        self.running = False
        self.lcdpanel = lcdpanel
        self.line = line
        self.data = data

    def run(self):
        self.running = True
        start = 0
        finish = 19
        while self.running:
            # scroll through the data
            self.lcd.display_string(self.data[start:finish], self.line)
            sleep(0.4)
            start += 1
            finish += 1
            if start > len(self.data):
                start = 0
                finish = 19

    def stopScroller(self):
        self.running = False

    def updData(self, data):
        self.data = data
