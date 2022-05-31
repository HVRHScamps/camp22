import libhousy
def main(robby: libhousy.robot):
    print("Hello World!")
    print(robby.colorSensor.getProximity())
    robby.climber.Set(1)
    