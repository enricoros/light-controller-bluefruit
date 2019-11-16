# misc board functions
import analogio
import digitalio
import time

# set pins
def setDigitalIn(pin, _pull):
    e = digitalio.DigitalInOut(pin)
    e.switch_to_input(pull=_pull)
    return e

def setDigitalOut(pin):
    e = digitalio.DigitalInOut(pin)
    e.direction = digitalio.Direction.OUTPUT
    return e

def setAnalogIn(pin):
    return analogio.AnalogIn(pin)

# read pins
def buttonPressed(digitalIn):
    return digitalIn.value is True

def buttonPressedDebounce(digitalIn):
    if digitalIn.value is True:
        time.sleep(0.2)
        return True
    return False

def buttonPressedForLong(digitalIn, seconds, samples):
    if digitalIn.value is False:
        return False
    for _ in range(samples):
        if digitalIn.value is False:
            return False
        time.sleep(seconds/samples)
    return True

class buttonMonitor:
    def __init__(self, _digitalIn):
        self.digitalIn = _digitalIn
        self.lastState = self.digitalIn.value

    def read(self):
        state = self.digitalIn.value
        changed = state != self.lastState
        self.lastState = state
        return state, changed

# write pins
def digitalSquare(digitalOut, delay):
    digitalOut.value = True
    time.sleep(delay)
    digitalOut.value = False
    time.sleep(delay)

def digitalSquares(digitalOut, repeat, delay):
    for _ in range(repeat):
        digitalSquare(digitalOut, delay)
