# audio manipulation functions
from audiocore import RawSample
from audiopwmio import PWMAudioOut as AudioOut

class EAudio:
    def __init__(self):
        import array
        self.audio = AudioOut(board.SPEAKER)
        self.SAMPLE_RATE = 8000
        self.sampleWave = array.array("H", [0] * self.SAMPLE_RATE)
        print(len(self.sampleWave))

    def enableSpeaker(self):
        self.speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
        self.speaker_enable.direction = digitalio.Direction.OUTPUT
        self.speaker_enable.value = True

    def genSineWave(self):
        import math
        FREQUENCY = 440  # 440 Hz middle 'A'
        #for i in range(self.SAMPLE_RATE):
        #    self.sampleWave[i] = int(math.sin(math.pi * 2 * i / 18) * (2 ** 15) + 2 ** 15)

    def playWave(self):
        # Keep playing the sample over and over, for 1 second
        self.audio.play(self.sampleWave, loop=True)
        time.sleep(1)
        self.audio.stop()

    def play_file(filename):
        print("Playing file: " + filename)
        self.sampleWave = open(filename, "rb")
        with WaveFile(wave_file) as wave:
            with AudioOut(board.SPEAKER) as audio:
                audio.play(wave)
                while audio.playing:
                    pass
        print("Finished")
