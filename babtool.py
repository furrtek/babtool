# Pack and depack Build-a-Bear sound module data
# https://github.com/furrtek/babtool/
# 2019 furrtek

import sys, struct, os, wave
from os import listdir
from os.path import isfile, join

def printusage():
    print("Usage: babtool r|w dump.bin|directory")
    exit()

def do_read():
    dump = open(sys.argv[2], 'rb')
    ba = bytearray(dump.read())
    
    i = 0
    script_ptrs = []
    while True:
        script_idx = ba[0x80 + i]
        if (script_idx == 0xFF):
            break
        script_idx *= 16
        script_ptrs.append(script_idx)
        print("Script %u @ 0x%05X" % (i, script_idx))
        i += 1
    
    i = 0
    sound_ptrs = []
    while True:
        sound_ptr = ba[0x100 + i*3]
        if (sound_ptr == 0xFF):
            break
        sound_ptr = (sound_ptr & 7) << 16
        sound_ptr += struct.unpack("<H", ba[0x101 + i*3:0x103 + i*3])[0]
        sound_ptrs.append(sound_ptr)
        print("Sound %u @ 0x%05X" % (i, sound_ptr))
        i += 1
    
    for i, sound_ptr in enumerate(sound_ptrs):
        fs = wave.open(str(i) + ".wav", 'wb')
        fs.setnchannels(1)
        fs.setsampwidth(1)
        fs.setframerate(11025)
        c = 1
        # Convert audio data in 256-byte blocks
        while True:
            w = bytearray()
            b = ba[sound_ptr:sound_ptr + 256]
            for s in b:
                w.append((s >> 4) * 17)
                w.append((s & 15) * 17)
            fs.writeframesraw(w)
            if (b[255] == 0xFF):
                break
            sound_ptr += 256
            c += 1
        print("Dumped sound %u to %u.wav, duration: %.2fs" % (i, i, (c << 8) / 11025.0))
        fs.close()
    
    dump.close()

def do_write():
    sound_data = []
    for f in listdir(sys.argv[2]):
        fj = join(sys.argv[2], f)
        if isfile(fj):
            print("Converting %s" % fj)
            fw = wave.open(fj, 'rb')
            if (fw.getnchannels() != 1):
                print("%s is not mono, skipping ", fj)
            if (fw.getsampwidth() != 1):
                print("%s is not 8-bit, skipping ", fj)
            if (fw.getframerate() != 11025):
                print("%s samplerate is not 11025Hz, skipping ", fj)
            ba = fw.readframes(fw.getnframes())
            fw.close()

            # Convert 8-bit to 4-bit (ugly)
            i = 0
            buff = bytearray()
            for b in ba:
                b = struct.unpack("B", b)[0]
                if ((i & 1) == 0):
                    s = b & 0xF0
                else:
                    buff.append(s + (b >> 4))
                i += 1

            # Pad to 512-byte boundary
            diff = 512 - ((i >> 1) & 511)
            for b in range(0, diff):
                buff.append(0xFF)
            sound_data.append(buff)

    # Fill buffer with 0xFF's
    outdata = bytearray(512 * 1024)
    for i in range(0, 512 * 1024):
        outdata[i] = 0xFF
    
    # Index to startup script at 0x120
    outdata[0:6] = [0x01, 0x12, 0xFF, 0x12, 0xFF, 0x12]

    # List of indexes to individual scripts starting at 0x140
    for i in range(0, len(sound_data)):
        outdata[0x80 + i] = 0x14 + i

    # Indexes to cold boot script ?
    outdata[0xFE] = 0x1F
    outdata[0xFF] = 0x1F

    # Sound data pointers
    acc = 0x300
    for i in range(0, len(sound_data)):
        outdata[0x100 + i*3] = 0xB0 + (acc >> 16)
        outdata[0x101 + i*3] = acc & 255
        outdata[0x102 + i*3] = (acc >> 8) & 255
        acc += len(sound_data[i])

    # Startup script ?
    outdata[0x120:0x126] = [0x00, 0x00, 0x20, 0x07, 0x09, 0x00]

    for i in range(0, len(sound_data)):
        outdata[0x126 + i*2] = len(sound_data) - 1
        outdata[0x127 + i*2] = 0x80 + i

    # Individual scripts
    for i in range(0, len(sound_data)):
        j = i * 16
        if (i < len(sound_data) - 1):
            outdata[0x140 + j:0x148 + j] = [0x04, i, 0x10, i + 1, 0x02, 0x01, 0x00, 0x15]
        else:
            outdata[0x140 + j:0x148 + j] = [0x04, i, 0x10, 0x00, 0x02, 0x01, 0x00, 0x15]

    # Cold boot script ?
    outdata[0x1F0:0x1F4] = [0x10, 0x00, 0x00, 0x15]

    # Sound data
    addr = 0x300
    for s in sound_data:
        length = len(s)
        outdata[addr:addr+length] = s
        addr += length

    fb = open("out.bin", 'wb')
    fb.write(outdata)
    fb.close()
    
    print("Generated out.bin")


if (len(sys.argv) != 3):
    printusage()

if (sys.argv[1] == 'r'):
    do_read()
elif (sys.argv[1] == 'w'):
    do_write()
else:
    printusage()
