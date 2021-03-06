#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import lcddriver
import RPi.GPIO as GPIO


class Lcd:
    """
    Classe permettent l'affichage de messages sur l'ecran lcd
    Ceux-ci sont constitues de chaines de caracteres, centres sur deux lignes
    """

    def __init__(self):
        self.power = True
        self.text = ["", ""]
        self.previous_text = ["", ""]
        self.setGPIO()
        self.display = lcddriver.lcd()
        os.chdir("/home/pi/Desktop/Sudoku-Plotter/script/lcd")

    def setGPIO(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(8, GPIO.OUT)
        GPIO.setup(10, GPIO.OUT)
        GPIO.output(8, GPIO.HIGH)
        GPIO.output(10, GPIO.HIGH)

    def start(self):
        text = open("text.txt", "w")
        text.close()
        previous_text = open("previous_text.txt", "w")
        previous_text.close()
        self.display.lcd_clear()
        while self.power:
            self.write()
            time.sleep(0.1)

    def write(self):
        try:
            text = open("text.txt", 'r')
            previous_text = open("previous_text.txt", 'r')
            for i in range(2):
                self.text[i] = text.readline().replace('\n', '')
                self.previous_text[i] = previous_text.readline().replace('\n', '')
                if self.text[i] != self.previous_text[i]:
                    self.writeLine(self.text[i].center(16), i)
            text.close()
            previous_text.close()
        except IOError:
            pass
        if self.text != self.previous_text:
            previous_text = open("previous_text.txt", "w")
            previous_text.write(self.text[0] + '\n' + self.text[1])
            previous_text.close()

    def writeLine(self, text, i):
        self.display.lcd_display_string(text, i + 1)

    def close(self):
        self.power = False
        self.display.lcd_clear()


Lcd().start()
