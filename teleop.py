import libhousy


class Teleop:
    def __init__(self, robot: libhousy.robot):
        self.robot = robot

    def drive(self, x_axis: float, y_axis: float):
        lthr = y_axis + x_axis
        if abs(lthr) > 1:
            lthr = lthr / abs(lthr)
        rthr = y_axis - x_axis
        if abs(rthr) > 1:
            rthr = rthr / abs(rthr)
        self.robot.lDrive.Set(lthr)
        self.robot.rDrive.Set(rthr)

    def shoot(self):
        self.robot.beltZ1.Set(-0.8)
        self.robot.beltZ2.Set(-0.8)
        self.robot.beltZ3.Set(1)
        self.robot.upperTension.Extend()
        self.robot.lowerTension.Retract()

    def pickup(self):
        self.robot.pickupMotor.Set(1)
        self.robot.pickupPneumatic.Extend()
        self.robot.beltZ1.Set(-0.8)
        self.robot.beltZ2.Set(0)
        self.robot.beltZ3.Set(0)
        self.robot.upperTension.Retract()
        self.robot.lowerTension.Extend()

    def stop(self):
        self.robot.pickupMotor.Set(0)
        self.robot.pickupPneumatic.Retract()
        self.robot.beltZ1.Set(0)
        self.robot.beltZ2.Set(0)
        self.robot.beltZ3.Set(0)

    def anglehood(self, stick : float):
        if stick > 0.4:
            self.robot.shootAngle.Extend()
        elif stick < -0.4:
            self.robot.shootAngle.Retract()
        else:
            self.robot.shootAngle.Stop()
