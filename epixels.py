# This module automates pixels
#
# Use this like:
#   pixels1 = neopixel.NeoPixel(board.A1, 20, brightness=0.2, auto_write=False)
#   p = EPixels(pixels1)
#   p.setAll(0xff0000) # red
#   p.setDisableMask(10, 0) # stops a bad pixel

import time

class EPixels:
    def __init__(self, pixels):
        self.pixels = pixels
        self.pixCount = len(self.pixels)
        self.pixelMask = [1] * self.pixCount
        self.autoHue = 0
        self.blank()

    def autoRainbowAll(self):
        self.autoHue = self.autoHue + 1
        self.rainbowAll(self.autoHue)

    def autoRainbowCycle(self):
        self.autoHue = self.autoHue + 1
        self.rainbowCycle(self.autoHue)

    def blank(self):
        self.setAll(0)

    def setAll(self, color):
        for i in range(self.pixCount):
            self.pixels[i] = color
        self.update()

    def blinkAll(self, color, rep, delay):
        for _ in range(rep):
            self.setAll(color)
            time.sleep(delay/2)
            self.setAll(0)
            time.sleep(delay/2)

    def blinkSingle(self, idx, color, rep, delay):
        for _ in range(rep):
            self.pixels[idx] = color
            self.update()
            time.sleep(delay/2)
            self.pixels[idx] = 0
            self.update()
            time.sleep(delay/2)

    def setDisableMask(self, index, value):
        index = index - 1
        if index >= 0 and index < self.pixCount:
            self.pixelMask[index] = value
            self.update()
        else:
            print("EPixels.setMask: value out of range")

    # hueBase: 0..255
    def rainbowAll(self, hueBase):
        for i in range(self.pixCount):
            idx = int(i + hueBase)
            self.pixels[i] = self.rgbWheel(idx & 255)
        self.update()

    # hueShiftBase: 0..255
    def rainbowCycle(self, hueShiftBase):
        for i in range(self.pixCount):
            idx = (i * 256 // self.pixCount) + hueShiftBase * 5
            self.pixels[i] = self.rgbWheel(idx & 255)
        self.update()

    # 0..255: transitions r - g - b - back to r.
    def rgbWheel(self, w):
        if w < 0 or w > 255:
            return (0, 0, 0)
        if w < 85:
            return (255 - w * 3, w * 3, 0)
        if w < 170:
            w -= 85
            return (0, 255 - w * 3, w * 3)
        w -= 170
        return (w * 3, 0, 255 - w * 3)

    # update, keeping the mask into account
    def update(self):
        for i in range(self.pixCount):
            if self.pixelMask[i] is 0:
                self.pixels[i] = 0
        self.pixels.show()

