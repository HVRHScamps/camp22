# A class to handle SensePi's LED matrix
import time
import networktables


class Leds:
    dead_flag = False
    dead_timer = 0

    def __init__(self):
        self.sensors = networktables.NetworkTables.getTable("sensors")

    def run(self, override=None, status=None):
        match override:
            case "dead":
                self.dead_flag = True
                self.dead_timer = time.time()
                self.sensors.putString("display", "dead")
            case None:
                if self.dead_flag:
                    self.dead_flag = not (time.time() - self.dead_timer > 4)
                else:
                    if status is not None:
                        ok = 0
                        for i in status:
                            if status[i]:
                                ok += 1
                        match ok:
                            case 0 | 1:
                                self.sensors.putString("display", "sad1")
                            case 2 | 3:
                                self.sensors.putString("display", "sad2")
                            case 4 | 5:
                                self.sensors.putString("display", "neutral")
                            case 6 | 7 | 8:
                                self.sensors.putString("display", "happy1")
                            case 9 | 10:
                                self.sensors.putString("display", "happy2")
            case _:
                self.sensors.putString("display", override)