"""Releases any stepper motors"""
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor


def main():
    """Releases any stepper motors"""
    motor_hat = Adafruit_MotorHAT()
    motor_hat.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    motor_hat.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    motor_hat.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    motor_hat.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

if __name__ == '__main__':
    main()
