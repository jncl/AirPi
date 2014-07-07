from time import sleep
import threading

# add logging support
import logging
mod_log = logging.getLogger('airpi.LcdScroller')

class LcdScroller(threading.Thread):
    def __init__(self, lcdpanel, rows, cols, delay, sl, data):
        threading.Thread.__init__(self)
        self.log = logging.getLogger('airpi.LcdScroller')
        self.running = False
        self.lcd = lcdpanel
        self.rows = rows
        self.cols = cols
        self.delay = delay
        self.sl = sl
        self.data = data
        self.bl = 0

    def run(self):
        self.running = True
        start = [0] * self.rows
        finish = [self.cols - 1] * self.rows
        try:
            while self.running:
                # self.log.debug("Start/Finish: {0} {1} {2}".format(start, finish, map(len, data)))
                # scroll through the data
                disp_str = u""
                for i in range(self.rows):
                    # handle non scrolling data
                    if self.sl[i] == 0:
                        disp_str = self.data[i]
                    else:
                        # scroll data
                        if finish[i] <= len(self.data[i]):
                            disp_str = self.data[i][start[i]:finish[i]]
                        else:
                            disp_str = self.data[i][start[i]:len(self.data[i])] + self.data[i][:finish[i] - len(self.data[i])]
                        start[i] += 1
                        finish[i] += 1
                        if start[i] == len(self.data[i]):
                            start[i] = 0
                            finish[i] = self.cols - 1

                    # self.log.debug(u"Display string: {0} [{1}] {2}".format(i + 1, disp_str, self.bl))
                    self.lcd.display_string(disp_str, i + 1, bl=self.bl)
                sleep(self.delay)
        except Exception as e:
            self.log.error("Error Scrolling lines: {0}".format(e))
            raise

    def stopScroller(self):
        self.running = False

    def updData(self, sl, data, bl):
        self.sl = sl
        self.data = data
        self.bl = bl