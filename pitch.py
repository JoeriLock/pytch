# This is a simple demonstration on how to stream
# audio from microphone and then extract the pitch
# and volume directly with help of PyAudio and Aubio
# Python libraries. The PyAudio is used to interface
# the computer microphone. While the Aubio is used as
# a pitch detection object. There is also NumPy
# as well to convert format between PyAudio into
# the Aubio.
import aubio
import numpy as num
import pyaudio
import sys
import time
from tuneList import TuneList
from ikea import Ikea

# Some constants for setting the PyAudio and the
# Aubio.
BUFFER_SIZE = 2048
CHANNELS = 1
FORMAT = pyaudio.paFloat32
METHOD = "default"
SAMPLE_RATE = 44100
HOP_SIZE = BUFFER_SIZE//2
PERIOD_SIZE_IN_FRAME = HOP_SIZE
DEBUG = True

class PitchListener:

    mic = ""
    ikea = ""
    def __init__(self):
        self.ikea = Ikea("192.168.178.101", "ro8fRf1TbgJpFwdt")
        self.listen()

    #I cant wisthle pitch perfect, so we do some rouding
    def groupPitch(self, pitch):
        return pitch - (pitch % 100)

    def listen(self):
        tuneList = TuneList()
        pA = pyaudio.PyAudio()

        # Open the microphone stream.
        self.mic = pA.open(format=FORMAT, channels=CHANNELS,
            rate= SAMPLE_RATE, input=True,
            frames_per_buffer= PERIOD_SIZE_IN_FRAME)
        pDetection = aubio.pitch(METHOD, BUFFER_SIZE,
            HOP_SIZE, SAMPLE_RATE)
        pDetection.set_unit("Hz")
        pDetection.set_silence(-40)

        pitchList = []
        oldPitch = 0
        # Infinite loop!
        while True:

            # Always listening to the microphone.
            data = self.mic.read(PERIOD_SIZE_IN_FRAME, exception_on_overflow = False)
            # Convert into number that Aubio understand.
            samples = num.fromstring(data,
                dtype=aubio.float_type)
            # Finally get the pitch.
            pitch = pDetection(samples)[0]
            pitch = self.groupPitch(pitch)
            # Compute the energy (volume)
            # of the current frame.
            volume = num.sum(samples**2)/len(samples)
            # Format the volume output so it only
            # displays at most six numbers behind 0.
            volume = "{:6f}".format(volume)

            # Finally print the pitch and the volume.
            if(float(volume) > 0.001000 and oldPitch != pitch):
                oldPitch = pitch
                print(str(pitch) + " " + str(volume))
                pitchList.append(pitch)
                if(len(pitchList) >= 5):
                    pitchList.pop(0)
                if(tuneList.isTune(pitchList)):
                    if(DEBUG):
                        print("Tune correct!")
                    
                    pitchList = []
                    if(self.ikea.getStatus(3)):
                        if(DEBUG):
                            print("Turning on!")
                        self.ikea.turnOnLight(2, 0)
                        self.ikea.turnOnLight(3, 0)
                        self.ikea.turnOnLight(4, 0)
                        self.ikea.turnOnLight(6, 0)
                    else:
                        if(DEBUG):
                            print("Turning off!")
                        self.ikea.turnOnLight(2, 50)
                        self.ikea.turnOnLight(3, 50)
                        self.ikea.turnOnLight(4, 50)
                        self.ikea.turnOnLight(6, 50)
x = PitchListener();
