
import serial
import time
#serial.hooks.list_ports.comports()

# https://pyserial.readthedocs.io/en/latest/shortintro.html

ser = serial.Serial('/dev/cu.usbserial-AQ00T6NF')
print(ser.name)
ser.close()


ser = serial.Serial('/dev/cu.usbserial-AQ00T6NF', 57600, timeout=0,parity=serial.PARITY_NONE, rtscts=1)
ser.write(b'P1\r')
time.sleep(.1)
ser.flush()
#s = ser.readline()       # read up to one hundred bytes or as much is in the buffer
#print (s)
#print (s.decode("utf-8"))


'''
Receive & Transmit Modes
The Pegasus supports LSB,USB,CW and FM modes in both transmit and receive and AM mode in receive only. The selected mode must be considered in calculations for the FREQUENCY tuning factors so any change in receive or transmit modes will require a recalculation of the frequency tuning factors.
format: where:
response: example:
Receive Filter
‘M’ Rx Tx <cr>
‘M’ = the ASCII M (0x4d) character.
Rx = recieve mode (See Tx). Tx = recieve mode.
ASCII ‘0’ (0x30) for AM mode
ASCII ‘1’ (0x31) for USB mode
ASCII ‘2’ (0x32) for LSB mode
ASCII ‘3’ (0x33) for CW mode
ASCII ‘4’ (0x34) for FM mode
<cr> = ASCII carriage return (0x0D) character.
none.
M11<cr> for USB recieve, USB transmit. M23<cr> for LSB recieve, CW transmit.
'''

ser.write(b'M00\r')
time.sleep(.1)

'''
Setting the Receive Tuning Factors
Because the FILTER, MODE and BFO selections all affect the tuning factors they should be adjusted before calculating the new tuning factors. Any change in these parameters will require recalculation of the tuning factors. The command format for programming the PEGASUS’s tuning factors is shown below. The controlling program must pre-calculate and format the tuning factors.
format: where:
response:
‘N’ Ch Cl Fh Fl Bh Bl <cr>
‘N’= is the ASCII ‘N’ (0x4E) character.
Ch = high byte of the 16 bit coarse tuning factor. CL = low byte of the 16 bit coarse tuning factor. Fh = high byte of the 16 bit fine tuning factor. Fl = low byte of the 16 bit fine tuning factor.
Bh = high byte of the 16 bit BFO factor.
Bl = low byte of the 16 bit BFO factor.
<cr> = ASCII carriage return (0x0D) character.
none.
'''

'''
Receive Filter
‘M’ Rx Tx <cr>
‘M’ = the ASCII M (0x4d) character.
Rx = recieve mode (See Tx). Tx = recieve mode.
ASCII ‘0’ (0x30) for AM mode
ASCII ‘1’ (0x31) for USB mode
ASCII ‘2’ (0x32) for LSB mode
ASCII ‘3’ (0x33) for CW mode
ASCII ‘4’ (0x34) for FM mode
<cr> = ASCII carriage return (0x0D) character.
none.
M11<cr> for USB recieve, USB transmit. M23<cr> for LSB recieve, CW transmit.
The Pegasus contains a large number of selectable filters that can be used in AM, LSB, USB and CW detection modes. There is no default filter selected and the appropriate filter should be set for the selected detection mode. The selected filter must be considered in calculations for the FREQUENCY tuning factors, so any change in filter selection will require a recalculation of the frequency tuning factors. In general the filter selection will also affect the BFO setting factor. The exception is AM mode, where the BFO setting has no meaning and is ignored.
format: where:
response: example:
‘W’ fn <cr>
‘W’ = the ASCII W (0x57) character.
fn = a filter number in the range 0 thru 33 (binary). From Table 1 below. <cr> = ASCII carriage return (0x0D) character.
none.
W 0x10 <cr> for filter number 16, 2100 Hz bandwidth.
Filter #
Bandwidth
0
6000
1
5700
2
5400
3
5100
4
4800
5
4500
6
4200
7
3900
8
3600
9
3300
10
3000
11
2850
Filter #
Bandwidth
12
2700
13
2550
14
2400
15
2250
16
2100
17
1950
18
1800
19
1650
20
1500
21
1350
22
1200
23
1050
Filter #
Bandwidth
24
900
25
750
26
675
27
600
28
525
29
450
30
375
31
330
32
300
33
8000
'''

ser.write(b'M00\r')
time.sleep(.1)

'''
Speaker Output Control
The speaker volume control sets the gain of the audio amplifier. The control range is off (0x00) to full on (0xff). The input to the audio amplifier is set by the Line Level Audio Control. Refer to the Line Level Audio command for further information.
format: where:
response: example:
default:
‘V’ nn <cr>
V = ‘V’ (Ascii 0x56) character
nn = speaker volume 0 to 255 (0x00 - 0xff) <cr>=ASCII carriage return (0x0D)
none
V 0x20 0x0D sets the speaker to level 32
0 (no output)
'''

ser.write(b'V40\r')
time.sleep(.1)

'''
RF GAIN CONTROL
The relative RF gain can be controlled over a range of 0-255. A setting of 0 represents full RF gain whereas a setting of 255 (0xff) represents the minimum RF gain level. Because this control directly affects the RF hard- ware this will directly affect S-Unit responses and Squelch settings.
format: where:
response: default:
‘A’ nn <cr>
A= ‘A’ (Ascii 0x41) character
nn = 8 Bit Attenuation level (0x00 to 0xff) <cr> = ASCII carriage return (0x0D) none.
0 (minimum gain)
'''
ser.write(b'A255\r')
time.sleep(.1)

'''
RF ATTENUATOR CONTROL
An RF Attenuator may be switched in or out under software control. The Attenuator applies approximately 15 db of attenuation. Because this control directly affects the RF hardware this will directly affect S-Unit responses and Squelch settings.
format: where:
response: default:
‘B’ ch <cr>
B= is the ASCII ‘B’ (0x42) character ch = Setting
‘1’ (0x31) = ON
‘0’ (0x30) = OFF
<cr> = ASCII carriage return (0x0D) none.
Off
'''

ser.write(b'')
