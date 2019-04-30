# babtool
This tool handles data for the blue Build-a-Bear sound modules. It can extract sounds from dumps or generate data from sound files.

These modules and their programming system are made by Voice Express Corp. and covered by **US patent 8675908**.

Their "proprietary NFC" programming method is quite nifty: it's done by inductive coupling through the module's speaker.
The MCU uses it as an antenna to pick up data and writes it to a 512KiB serial flash chip.
According to the patent's schematics, the module may also be able to answer back to the programmer (see "RCRV" lines).

Voice Express mentions that some of their other modules are able to drive LEDs or motors in sync with voice of music, so they're
probably smart enough to interpret some form of minimal scripts.

# Dumping
Required:
* A 3.3V Arduino, or a 5V one with level adapters
* Jumper wires
* Flat head screwdriver
* Soldering equipment (hot air gun preferred)

Open the module with a flat head screwdriver. Remove the 25X40 flash chip from the board. Program a **3.3V** Arduino with `dump.ino`.
Hook it up to the chip like this: 

| 25X40 | Arduino |
| ----- | ------- |
|   1   |    9    |
|   2   |    12   |
|   3   |  3.3V   |
|   4   |   GND   |
|   5   |    11   |
|   6   |    13   |
|   7   |  3.3V   |
|   8   |   3.3V  |

Open a serial terminal and connect to your programmed Arduino at 115200 8N1, enable logging to file, press a key and wait.
Once your log file is exactly 512KiB in size, you're done.

# Data format
This information isn't verified yet !

* 0x00000: Unknown, version ?
* 0x00080: Script index for each sound (bytes), *16 for effective address
* 0x00100: Sound data pointer list. Groups of 3 bytes:
  * 1st: 64kiB bank number OR 0xB0
  * 2st: Byte address LSB
  * 3st: Byte address MSB
* 0x00120: ?
* 0x00140: Script data for each sound ? 16-byte blocks
  * `0x02 NN`: ?
  * `0x04 NN`: Start playing sound from NN ?
  * `0x10 NN`: Set next script NN ?
  * `0x00 0x15`: Go to sleep ?

Samples are raw unsigned 4-bit played back at around 11025Hz.
Sounds seem to be padded to 512-byte blocks.
It is unknown if this is a format limitation or something decided by the programming booth software.

# Example: Toothless
See `bab_toothless_dump.bin` for the full flash memory dump.

* 0x00080: Six script indexes:
  * `0x14`: 0x00140
  * `0x15`: 0x00150
  * `0x16`: 0x00160
  * `0x17`: 0x00170
  * `0x18`: 0x00180
  * `0x19`: 0x00190
* 0x00100: Six sound data pointers:
  * `0xB0 0x00 0x03`: Sound #0 at 0x00300
  * `0xB0 0x00 0x36`: Sound #1 at 0x03600
  * `0xB0 0x00 0x6F`: Sound #2 at 0x06F00
  * `0xB0 0x00 0xAC`: Sound #3 at 0x0AC00
  * `0xB0 0x00 0xD6`: Sound #4 at 0x0D600
  * `0xB0 0x00 0xF1`: Sound #5 at 0x0F100
* 0x00120: ?
* 0x00140: Script #0
  * `0x04 0x00`: Play sound #0
  * `0x10 0x01`: Next script will be #1
  * `0x02 0x01`: ???
  * `0x00 0x15`: Go to sleep
* 0x00145: Script #1
  * `0x04 0x01`: Play sound #1
  * `0x10 0x02`: Next script will be #2
  * `0x02 0x01`: ???
  * `0x00 0x15`: Go to sleep
* ...
* 0x00300: Sound #0 data
* ...
