
import serial
import time

ser = serial.Serial('/dev/cu.usbserial-AQ00T6NF')
ser.baudrate = 57600
ser.rtscts = True
ser.timeout = 1

FILTERS = [
        6000, 5700, 5400, 5100, 4800, 4500, 4200,
        3900, 3600, 3300, 3000, 2850, 2700, 2550,
        2400, 2250, 2100, 1950, 1800, 1650, 1500,
        1350, 1200, 1050, 900, 750, 675, 600,
        525, 450, 375, 330, 300, 8000,]

rx_filter = 33
mode = 0

#ser._rts_state(True)
ser.flushInput()

print (ser)




def get_line_blocking(ser):
    buf = ""
    while True:
        while not ser.getCTS():
            pass
        ch = ser.read(1)
        try:
            buf = buf + ch.decode("utf-8")
        except:
            pass
        if ch == b'\r':
            buf = buf[:-1]
            break
    return(buf)
        
def set_tuning(ser, coarse, fine, bfo):
    assert coarse >= 0 and coarse < 65536
    assert fine >= 0 and fine < 65536
    assert bfo >= 0 and bfo < 65536
        
    ser.write(b'\x4e%c%c%c%c%c%c\x0d' % 
            ((coarse>>8)&255, coarse&255, 
            (fine>>8)&255, fine&255, 
            (bfo>>8)&255, bfo&255))
        
        
def set_freq(ser, mode, freq, cwbfo=0):
    #assert hasattr(self, 'mode')
    #assert hasattr(self, 'rx_filter')
    MODE_CW = 3
    if mode != MODE_CW: 
        cwbfo = 0

    mcor = [0, 1, -1, -1][mode]
    fcor = FILTERS[rx_filter]/2+200

    adjusted_freq = freq - 1250 + mcor*(fcor+cwbfo)

    coarse = int(18000 + (adjusted_freq // 2500))
    fine = int(5.46 * (adjusted_freq % 2500))
    bfo = int(2.73 * (fcor+cwbfo+8000))
    set_tuning(ser, coarse, fine, bfo)


        
def init_radio(ser):
    mode = 0
    ser.write(b'\x4d%d\x0d' % mode)
    time.sleep(.1)
    squelch = 0
    ser.write(b'\x53%c\x0d' % squelch)
    time.sleep(.1)
    vol = 80
    ser.write(b'\x56%c\x0d' % vol)
    time.sleep(.1)
    line_vol = 5
    ser.write(b'\x43%c\r' % line_vol)
    agc = 2
    ser.write(b'\x47%d\x0d' % agc)
    time.sleep(.1)
    rx_filter = 33
    #ser.write(b'\x57%d\r' % rx_filter)
    time.sleep(.1)
   
    #set_freq(ser, mode, 3630000)
    set_freq(ser, mode, 15000000)
    
    
  

print ("Sending restart XX to Pegasus...")  
ser.write(b'XX\r') 
print ("Looking for DSP START or RADIO START...")
# force radio restart
 

while True:
    myline = get_line_blocking(ser)
    print (myline)
    if myline == "    DSP START" or myline == "   RADIO START":
        print ("Got: ",myline)
        if myline == "    DSP START":
            print ("DSP Start found.. Starting radio...")
            ser.write(b'P1\r')
            myline = get_line_blocking(ser)
        elif myline == "   RADIO START":
            print ("RADIO START FOUND. Doing radio init....")
            init_radio(ser)
            break
        else:
            ser.write(b'XX\r') 
                
            
            
        
def cls():
    print ('\x1b[2J')
    
        
# radio run
while True:

    ser.write(b'?S\r')
    #ser.write(b'\x3F\x6D\0D')
    buf = get_line_blocking(ser)
    print (buf)
    '''
    if buf[0] == 'S':
        buf = buf[1:]
        sunits = buf[:2]
        fractional = buf[-2:]
        #print (sunits+"."+fractional)
        strnum = str(int(sunits,16))+"."+str(int(fractional,16))
        #print (strnum)
        mysunits = float(strnum)
        #print (mysunits)
        sunits = mysunits
        
    
    #print (sunits)
    if sunits > 0.0 and sunits < 1.0:
        cls()
        print ("")
    elif sunits > 1.01 and sunits < 1.999:
        cls()
        print ("#")
    elif sunits > 2.000 and sunits < 2.999:
        cls()
        print ("##")
    elif sunits > 3.000 and sunits < 3.999:
        cls()
        print ("###")
    elif sunits > 4.0 and sunits < 4.999:
        cls()
        print ("####")
    elif sunits > 5.0and sunits < 5.999:
        cls()
        print ("#####")
    elif sunits > 6.0 and sunits < 6.999:
        cls()
        print ("######")
    elif sunits > 7.000 and sunits < 7.999:
        cls()
        print ("#######")
        
    elif sunits > 8.0 and sunits < 8.9999:
        cls()
        print ("########")
    elif sunits > 9.000 and sunits < 9.999:
        cls()
        print ("#########")
    elif sunits > 10.0000 and sunits < 10.9999:
        cls()
        print ("##########")
    elif sunits > 11.0000 and sunits < 11.9999:
        cls()
        print ("###########")

    elif sunits > 1700 and sunits < 1799:
        cls()
        print ("#############")
    elif sunits > 1800 and sunits < 1899:
        cls()
        print ("##############")
    elif sunits > 1900 and sunits < 1999:
        cls()
        print ("###############")
    elif sunits > 2000 and sunits < 2099:
        cls()
        print ("################")
    elif sunits > 2100 and sunits < 2199:
        cls()
        print ("#################")
    elif sunits > 2200 and sunits < 2299:
        cls()
        print ("##################")
    elif sunits > 3000 and sunits < 2399:
        cls()
        print ("###################")
    elif sunits > 2400 and sunits < 2499:
        cls()
        print ("####################")
    elif sunits > 2500 and sunits < 2599:
        cls()
        print ("#####################")
    elif sunits > 2600 and sunits < 2699:
        cls()
        print ("######################")
    elif sunits > 2700 and sunits < 2799:
        cls()
        print ("#######################")
    elif sunits > 2800 and sunits < 2899:
        cls()
        print ("########################")
    elif sunits > 2900 and sunits < 2999:
        cls()
        print ("#########################")
    elif sunits > 3000 and sunits < 3099:
        cls()
        print ("##########################")
    elif sunits > 1000 and sunits < 3199:
        cls()
        print ("###########################")
    elif sunits > 3200 and sunits < 3299:
        cls()
        print ("############################")
    elif sunits > 3300 and sunits < 3399:
        cls()
        print ("#############################")
    '''
    