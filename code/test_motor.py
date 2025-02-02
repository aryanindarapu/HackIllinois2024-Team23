import numpy as np
from src import motor as motor_module
import time

if __name__ == '__main__':

    motor1 = motor_module.Motor({
        "pins": {
            "speed": 13,
            "control1": 5,
            "control2": 6
        }
    })

    motor2 = motor_module.Motor({
        "pins": {
            "speed": 12,
            "control1": 7,
            "control2": 8
        }
    })

    speeds = list(np.linspace(0, 1, 11)) + list(np.linspace(0.9, 0, 10))

    dt = 0.25
    motor1.stop()
    motor2.stop()
    time.sleep(dt)

    # for speed in speeds:
    #     print('Motor forward at {}% speed'.format(speed * 100))
    #     motor1.forward(speed)
    #     motor2.forward(speed)
    #     time.sleep(dt)

    # for speed in speeds:
    #     print('Motor backward at {}% speed'.format(speed * 100))
    #     motor1.backward(speed)
    #     motor2.backward(speed)
    #     time.sleep(dt)
    start_time = time.time()
    while time.time() - start_time < 10:
        motor1.forward(0.2)
        motor2.forward(0.2)
        time.sleep(dt)

    motor1.stop()
    motor2.stop()
