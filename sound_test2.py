import math
import numpy
import pyaudio
import audioop
import random
import struct
import pylab as pl

FREQ = 1000
DBCONST_TONE = 0 #26.5 for 50 dB
DBCONST_NOISE = 2.6 #2.6 for 30db noise; 26.5 for 50 dB; 85 for 60 dB
NUM_TURNAROUNDS = 9
START_FREQS = [1040,960]
ORDER_SN = 1 #1 for (S,N), 0 for (N,S)

        
def sine(frequency, length, rate):
     length = int(length * rate)
     factor = float(frequency) * (math.pi * 2) / rate
     sine = numpy.sin(numpy.arange(length) * factor)
     return sine

def noise(frequency, length, rate):
    length = int(length * rate)
    factor = float(frequency) * (math.pi * 2) / rate
    noise = numpy.random.rand(length)
    return noise


def play_tone(stream, frequency=440, length=1, rate=44100):
    #length in half-seconds
    chunks = []
    tone = DBCONST_TONE * sine(frequency, length, rate)
    silence = numpy.zeros(30000)
    noiseSound = DBCONST_TONE * sine(FREQ, length, rate) + \
        DBCONST_NOISE*noise(FREQ, length, rate)
    
    if ORDER_SN:
        chunks.append(tone)
        chunks.append(silence)
        chunks.append(noiseSound)
    else:
        chunks.append(noiseSound)
        chunks.append(silence)
        chunks.append(tone)
    chunk = numpy.concatenate(chunks) * 0.25
    stream.write(chunk.astype(numpy.float32).tostring())
    return chunk
    
def get_rms(block):
    s = 0
    for i in block:
        s += i**2
    return math.sqrt(float(1./len(block)) * s)
        
def test(current):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                     channels=2, rate=44100, output=1)

    play_tone(stream, current)

    stream.close()
    p.terminate()
    
    if (current >= FREQ):
        if ORDER_SN:
            return 1
        else:
            return 2
    else:
        if ORDER_SN:
            return 2
        else:
            return 1
            
def dbPlot():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                     channels=2, rate=44100, output=1)

    chunk = play_tone(stream, FREQ)
    
    t = numpy.arange(len(chunk))*1.0/44100
    a = 20*numpy.log10(numpy.abs(numpy.fft.rfft(chunk)))
    f = numpy.linspace(0, 44100/2.0, len(a))
    pl.plot(f, a)
    print numpy.sqrt(numpy.mean(numpy.square(a)))
    pl.xlabel("Frequency(Hz)")
    pl.ylabel("Power(dB)")
    pl.show()

    stream.close()
    p.terminate()
    

if __name__ == '__main__':
    
    #dbPlot()

    for j in START_FREQS:
        
        for i in [1,0]:
            
            ORDER_SN = i

            current = j #1040/960
            step = 20.0 + random.uniform(-5, 5) #initial
            min_step = 1.0
            turnarounds = []
            past_answer = True
            num_steps = 0
           
            while (len(turnarounds) < NUM_TURNAROUNDS):
                num_steps += 1
                results = test(current)
                if step < min_step:
                    step = min_step
                answer = input('1 if first tone was higher, else 2: ')  
                if (int(answer) != results):
                    print "wrong"
                    if (past_answer == True):
                        turnarounds.append(current)
                        past_answer = False
                    if (current<FREQ):
                        current-=step
                    else:
                        current+= step
                    step += 3.0
                else:
                    print "correct"
                    if past_answer == False:
                        turnarounds.append(current)
                        past_answer = True
                    if (current<FREQ):
                        current+=step
                    else:
                        current-= step
                    step /= num_steps
                        
            print str(j)
            print "turnarounds: ", str(turnarounds)
            print "Ave: ", str(reduce(lambda x, y: x + y, turnarounds) \
                / len(turnarounds))
            print "# Pres: ", str(num_steps)