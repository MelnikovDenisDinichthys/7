import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import datetime as dt
import time as tm

# ------------Настройка портов GPIO--------------------------------

# dac  = [26, 19, 13,  6,  5, 11,  9, 10]
# leds = [21, 20, 16, 12,  7,  8, 25, 24]
# comp = 4
# troyka = 17

dac  = [8, 11, 7,  1,  0,  5, 12, 6]
leds = [2,  3, 4, 17, 27, 22, 10, 9]
comp = 14
troyka = 13

period = 0.2

izm = []

picture_file_name = './7/Picture.png'
data_file_name = './7/data.txt'
settings_file_name = './7/settings.txt'

GPIO.setmode(GPIO.BCM)
GPIO.setup(dac,  GPIO.OUT)
GPIO.setup(leds, GPIO.OUT)
GPIO.setup(comp, GPIO.IN)
GPIO.setup(troyka, GPIO.OUT)

# ------------Функции--------------------------------------------

def dec2bin (number):
    return [int (digit) for digit in bin (number)[2:].zfill (8)]

def adc ():
    digits = [0, 0, 0, 0, 0, 0, 0, 0]
    ret_val = 0
    for i in range (7, 0, -1):
        digits [7-i] = 1
        ret_val = ret_val + 2**i
        GPIO.output(dac, digits)
        tm.sleep (0.005)
        result = GPIO.input(comp)
        if result == 1: 
            digits [7-i] = 0
            ret_val = ret_val - 2**i
    return ret_val

def color_leds (number):
    GPIO.output(leds, dec2bin(number))
    return

def current_time():
    return tm.time()

# ------------Тело программы-------------------------------------

res = 0

try:
# ------------Начало----------------------------------------------

    GPIO.output(troyka, GPIO.HIGH)
    start = current_time()

# ------------Зарядка---------------------------------------------

    while res < 255*0.6:
        res = adc()
        color_leds(res)
        res_V = res*3.3/255
        izm.append(res)
        print('Зарядка: В момент времени ', current_time() - start, ' значение напряжения равно ', res_V)
        tm.sleep(period)

# ------------Сброс напряжения-------------------------------------

    GPIO.output(troyka, GPIO.LOW)

# ------------Разрядка---------------------------------------------

    while res > 255*0.02:
        res = adc()
        color_leds(res)
        res_V = res*3.3/255
        izm.append(res)
        print('Разрядка: В момент времени ', current_time() - start, ' значение напряжения равно ', res_V)
        tm.sleep(period)

# ------------Конец эксперимента----------------------------------

    end = current_time()

# ------------Построение графика----------------------------------

    plt.plot(izm)
    plt.title('Значение напряжения на тройка-модуле\nв зависимости от номера измерения')
    plt.xlabel('Номер измерения')
    plt.ylabel('Значение напряжения')
    plt.savefig(picture_file_name, dpi = 300)

# ------------Запись в файлы результатов измерений----------------

    with open(data_file_name, 'w') as data_file:
            data_file.write('\n'.join([str(item) for item in izm]))

    with open(settings_file_name, 'w') as settings_file:
            settings_file.write('Частота дискретизации равна ')
            settings_file.write(str(1/period))
            settings_file.write('\nШаг квантования равен ')
            settings_file.write(str(3.3/256))

# ------------Вывод в консоль результатов-------------------------

    print('Общая продолжительность эксперимента равна ', end - start)
    print('Период одного измерения равен ', period)
    print('Частота дискретизации равна ', 1/period, '\nШаг квантования равен ', 3.3/256)

# ------------Завершение программы и сброс параметров платы-------

finally:
    GPIO.output(dac,  0)
    GPIO.output(leds, 0)
    GPIO.output(troyka, 0)
    GPIO.cleanup()
    plt.clf()
