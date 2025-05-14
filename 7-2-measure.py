import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import time

GPIO.setwarnings(False)

dac = [26, 19, 13, 6, 5, 11, 9, 10]
leds = [21, 20, 16, 12, 7, 8, 25, 24]
comp = 4
troyka = 17
bits = len(dac)
lvls = 2 ** bits
maxV = 3.3

GPIO.setmode(GPIO.BCM)

GPIO.setup(troyka, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(dac, GPIO.OUT)
GPIO.setup(comp, GPIO.IN)

# function for translate num in 10 system to bin system with array form
def dec_to_bin(val):
    return [int(i) for i in bin(val)[2:].zfill(8)]

# a function that measures the voltage at the output of the troika module
def adc():
    lvl = 0
    for i in range(bits - 1, -1, -1):
        lvl += 2**i
        GPIO.output(dac, dec_to_bin(lvl))
        time.sleep(0.01)
        comp_val = GPIO.input(comp)
        if (comp_val == 0):
            lvl -= 2**i
    return lvl

# output bin to leds
def num2_dac_leds(val):
    signal = dec_to_bin(val)
    GPIO.output(dac, signal)
    return signal

data_v = []
data_t = []

try:
    GPIO.output(troyka, GPIO.HIGH)
    start_time = time.time()
    val = 0
    while val < 230:
        val = adc()
        print("Зарядка. volts: {:.4}".format(val / lvls * maxV))
        num2_dac_leds(val)
        data_v.append(val)
        data_t.append(time.time() - start_time)
    
    print("kek")

    GPIO.output(troyka, GPIO.LOW)

    while val > 20:
        val = adc()
        print("Разрядка. volts: {:.4}".format(val / lvls * maxV))
        num2_dac_leds(val)
        data_v.append(val)
        data_t.append(time.time() - start_time)

    end_time = time.time()

    with open("./settings.txt", "w") as file:
        file.write(str((end_time - start_time) / len(data_v)))
        file.write("\n")
        file.write(str(maxV / 256))

    print(end_time - start_time, " s")
    print(len(data_v) / (end_time - start_time))
    print(maxV / 256)

finally:
    GPIO.output(dac, GPIO.LOW)
    GPIO.output(troyka, GPIO.LOW)
    GPIO.cleanup()

data_t_str = [str(elem) for elem in data_t]
data_v_str = [str(elem) for elem in data_v]

with open("./data.txt", "w") as file:
    file.write("\n".join(data_v_str))

plt.plot(data_t, data_v)
plt.show()
