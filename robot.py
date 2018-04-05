#!/usr/bin/env python3

import wpilib
from wpilib.drive import DifferentialDrive


class MyRobot(wpilib.IterativeRobot):
    
    def robotInit(self):
        
        # initialize the timer
        self.timer = wpilib.Timer()
        
        # set variables used in drive loops
        self.DriveSpd = 1  # Default drive speed (only use for teleop)
        self.RotationSpd = 1  # Default rotation speed
        
        self.ShooterSpd = 1  # Default shooter speed
        self.ShooterEnable = 0  # Set the shooter to Disabled by default
        self.Direction = -1  # Set direction to -1 (which is forward sadly)
        self.SpeedAut = 0  # This is the Drive Speed for autonomous
        self.ReachedSwitch = 0  # This is the value used to check if we
        # have reached the switch yet
        
        # Initialize the encoders (order is unintuitive)
        self.EncoderB = wpilib.encoder.Encoder(0, 1, True)
        self.EncoderA = wpilib.encoder.Encoder(2, 3, True)
        
        # Initialize the drive train motors.
        self.frontLeft = wpilib.Spark(0)
        self.rearLeft = wpilib.Spark(1)
        self.left = wpilib.SpeedControllerGroup(self.frontLeft,
                                                self.rearLeft)
        
        self.frontRight = wpilib.Spark(2)
        self.rearRight = wpilib.Spark(3)
        self.right = wpilib.SpeedControllerGroup(self.frontRight,
                                                 self.rearRight)
        
        self.drive = DifferentialDrive(self.left, self.right)
        
        # Initialize the joysticks
        self.stick1 = wpilib.Joystick(0)
        self.stick2 = wpilib.Joystick(1)
        
        # Initialize the shooter motors
        self.Lshoot = wpilib.Spark(4)
        self.Rshoot = wpilib.Spark(5)
        self.shoot = wpilib.SpeedControllerGroup(self.Lshoot,
                                                 self.Rshoot)
    
    def teleopInit(self):
        pass
    
    def teleopPeriodic(self):
        
        # Call the functions to drive and shoot and
        # pass them the values.
        # This is called by the FMS periodically.
        self.drive.arcadeDrive(
            ((self.stick1.getY() * self.DriveSpd) * self.Direction),
            (self.stick1.getX()))
        self.shoot.set(
            self.ShooterSpd * (self.stick1.getThrottle() + 1))
        
        # Print the throttle value from the joystick
        # (for driver's reference and debugging)
        print(self.stick1.getThrottle())
        
        # Buttons to control the shooter.
        # -1 is forward 1 is backwards (unfortunately)
        if self.stick1.getRawButton(1):
            self.ShooterSpd = -1
        elif self.stick1.getRawButton(5):
            self.ShooterSpd = -1
        elif self.stick1.getRawButton(3):
            self.ShooterSpd = 1
        else:
            self.ShooterSpd = 0
        
        # Button to change direction
        if self.stick1.getRawButton(12):
            self.Direction = 1
        else:
            self.Direction = -1
        
        # Button to activate slow mode
        if self.stick1.getRawButton(2):
            self.DriveSpd = 0.6
        else:
            self.DriveSpd = 1
    
    def autonomousInit(self):
        # Start the timer (This has to be in Init because you shouldn't
        # start the timer periodically (duh)
        self.timer.start()
    
    def autonomousPeriodic(self):
        
        # Get the data about Alliance sides from the DriverStation
        self.gamedata = wpilib.DriverStation \
            .getInstance() \
            .getGameSpecificMessage()
        
        # Call the functions to drive and shoot
        # and pass them the variables
        self.drive.arcadeDrive(self.SpeedAut, 0)
        self.shoot.set(self.ShooterSpd * self.ShooterEnable)
        
        # Print the encoder calues to the driver station (for debugging)
        print("A", self.EncoderA.get())
        print("B", self.EncoderB.get())
        
        # Drive to the switch and stop after 6 seconds or when we reach
        # The right distance using the encoders
        if self.timer.get() < 6 and self.EncoderA.get() > -69.9 * 25:
            self.SpeedAut = -0.6
        else:
            self.SpeedAut = 0
            self.ReachedSwitch = 1
        
        # Shoot the cube after 6 seconds and after ReachedSwitch is
        # Set to 1 then stop after 2 seconds
        if self.timer.get() < 6:
            self.ShooterSpd = 0
        elif self.timer.get() < 8 and self.ReachedSwitch == 1:
            self.ShooterSpd = 1
        elif self.timer.get() < 10:
            self.ShooterSpd = 0
        else:
            self.ShooterSpd = 0
        
        # Check if we are on the right and enable/disable the shooter
        # accordingly
        if self.gamedata == "RRR" or self.gamedata == "RLR":
            self.ShooterEnable = 1
        elif self.gamedata == "LLL" or self.gamedata == "LRL":
            self.ShooterEnable = 0
        else:
            self.ShooterEnable = 0


if __name__ == '__main__':
    wpilib.run(MyRobot)
