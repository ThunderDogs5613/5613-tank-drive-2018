#!/usr/bin/env python3

import wpilib
# from robotpy_ext.common_drivers.navx import AHRS
from wpilib.drive import DifferentialDrive
# from robotpy_ext.common_drivers import navx
from networktables import NetworkTables


# from robotpy_ext.control.toggle import Toggle


class MyRobot(wpilib.IterativeRobot):
        """This is a demo program showing the use of the navX MXP to implement
        a "rotate to angle" feature. This demo works in the pyfrc simulator.
 
        This example will automatically rotate the robot to one of four
        angles (0, 90, 180 and 270 degrees).
 
        This rotation can occur when the robot is still, but can also occur
        when the robot is driving.  When using field-oriented control, this
        will cause the robot to drive in a straight line, in whatever direction
        is selected.
 
        This example also includes a feature allowing the driver to "reset"
        the "yaw" angle.  When the reset occurs, the new gyro angle will be
        0 degrees.  This can be useful in cases when the gyro drifts, which
        doesn't typically happen during a FRC match, but can occur during
        long practice sessions.
 
        Note that the PID Controller coefficients defined below will need to
        be tuned for your drive system.
        """
        
        # The following PID Controller coefficients will need to be tuned */
        # to match the dynamics of your drive system.  Note that the      */
        # SmartDashboard in Test mode has support for helping you tune    */
        # controllers by displaying a form where you can enter new P, I,  */
        # and D constants and test the mechanism.                         */
        
        # Often, you will find it useful to have different parameters in
        # simulation than what you use on the real robot
        
        if wpilib.RobotBase.isSimulation():
                # These PID parameters are used in simulation
                kP = 0.06
                kI = 0.00
                kD = 0.00
                kF = 0.00
        else:
                # These PID parameters are used on a real robot
                kP = 0.03
                kI = 0.00
                kD = 0.00
                kF = 0.00
        
        kToleranceDegrees = 2.0
        
        def robotInit(self):
                
                # initialize the timer
                self.timer = wpilib.Timer()
                
                # set variables used in drive loops
                self.DriveSpd = 1  # Default drive speed (only use for teleop)
                self.RotationSpd = 1  # Default rotation speed
                
                self.ShooterSpd = 1  # Default shooter speed
                self.ShooterEnable = 0 # Set the shooter to Disabled by default
                self.Direction = -1 # Set direction to -1 (which is forward sadly)
                self.SpeedAut = 0 # This is the Drive Speed for autonomous
                self.ReachedSwitch = 0 # This is the value used to check if we
                                       # have reached the switch yet
                
                # For Toggling Buttons
                # self.toggle7 = Toggle(self.stick1, 7)
                # self.toggle1 = Toggle(self.stick1, 1)
                # self.toggle6 = Toggle(self.stick1, 6)
                # self.toggle4 = Toggle(self.stick1, 4)
                # self.toggle5 = Toggle(self.stick1, 5)
                # self.toggle3 = Toggle(self.stick1, 3)
                # self.toggle2 = Toggle(self.stick1, 2)
                
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
                self.Lshoot = wpilib.Spark(5)
                self.Rshoot = wpilib.Spark(6)
                self.shoot = wpilib.SpeedControllerGroup(self.Lshoot,
                                                         self.Rshoot)
        
        def teleopInit(self):
                pass
        
        def teleopPeriodic(self):
                
                # Call the functions to drive and shoot and
                # pass them the values.
                # This is called by the FMS periodically.
                self.drive.arcadeDrive(
                        (self.stick1.getY() * self.DriveSpd) * self.Direction,
                        self.stick1.getX())
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
