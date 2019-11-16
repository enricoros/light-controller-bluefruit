# Note: board has: ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A8', 'A9', 'ACCELEROMETER_INTERRUPT', 'ACCELEROMETER_SCL', 'ACCELEROMETER_SDA', 'AUDIO', 'BUTTON_A', 'BUTTON_B', 'D0', 'D1', 'D10', 'D12', 'D13', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'I2C', 'L', 'LIGHT', 'MICROPHONE_CLOCK', 'MICROPHONE_DATA', 'MISO', 'MOSI', 'NEOPIXEL', 'RX', 'SCK', 'SCL', 'SDA', 'SLIDE_SWITCH', 'SPEAKER', 'SPEAKER_ENABLE', 'SPI', 'TEMPERATURE', 'TX', 'UART']
import board
import digitalio
import neopixel
import random
import storage
import time
from adafruit_bluefruit_connect.button_packet import ButtonPacket

from eBoard import *
from ePixels import EPixels
from eBLE import EBLE

# digital inputs
buttonA = setDigitalIn(board.BUTTON_A, digitalio.Pull.DOWN)
buttonB = setDigitalIn(board.BUTTON_B, digitalio.Pull.DOWN)
slideMode = buttonMonitor(setDigitalIn(board.SLIDE_SWITCH, digitalio.Pull.UP))

# digital outputs
led = setDigitalOut(board.L)

# analog inputs (unused)
#analog3 = setAnalogIn(board.A3)
#analog4 = setAnalogIn(board.A4)
#analog5 = setAnalogIn(board.A5)

# pixels (defaults to off)
ePixels1 = EPixels(neopixel.NeoPixel(board.A1, 20, brightness=0.5, auto_write=False))
ePixelsLocal = EPixels(neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.5, auto_write=False))

# other
eBLE = EBLE()
COLOR_UNSET_TUPLE = (8, 8, 8)
COLOR_WHITE = 0xFFFFFF
COLOR_RED   = 0xFF0000

# load initial configuration
frequencyLimiter = 0.01 # 100Hz

# Editor class
class PixelEditor:
    def __init__(self, _epx1, _epx2):
        self.epx1 = _epx1
        self.epx2 = _epx2
        self.count1 = self.epx1.pixCount
        self.count2 = self.epx2.pixCount
        self.count = self.count1 + self.count2
        self.idx = 0
        self.autoHueBase = 0
        # state
        self.applyDefaults()
        self.loadFromStorage()
        # enter
        self.loop()
        self.__moveIdx(0)

    def applyDefaults(self):
        self.bri1 = 2 # over 10
        self.bri2 = 2
        self.colors = [COLOR_UNSET_TUPLE] * self.count
        self.flickers = [0] * self.count
        self.rainbows = [0] * self.count
        self.mutes = [0] * self.count

    def loadFromStorage(self):
        try:
            with open("/pixels.txt", "r") as fp:
                lines = fp.readlines()
        except Exception as e:
            print("LOAD ERROR: " + str(e))
        l = [int(text_number) for text_number in lines]
        # min len: 3
        if len(l) < 3:
            print("error loading, too small: " + len(l))
            return
        count = l[0]
        # stored count = self.count
        if count != self.count:
            print("different count: " + str(count) + ", exp: " + str(self.count))
            return
        # expected length = length
        expLen = 3 + count * 6
        if expLen != len(l):
            print("different length: " + str(len(l)) + ", exp: " + str(expLen))
            return
        # start parsing
        self.bri1 = l[0]
        self.bri2 = l[1]
        # don't reallocate the arrays since the size is the same, so the arrays are in place
        for idx in range(self.count):
            bIdx = 3 + idx * 6
            c0 = l[bIdx]
            c1 = l[bIdx+1]
            c2 = l[bIdx+2]
            self.colors[idx] = (c0, c1, c2)
            self.flickers[idx] = l[bIdx+3]
            self.rainbows[idx] = l[bIdx+4]
            self.mutes[idx] = l[bIdx+5]

    def saveToStorage(self):
        l = [self.count, self.bri1, self.bri2]
        for idx in range(self.count):
            color = self.colors[idx]
            l.append(color[0])
            l.append(color[1])
            l.append(color[2])
            l.append(self.flickers[idx])
            l.append(self.rainbows[idx])
            l.append(self.mutes[idx])
        str_l = '\n'.join([str(number) for number in l])
        try:
            with open("/pixels.txt", "w") as fp:
                fp.write(str_l)
            #digitalSquare(led, 0.05)
        except Exception as e:
            ePixelsLocal.blinkAll(0x800000, 2, 0.5)
            print("SAVE ERROR: " + str(e))

    # main entry point. assuming a 50Hz frequency
    def loop(self):
        self.epx1.pixels.brightness = float(self.bri1) / 10
        self.epx2.pixels.brightness = float(self.bri2) / 10
        for idx in range(self.count):
            ePix, eIdx = self.__ePix(idx)
            color = self.colors[idx]
            flicker = self.flickers[idx]
            rainbow = self.rainbows[idx]
            mute = self.mutes[idx]
            if mute != 0:
                ePix.pixels[eIdx] = 0
            elif rainbow != 0:
                v = (idx * 256 // self.count) + self.autoHueBase
                ePix.pixels[eIdx] = ePix.rgbWheel(v & 255)
            elif flicker != 0:
                factor = random.random()
                color = tuple(int(factor * x) for x in color)
                ePix.pixels[eIdx] = color
            else:
                ePix.pixels[eIdx] = color
        self.epx1.update()
        self.epx2.update()
        self.autoHueBase = self.autoHueBase + 5

    def longPressA(self):
        print("NOT IMPLEMENTED")

    def longPressB(self):
        self.applyDefaults()
        self.saveToStorage()
        self.loadFromStorage()
        self.loop()

    def ePrev(self):
        self.__moveIdx((self.idx - 1) % self.count)

    def eNext(self):
        self.__moveIdx((self.idx + 1) % self.count)

    def eUp(self):
        if self.idx < self.count1:
            if self.bri1 < 10:
                self.bri1 = self.bri1 + 1
        else:
            if self.bri2 < 10:
                self.bri2 = self.bri2 + 1
        self.__save()

    def eDown(self):
        if self.idx < self.count1:
            if self.bri1 > 0:
                self.bri1 = self.bri1 - 1
        else:
            if self.bri2 > 0:
                self.bri2 = self.bri2 - 1
        self.__save()

    def eModeNormal(self):
        self.flickers[self.idx] = 0
        self.rainbows[self.idx] = 0
        self.mutes[self.idx] = 0
        self.__blinkIdx(COLOR_RED)
        self.__save()

    def eToggleFlicker(self):
        self.flickers[self.idx] ^= 1
        self.__blinkIdx(COLOR_RED)
        self.__save()

    def eToggleRainbow(self):
        self.rainbows[self.idx] ^= 1
        self.__blinkIdx(COLOR_RED)
        self.__save()

    def eToggleMute(self):
        self.mutes[self.idx] ^= 1
        self.__blinkIdx(COLOR_RED)
        self.__save()

    def eColor(self, color):
        self.colors[self.idx] = color
        # hack: for the inner circle, change all the colors at once
        if self.idx >= self.count1:
            for n in range(self.count2):
                self.colors[self.count1 + n] = color
        self.__save()

    def __moveIdx(self, idx):
        self.idx = idx
        self.__blinkIdx(COLOR_WHITE)

    def __blinkIdx(self, color):
        ePix, eIdx = self.__ePix(self.idx)
        reps = 1
        if self.mutes[self.idx] != 0:
            reps = 4
        elif self.rainbows[self.idx] != 0:
            reps = 3
        elif self.flickers[self.idx] != 0:
            reps = 2
        ePix.blinkSingle(eIdx, color, reps, 0.2)

    def __ePix(self, idx):
        if idx < self.count1:
            return self.epx1, idx
        return self.epx2, idx - self.count1

    def __save(self):
        self.saveToStorage()

editor = PixelEditor(ePixels1, ePixelsLocal)

# main loop variables
colorMode = 0

# main loop
while True:
    time.sleep(frequencyLimiter)

    # use the SLIDE_SWITCH to enable or disable the configuration mode
    isConfig, configChanged = slideMode.read()
    if configChanged:
        ePixelsLocal.blinkAll(0x800000 if isConfig else 0x008000, 4, 0.05)

    ### CONFIGURATION
    if isConfig:
        command = eBLE.loop()
        if command is None:
            # just blink while waiting commands
            digitalSquare(led, 0.05)
        else:
            # key press
            if command.kind is 1:
                if command.value is ButtonPacket.LEFT:
                    editor.ePrev()
                elif command.value is ButtonPacket.RIGHT:
                    editor.eNext()
                elif command.value is ButtonPacket.UP:
                    editor.eUp()
                elif command.value is ButtonPacket.DOWN:
                    editor.eDown()
                elif command.value is ButtonPacket.BUTTON_1:
                    editor.eModeNormal()
                elif command.value is ButtonPacket.BUTTON_2:
                    editor.eToggleFlicker()
                elif command.value is ButtonPacket.BUTTON_3:
                    editor.eToggleRainbow()
                elif command.value is ButtonPacket.BUTTON_4:
                    editor.eToggleMute()
                else:
                    print('unknown button: ' + command.value)
            # color
            elif command.kind is 2:
                editor.eColor(command.value)
        # A long press (4s)
        if buttonPressedForLong(buttonA, 4, 50):
            ePixelsLocal.blinkAll(0x080080, 4, 0.05)
            editor.longPressA()
        # B long press (4s)
        if buttonPressedForLong(buttonB, 4, 50):
            ePixelsLocal.blinkAll(0x000080, 4, 0.05)
            editor.longPressB()
        # apply to editor
        editor.loop()
        continue

    ### RUNTIME
    # button A toggle between the Editor and 2 Fun modes
    if buttonPressedDebounce(buttonA):
        colorMode = (colorMode + 1) % 3
        # FIXME: HACK: hardcoding the disabling of pixel 10 because it goes crazy (not in mode1)
        ePixels1.setDisableMask(10, 1 if colorMode == 0 else 0)

    if colorMode == 0:
        editor.loop()
        time.sleep(frequencyLimiter) # halves the rate
    elif colorMode == 1:
        ePixels1.autoRainbowAll()
        ePixelsLocal.autoRainbowAll()
    elif colorMode == 2:
        ePixels1.autoRainbowCycle()
        ePixelsLocal.autoRainbowCycle()
