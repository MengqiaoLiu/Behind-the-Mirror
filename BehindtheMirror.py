#encoding=utf-8
import os
import sys
import webbrowser
import time
import _thread
from evdev import InputDevice
from select import select
import RPi.GPIO as GPIO
import board
import neopixel
import numpy as np
import cv2

pixel1_pin = board.D21
num_pixels = 36
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel1_pin, num_pixels, brightness=0.05, auto_write=False,pixel_order=ORDER)

width, height = 2560, 1024
image = np.ones((height, width, 3), dtype=np.float32)
image[:1024, :2560] = 0  # black at top-left corner

A1 = 0 #A的状态，0=没ready，1=SYN ready, 2=B的 SYN 和 ACK ready，
B1 = 0 #B的状态，0=没ready，1=SYN ready
C = 0 #A的code值
D = 0 #B的code值
m = 0 #判断B的code状态，0=没有，1=已验证A的code，2=已设定自己的code
n = 0 #判断A的code状态，0=没有，1=已验证A的code，2=已设定自己的code

w = 17 #A的1 17
a = 30 #A的2 30
s = 31 #A的3 31

d = 32 #B的1 32
f = 33 #B的2 33
g = 34 #B的3 34

up = 103 #A的SYN  103
down = 108 #A的ACK 108
left = 105 #B的SYN  105
right = 106 #B的ACK 106

inits = 1 #表示是否为初始状态
end = 0
clicktime = 0
nowtime = 0
overtimeflag = 0
stage = 0

light1 = 17
light6 = 27
light11 = 22
light16 = 5
light2 = 6
light4 = 24
light8 = 13
light12 = 19
light14 = 25
light18 = 26
lightgroup1 = 18
lightgroup2 = 23

onlight = light2
flashlight = light12

GPIO.setmode(GPIO.BCM) #!!!!!!!!!!!!!!!!!!!!!!!
GPIO.setup(light1,GPIO.OUT)
GPIO.setup(light11,GPIO.OUT)
GPIO.setup(light6,GPIO.OUT)
GPIO.setup(light16,GPIO.OUT)
GPIO.setup(light2,GPIO.OUT)
GPIO.setup(light4,GPIO.OUT)
GPIO.setup(light8,GPIO.OUT)
GPIO.setup(light12,GPIO.OUT)
GPIO.setup(light14,GPIO.OUT)
GPIO.setup(light18,GPIO.OUT)
GPIO.setup(lightgroup1,GPIO.OUT)
GPIO.setup(lightgroup2,GPIO.OUT)



def linkstart():
    global end
    end = 1
    pixels.fill((255, 255, 255))
    pixels.show()
    cv2.destroyAllWindows()
    #open cam
    #os.system("cam")
    
    time.sleep(4)
    #print ("rua")
    
    
def init_light():
    global stage
    global inits
    inits = 1
    #GPIO.output(lightBD, GPIO.HIGH)
    print ("light BD on")
    while(stage == 0):
        GPIO.output(light1, GPIO.HIGH)
        GPIO.output(light11, GPIO.HIGH)
        print ("light 1 on")
        print ("light 11 on")
        print (stage)
        time.sleep(0.5)
        GPIO.output(light1, GPIO.LOW)
        GPIO.output(light11, GPIO.LOW)
        print ("light 1 off")
        print ("light 11 off")
        time.sleep(0.5)

def first_stage():
    global stage
    global inits
    inits = 0
    while(stage == 1):
        GPIO.output(light2, GPIO.HIGH)
        GPIO.output(light4, GPIO.HIGH)
        GPIO.output(light8, GPIO.HIGH)
        GPIO.output(lightgroup1, GPIO.HIGH)
        print ("light 2-10 on")
        time.sleep(0.5)
        GPIO.output(light2, GPIO.LOW)
        GPIO.output(light4, GPIO.LOW)
        GPIO.output(light8, GPIO.LOW)
        GPIO.output(lightgroup1, GPIO.LOW)
        print ("light 2-10 off")
        time.sleep(0.5)

def second_stage():
    global stage
    if stage == 2:
        GPIO.output(onlight, GPIO.HIGH)
        print ("light ",str(onlight)," on")
        while (stage == 2):
            GPIO.output(flashlight, GPIO.HIGH)
            print ("light ",str(flashlight)," on")
            time.sleep(0.5)
            GPIO.output(flashlight, GPIO.LOW)
            print ("light ",str(flashlight)," off")
            time.sleep(0.5)

def third_stage():
    global stage
    if stage == 3:
        GPIO.output(onlight, GPIO.LOW)
        print ("light ",str(onlight)," off")
        GPIO.output(flashlight, GPIO.HIGH)
        print ("light ",str(flashlight)," on")
        while (stage == 3):
            GPIO.output(light11, GPIO.HIGH)
            print ("light 11 on")
            time.sleep(0.5)
            GPIO.output(light11, GPIO.LOW)
            print ("light 11 off")
            time.sleep(0.5)

def fourth_stage():
    global stage
    if stage == 4:
        GPIO.output(light11, GPIO.LOW)
        print ("light 11 off")
        GPIO.output(light12, GPIO.LOW)
        print ("light 12 off")
        while (stage == 4):
            GPIO.output(light12, GPIO.HIGH)
            GPIO.output(light14, GPIO.HIGH)
            GPIO.output(light18, GPIO.HIGH)
            GPIO.output(lightgroup2, GPIO.HIGH)
            print ("light 12-20 on")
            time.sleep(0.5)
            GPIO.output(light12, GPIO.LOW)
            GPIO.output(light14, GPIO.LOW)
            GPIO.output(light18, GPIO.LOW)
            GPIO.output(lightgroup2, GPIO.LOW)
            print ("light 12-20 off")
            time.sleep(0.5)

def fifth_stage():
    global stage
    if stage == 5:
        GPIO.output(onlight, GPIO.HIGH)
        print ("light ",str(onlight)," on")
        while (stage == 5):
            GPIO.output(light16, GPIO.HIGH)
            print ("light 16 on")
            time.sleep(0.5)
            GPIO.output(light16, GPIO.LOW)
            print ("light 16 off")
            time.sleep(0.5)

def sixth_stage():
    global stage
    if stage == 6:
        GPIO.output(light16, GPIO.LOW)
        GPIO.output(onlight, GPIO.LOW)
        print ("light 16 off")
        print ("light ",str(onlight)," off")
        while (stage == 6):
            GPIO.output(flashlight, GPIO.HIGH)
            print ("light ",str(flashlight)," on")
            time.sleep(0.5)
            GPIO.output(flashlight, GPIO.LOW)
            print ("light ",str(flashlight)," off")
            time.sleep(0.5)
def seventh_stage():
    global stage
    if stage == 7:
        GPIO.output(flashlight, GPIO.HIGH)
        print ("light ",str(flashlight)," on")
        while (stage == 7):
            GPIO.output(light6, GPIO.HIGH)
            print ("light 6 on")
            time.sleep(0.5)
            GPIO.output(light6, GPIO.LOW)
            print ("light 6 off")
            time.sleep(0.5)

def eighth_stage():
    global stage
    if stage == 8:
        GPIO.output(light6, GPIO.LOW)
        GPIO.output(onlight, GPIO.LOW)
        print ("light 6 off")
        print ("light ",str(onlight)," off")
        linkstart()

def warning_stage(light):
    global stage
    global clicktime
    global nowtime
    global inits
    global end
    global pixels
    while (end != 1):
        nowtime = time.time()
        #print ("nowtime" = nowwddwtime)
        #print ("clicktime" = clicktime)
        
        if ((nowtime - clicktime) >= 30) and (inits != 1) :
            stage = -1
            break
        
        if ((nowtime - clicktime) >= 20) and (inits != 1) :
            pixels.fill((0, 0, 0))
            pixels.show()
            pixels.fill((255, 0, 0))
            pixels.show()
            print ("light AC on")
            time.sleep(0.5)
    
            pixels.fill((0, 0, 0))
            pixels.show()
            print ("light AC off")
            time.sleep(0.5)
        else:
            pixels.fill((255, 255, 255))
            pixels.show()
    print ("endthread")

def error_stage():
    global stage
    global clicktime
    global pixels
    if stage == -1:
        pixels.fill((255, 0, 0))
        pixels.show()
        print ("light AC on")
        time.sleep(8)
        pixels.fill((0, 0, 0))
        pixels.show()
        print ("light AC off")

def press_up():
    #detectInputKey()
    global A1
    global B1
    global C
    global D
    global m
    global n
    #global stage
    #global clicktime
    #clicktime = time.time()
    A1 = 1
    if A1 == 1:
        B1 = 0
        print ("A is ready")
        stage = 1
        print (stage)
    elif A1 == 3:
        print ("END!")
        stage = -1
        #init()
        #return 0

def press_w():
    #detectInputKey()
    global A1
    global B1
    global C
    global D
    global m
    global n
    global onlight
    global flashlight
    #global stage
    #global clicktime
    #clicktime = time.time()
    if A1 == 0:
        print ("Not ready yet!")
        stage = -1
    elif A1 == 1:
        C = 1
        print ("A send!")
        onlight = light2
        flashlight = light12
        stage += 1
    elif A1 == 2:
        if n == 0:
            if D == 1:
                n=1
                print ("OK!Press down to connect!")
                stage += 1
            else:
                print ("wrong")
                stage = -1
        else:
            print ("OK!Press down to connect!")
    elif A1 == 3:
        print("END!")
        stage = -1

def press_a():
    #detectInputKey()
    global A1
    global B1
    global C
    global D
    global m
    global n
    global onlight
    global flashlight
    #global stage
    #global clicktime
    #clicktime = time.time()
    if A1 == 0:
        print ("Not ready yet!")
        stage = -1
    elif A1 == 1:
        C = 2
        print ("A send!")
        onlight = light4
        flashlight = light14
        stage += 1
    elif A1 == 2:
        if n == 0:
            if D == 2:
                n=1
                print ("OK!Press down to connect!")
                stage += 1
            else:
                print ("wrong")
                stage = -1
        else:
            print ("OK!Press down to connect!")
    elif A1 == 3:
        print("END!")
        stage = -1

def press_s():
    #detectInputKey()
    global A1
    global B1
    global C
    global D
    global m
    global n
    global onlight
    global flashlight
    #global stage
    #global clicktime
    #clicktime = time.time()
    if A1 == 0:
        print ("Not ready yet!")
        stage = -1
    elif A1 == 1:
        C = 3
        print ("A send!")
        onlight = light8
        flashlight = light18
        stage += 1
    elif A1 == 2:
        if n == 0:
            if D == 3:
                n=1
                print ("OK!Press down to connect!")
                stage += 1
            else:
                print ("wrong")
                stage = -1
        else:
            print ("OK!Press down to connect!")
    elif A1 == 3:
        print("END!")
        stage = -1


def press_down():
    #detectInputKey()
    global A1
    global B1
    global C
    global D
    global m
    global n
    #global stage
    #global clicktime
    #clicktime = time.time()
    if A1 == 2 and B1 == 2:
        if n == 1:
            A1 = 3
            print ("Successfully connected! Click any to end")
            stage += 1
            #open cam
            #os.system("cam")
            #webbrowser.open(user1cam)
            #webbrowser.open(user2cam)
        else:
            print ("Not ready yet!")
            stage = -1
    else:
         print("Not finished yet!")
         stage = -1
         

def press_left():
    #detectInputKey()
    global A1
    global B1
    global C
    global D
    global m
    global n
    #global stage
    #global clicktime
    #clicktime = time.time()
    #keyboard.wait(left)
    if A1 == 1 and C!= 0 and m == 1:
        print ('Both Ready~')
        stage += 1
        B1 = 1
        #stage = 4
    else:
        if A1 == 3:
            print("END!")
            stage = -1
        else:
            print ('A is not ready yet!')
            stage = -1


def press_d():
    #detectInputKey()
    global A1
    global B1
    global C
    global D
    global m
    global n
    global onlight
    global flashlight
    #global stage
    #global clicktime
    #clicktime = time.time()
    if A1 == 1 and C != 0:
        if m == 2:
            stage = -1
        else:
            if m == 0:
                if C == 1:
                    m = 1
                    print ('Choose left')
                    stage += 1
                    #stage = 3
                else:
                    print ('Wrong')
                    stage = -1
            else:
                if B1 == 1:
                    onlight = light12
                    flashlight = light2
                    print ('OK! Press right to send!')
                    stage += 1
                    D = 1
                    m = 2
                else:
                    print('Wrong')
                    stage = -1
    else:
        if B1 == 2 and A1 == 2:
            print ('Wait please')
        print ('Not ready yet!')
        stage = -1
    if A1 == 3:
        print("END!")
        stage = -1

   
   
def press_f():
    #detectInputKey()
    global A1
    global B1
    global C
    global D
    global m
    global n
    global onlight
    global flashlight
    #global stage
    #global clicktime
    #clicktime = time.time()
    if A1 == 1 and C != 0:
        if m == 2:
            stage = -1
        else:
            if m == 0:
                if C == 2:
                    m = 1
                    print ('Choose left')
                    stage += 1
                    #stage = 3
                else:
                    print ('Wrong')
                    stage = -1
            else:
                if B1 == 1:
                    onlight = light14
                    flashlight = light4
                    print ('OK! Press right to send!')
                    stage += 1
                    D = 2
                    m = 2
                else:
                    print('Wrong')
                    stage = -1
    else:
        if B1 == 2 and A1 == 2:
            print ('Wait please')
        print ('Not ready yet!')
        stage = -1
    if A1 == 3:
        print("END!")
        stage = -1



def press_g():
    #detectInputKey()
    global A1
    global B1
    global C
    global D
    global m
    global n
    global onlight
    global flashlight
    #global stage
    #global clicktime
    #clicktime = time.time()
    if A1 == 1 and C != 0:
        if m == 2:
            stage = -1
        else:
            if m == 0:
                if C == 3:
                    m = 1
                    print ('Choose left')
                    stage += 1
                    #stage = 3
                else:
                    print ('Wrong')
                    stage = -1
            else:
                if B1 == 1:
                    onlight = light18
                    flashlight = light8
                    print ('OK! Press right to send!')
                    stage += 1
                    D = 3
                    m = 2
                else:
                    print('Wrong')
                    stage = -1
    else:
        if B1 == 2 and A1 == 2:
            print ('Wait please')
        print ('Not ready yet!')
        stage = -1
    if A1 == 3:
        print("END!")
        stage = -1


def press_right():
    #detectInputKey()
    global A1
    global B1
    global C
    global D
    global m
    global n
    #global stage
    #global clicktime
    #clicktime = time.time()
    if D == 0:
        print ('Not choosen code yet!')
        stage = -1
    else:
        if B1 == 1 and A1 == 1:
            B1 = 2
            A1 = 2
            print ("B send!")
            stage += 1
        else:
            print ('Wrong!')
            stage = -1
    if A1 == 3:
        print("END!")
        stage = -1

def init():
    global A1
    global B1
    global C
    global D
    global m
    global n
    global clicktime
    global nowtime
    global stage
    global image
    clicktime = time.time()
    nowtime = time.time()
    A1 = 0
    B1 = 0
    C = 0
    D = 0
    m = 0
    n = 0
    GPIO.output(light1, GPIO.LOW)
    GPIO.output(light6, GPIO.LOW)
    GPIO.output(light11, GPIO.LOW)
    GPIO.output(light16, GPIO.LOW)
    GPIO.output(light2, GPIO.LOW)
    GPIO.output(light4, GPIO.LOW)
    GPIO.output(light8, GPIO.LOW)
    GPIO.output(light12, GPIO.LOW)
    GPIO.output(light14, GPIO.LOW)
    GPIO.output(light18, GPIO.LOW)
    GPIO.output(lightgroup1, GPIO.LOW)
    GPIO.output(lightgroup2, GPIO.LOW)
    
    window_name = 'projector'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.moveWindow(window_name, 0, 0)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                          cv2.WINDOW_FULLSCREEN)
    cv2.imshow(window_name, image)
    cv2.waitKey()
    
def default():
    print('No such case')

def main():
    global pixels
    time.sleep(10)
    init()
    _thread.start_new_thread (detectInputKey,(1,))
    _thread.start_new_thread (warning_stage,(1,))
    #detectInputKey()
    pixels.fill((255, 255, 255))
    pixels.show()
    init_light()
    first_stage()
    second_stage()
    thrid_stage()
    forth_stage()
    fifth_stage()
    sixth_stage()
    seventh_stage()
    eighth_stage()
    error_stage()
    pixels.deinit()
    GPIO.cleanup()

def detectInputKey(abc):
    global stage
    global clicktime
    global onlight
    global flashlight
    switch={17: press_w,
            30: press_a,
            31: press_s,
            32: press_d,
            33: press_f,
            34: press_g,
            103: press_up,
            108: press_down,
            105: press_left,
            106: press_right
            }

    deva = InputDevice('/dev/input/event0')
    while True:
        select([deva], [], [])
        for event in deva.read():
            if event.value == 1:
                switch.get(event.code, default)()
                clicktime = time.time()
                #clicktime = process_time()
                #print "code:%s value:%s" % (event.code, event.value)


    
        
    
if __name__ == '__main__':
    main()

