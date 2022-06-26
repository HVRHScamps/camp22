# camp22
A Robotics learning platform created by [Jacob Ellington](https://github.com/cannotilever) for Housatonic Valley Regional High School

## Intended Use
This system was developed as part of a week-long Python course for roughtly 8-12th grade beginner programmers.
Students write modules in the other repos in the HVRHScamps organization which are atomatically pulled and assessed by 
robot's `modhandler` before execution. 

## Installation
Don't.


In its current state this software is really not suitable for general use and needs a lot of tinkering from me to work properly.
Hopefully I can change this in the future but right now this is basically in alpha.

## Hardware
In its current iteration this software is not very flexable, it is designed for the very specific setup of our specific robot.
The Robo-Rio on the robot directly controls all actuators for saftey reasons (we don't want bad student code getting the drive system stuck on)
The mounted Raspberry Pis comminucate via NetworkTables with each other and with the Robo-Rio
Controlls are via a Bluetooth Xbox One controller

### The Robot
FRC [Team 716](https://github.com/716robotics)'s 2019 (Infinite Recharge) competition robot
- 4x Mini-CIM tank drivetrain with encoders
- 3-section belt ball storage and feed system with pneumatic belt tensioners
- Shoot wheel with geartooth sensor
- 1-axis pitch articulated turret for ball elevation control with PLG motor and integrated encoder
- pneumatic articulated pickup arm
- NAVX MXP IMU sensor

### The Add-ons
A raspberry Pi 4b with Raspberry Pi 7" touchscreen that runs this camp22 code
A raspberry pi 3b+ with Sense HAT that runs supplimentary visuals 

Note: The Pi 4b is running Ubuntu Desktop because this project requires python 3.10 which Raspberry Pi OS does not ship
at time of writing, and I could not get the Xbox controllers to work on Raspberry Pi OS while they do on both Ubuntu and Fedora for Raspberry Pi

## Why python?
This project is admittedly way more complicated than it needs to be because I am trying to maintain a high level of saftey
in spite of Python's GIL. However, since this software was created for an educational program for absolute beginners and python is easy.
Reasistically, no 8th grader is going to have a robot up and running from scratch in a week using a more preferable language like C++
