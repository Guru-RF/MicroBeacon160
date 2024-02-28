# LoraCWBeacon Copyright 2023 Joeri Van Dooren (ON3URE)

import asyncio
import time

import board
from digitalio import DigitalInOut, Direction

import config

# User config
WPM = config.WPM
BEACON = config.BEACON
BEACONDELAY = config.BEACONDELAY

# CW
osc = DigitalInOut(board.GP15)
osc.direction = Direction.OUTPUT
osc.value = False

# setup encode and decode
encodings = {}


def encode(char):
    global encodings
    if char in encodings:
        return encodings[char]
    elif char.lower() in encodings:
        return encodings[char.lower()]
    else:
        return ""


decodings = {}


def decode(char):
    global decodings
    if char in decodings:
        return decodings[char]
    else:
        # return '('+char+'?)'
        return "¿"


def MAP(pattern, letter):
    decodings[pattern] = letter
    encodings[letter] = pattern


MAP(".-", "a")
MAP("-...", "b")
MAP("-.-.", "c")
MAP("-..", "d")
MAP(".", "e")
MAP("..-.", "f")
MAP("--.", "g")
MAP("....", "h")
MAP("..", "i")
MAP(".---", "j")
MAP("-.-", "k")
MAP(".-..", "l")
MAP("--", "m")
MAP("-.", "n")
MAP("---", "o")
MAP(".--.", "p")
MAP("--.-", "q")
MAP(".-.", "r")
MAP("...", "s")
MAP("-", "t")
MAP("..-", "u")
MAP("...-", "v")
MAP(".--", "w")
MAP("-..-", "x")
MAP("-.--", "y")
MAP("--..", "z")

MAP(".----", "1")
MAP("..---", "2")
MAP("...--", "3")
MAP("....-", "4")
MAP(".....", "5")
MAP("-....", "6")
MAP("--...", "7")
MAP("---..", "8")
MAP("----.", "9")
MAP("-----", "0")

MAP(".-.-.-", ".")  # period
MAP("--..--", ",")  # comma
MAP("..--..", "?")  # question mark
MAP("-...-", "=")  # equals, also /BT separator
MAP("-....-", "-")  # hyphen
MAP("-..-.", "/")  # forward slash
MAP(".--.-.", "@")  # at sign

MAP("-.--.", "(")  # /KN over to named station
MAP(".-.-.", "+")  # /AR stop (end of message)
MAP(".-...", "&")  # /AS wait
MAP("...-.-", "|")  # /SK end of contact
MAP("...-.", "*")  # /SN understood
MAP(".......", "#")  # error


# key down and up
def cw(on):
    if on:
        osc.value = True
    else:
        osc.value = False


# timing
def dit_time():
    global WPM
    PARIS = 50
    return 60.0 / WPM / PARIS


# transmit pattern
def keydown():
    cw(True)


# transmit pattern
def play(pattern):
    for sound in pattern:
        if sound == ".":
            cw(True)
            time.sleep(dit_time())
            cw(False)
            time.sleep(dit_time())
        elif sound == "-":
            cw(True)
            time.sleep(3 * dit_time())
            cw(False)
            time.sleep(dit_time())
        elif sound == " ":
            time.sleep(4 * dit_time())
    time.sleep(2 * dit_time())


# play beacon and pause
def beacon():
    global cwBeacon
    letter = cwBeacon[:1]
    cwBeacon = cwBeacon[1:]
    print(letter, end="")
    play(encode(letter))


async def beaconLoop():
    global cwBeacon
    global BEACON
    cwBeacon = BEACON
    while True:
        beacon()
        await asyncio.sleep(0)
        if len(cwBeacon) == 0:
            await asyncio.sleep(0.5)
            cw(True)
            await asyncio.sleep(BEACONDELAY)
            cw(False)
            await asyncio.sleep(0.5)
            cwBeacon = BEACON


async def main():
    loop = asyncio.get_event_loop()
    cwL = asyncio.create_task(beaconLoop())
    await asyncio.gather(cwL)


asyncio.run(main())
