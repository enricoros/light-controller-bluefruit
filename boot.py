# only if the switch is in programming mode AT BOOT, write access will be granted
import board
import digitalio
import storage

switch = digitalio.DigitalInOut(board.SLIDE_SWITCH)
switch.switch_to_input(pull=digitalio.Pull.UP)

# If the switch is grounded (to the left),
# CircuitPython can write to the drive
storage.remount("/", not switch.value)
