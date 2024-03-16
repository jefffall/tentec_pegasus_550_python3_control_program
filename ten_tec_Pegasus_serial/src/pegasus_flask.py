#!/bin/python3
#import socket
import threading
import time
#import binascii
import struct
import webbrowser
import urllib3


from flask import Flask, request, jsonify

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)



app = Flask(__name__, static_url_path='')

"""
pegasus controller
:copyright: (c) 2013 by Tom van Dijk
:license: BSD, see LICENSE for more details.
"""
import serial
#import io

'''
static char TT550setMODE[]                      = "Mnn\r";
static char TT550setRcvBW[]                     = "Wx\r";
static char TT550setXmtBW[]                     = "Cx\r";
static char TT550setVolume[]            = "Vn\r";
static char TT550setAGC[]                       = "Gc\r";
static char TT550setRFGAIN[]            = "An\r";
static char TT550setATT[]                       = "Bc\r";
static char TT550setCWWPM[]                     = "Eabcdef\r";
static char TT550setMONVOL[]            = "Hn\r";
static char TT550setCWMONVOL[]          = "Jn\r";
static char TT550setNRNOTCH[]           = "Kna\r";
static char TT550setLINEOUT[]           = "Ln\r"; // 63 - min, 0 - max
static char TT550setMICLINE[]           = "O1cn\r"; // *******************************************
static char TT550setPOWER[]                     = "Pn\r"; // ****************************************
static char TT550setXMT[]                       = "Q1\r";
static char TT550setRCV[]                       = "Q0\r";
static char TT550setSQUELCH[]           = "Sn\r";       // 0..19; 6db / unit
static char TT550setVOX[]                       = "Uc\r";       // '0' = off; '1' = on
static char TT550setVOXGAIN[]           = "UGn\r";      // 0 <= n <= 255
static char TT550setANTIVOX[]           = "UAn\r";      // 0..255
static char TT550setVOXHANG[]           = "UHn\r";      // 0..255; n= delay*0.0214 sec
static char TT550setCWSPOTLVL[]         = "Fn\r";       // 0..255; 0 = off
static char TT550setCWQSK[]                     = "UQn\r";      // 0..255; 0 = none
static char TT550setAUXHANG[]           = "UTn\r";      // 0..255; 0 = none
static char TT550setBLANKER[]           = "Dn\r";       // 0..7; 0 = off
static char TT550setSPEECH[]            = "Yn\r";       // 0..127; 0 = off

static char TT550setDISABLE[]           = "#0\r";       // disable transmitter
static char TT550setENABLE[]            = "#1\r";       // enable transmitter
static char TT550setTLOOP_OFF[]         = "#2\r";       // disable T loop
static char TT550setTLOOP_ON[]          = "#3\r";       // enable T loop
static char TT550setKEYER_OFF[]         = "#6\r";       // enable keyer
static char TT550setKEYER_ON[]          = "#7\r";       // disable keyer
static char TT550setALIVE_OFF[]         = "#8\r";       // disable keep alive
//static char TT550setALIVE_ON[]        = "#9\r";       // enable keep alive
//static char TT550getAGC[]                     = "?Y\r";       // 0..255
//static char TT550getFWDPWR[]          = "?F\r";       // F<0..255>
//static char TT550getREFPWR[]          = "?R\r";       // R<0..255>
static char TT550query[]                        = "?S\r";       // S<0..255><0..255>
static char TT550getFWDREF[]            = "?S\r";       // T<0..255><0..255>

static char TT550setAMCARRIER[]         = "R%c\r";  00 to ff     // enables AM mode transmit

'''

class PEGASUS():
    MODE_AM = 0
    MODE_USB = 1
    MODE_LSB = 2
    MODE_CW = 3
    MODE_FM = 4

    AGC_SLOW = 1
    AGC_MEDIUM = 2
    AGC_FAST = 3
    
    TX_FILTERS = [
        0, 0, 0, 0, 0, 0, 0, 3900, 3600, 3300, 3000, 2850, 2700, 
        2550, 2400, 2250, 2100, 1950, 1800, 1650, 1500, 1350, 1200, 1050, 900]

    RX_FILTERS = [
        6000, 5700, 5400, 5100, 4800, 4500, 4200,
        3900, 3600, 3300, 3000, 2850, 2700, 2550,
        2400, 2250, 2100, 1950, 1800, 1650, 1500,
        1350, 1200, 1050, 900, 750, 675, 600,
        525, 450, 375, 330, 300, 8000]

    def __init__(self, port, sleep_time=0.2):
        self.ser = serial.Serial('/dev/cu.usbserial-AQ00T6NF')
        #self.ser = serial.Serial(port, 57600, timeout=0,parity=serial.PARITY_NONE, rtscts=1, xonxoff=True)

        self.ser.baudrate = 57600
        self.ser.rtscts = True
        self.ser.timeout = 0

        #ser = serial.serial_for_url('\r', timeout=1)
        #sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        
        self.strength = 0
        self.smeter = 0
        self.watts_forward = 0
        self.watts_reflected = 0
        self.firmware = ''
        self.rx_filter = 0
        self.tx_filter = 0
        self.tx_freq = 0
        self.rx_freq = 0
        self.transmit_bandwidth = 0
        self.transmit_watts_setting = "NOT SET"
        self.mode = 0
        self.last_mode = b'M00\r'
        self.speaker_volume = 0
        self.set_volume_by_knob = 0
        self.filter_value = 20 # 1500 Hz
        self.set_filter_by_knob = 0
        self.filter_hz = ""
        self.squelch_value = "NOT SET"
        self.anr_notch_value = "OFF"
        self.transmit_enable = "NOT SET"
        self.trasmit_power = "NOT SET"
        self.transmit_bandwidth = "NOT SET"
        self.mic_gain = "NOT SET"
        self.speech_processor = "NOT SET"
        self.tx_monitor = "NOT SET"
        self.tune_transmitter = "OFF"
        self.cw_sidetone = "NOT SET"
        
        
        self.tuning_in_motion = 0
        self.transmitter_freq_set = False
        
        self.anr = False
        self.notch = False
        
        self.last_antenna_tuner_command = ""
        self.antenna_auto_tune_in_progress = False
        
        thr = threading.Thread(target=PEGASUS.read_thread, args=[self])
        thr.daemon = True
        thr.start()
        
        '''
        thr = threading.Thread(target=PEGASUS.strength_thread, args=[self, sleep_time])
        thr.daemon = True
        thr.start()
        '''

        
   
    def get_line_blocking(self, ser):
        buf = b''
        while True:
            while not ser.getCTS():
                pass
            ch = ser.read(1)
            try:
                #buf = buf + ch.decode("utf-8")
                buf = buf + ch
            except:
                pass
            if ch == b'\r':
                buf = buf[:-1]
                break
        return(buf)
    
    #def rw_mutex(ser, op, bin_bytes):
    
    def reset_radio(self):
        self.ser.flush()
        time.sleep(.1)
        print ("Sending restart XX to Pegasus...")  
        self.ser.write(b'XX\r') 
        print ("Looking for DSP START or RADIO START...")
        #     force radio restart
 
        while True:
            try:
                myline = self.get_line_blocking(self.ser)
                print (myline)
            except:
                print ("read exception: reset radio")
            if myline == b'    DSP START':
                print ("DSP Start found.. Starting radio...")
                self.ser.flush()
                self.ser.write(b'P1\r')
            elif b'   RADIO START' in myline:
                print ("RADIO START FOUND. Doing radio init....")
                break
            else:
                self.ser.write(b'XX\r') 
                time.sleep(.1)
                
    def twos_comp_np(self, vals, bits):
        """compute the 2's compliment of array of int values vals"""
        vals[vals & (1<<(bits-1)) != 0] -= (1<<bits)
        return vals
    
    def calculate_frequency(self, keypad_buffer):
        kblen = len(keypad_buffer)
        if "." in keypad_buffer:
            parts = keypad_buffer.split(".")
            myfreq = parts[0] + parts[1]
            #if len(parts[0]) == 2:
                #zeros_needed = 7 - len(parts[1])
            #else:   
            zeros_needed = 7 - len(parts[1])
            for x in range(1,zeros_needed):
                myfreq = myfreq + "0"
        elif kblen == 4:
            myfreq = keypad_buffer + "000"  #108850000
        elif kblen == 5:
            myfreq = keypad_buffer + "000"  #38850000
        else:
            myfreq = keypad_buffer
            #print ("Len keypad buffer = ",kblen)
            if kblen == 2:
                zeros_needed = 9 - kblen
            elif len(keypad_buffer) == 1:
                zeros_needed = 8 - kblen
            else:
                print ("bad keypad buffer length = ",kblen)
                zeros_needed = 0
            for x in range(1,zeros_needed):
                myfreq = myfreq + "0"
                #print ("myfreq: ",myfreq)
        #print ("calculated frequency is: ",myfreq)
        return(myfreq)
    
    def twos_complement(self, value, bitWidth):
        if value >= 2**bitWidth:
            # This catches when someone tries to give a value that is out of range
            raise ValueError("Value: {} out of range of {}-bit value.".format(value, bitWidth))
        else:
            return value - int((value << 1) & 2**bitWidth)
    
    '''
    Read Thread and Signal strength Thread
    '''
    def read_thread(self):
        #self.ser = serial.Serial('/dev/cu.usbserial-AQ00T6NF')
        #self.ser = serial.Serial(port, 57600, timeout=0,parity=serial.PARITY_NONE, rtscts=1, xonxoff=True)

        #self.ser.baudrate = 57600
        #self.ser.rtscts = True
        #self.ser.timeout = 0
    
        time.sleep(2) # let radio reset
        #self.ser.timeout = 0
        keypad_buffer = ""
        while True:
            
            if self.tuning_in_motion > 0:
                self.tuning_in_motion = self.tuning_in_motion - 1
                if self.tuning_in_motion == 0:
                    self.transmitter_freq_set  = False
                
            if self.transmitter_freq_set == False:
                self.set_tx_freq(self.rx_freq)
                print ("Trasnmitter freq was automatically set to: ",self.rx_freq)
                self.transmitter_freq_set = True
                    
            
            time.sleep(.0001)
            #self.ser.write(b'?S\r')
            while not self.ser.getCTS():
                pass
            buf = self.get_line_blocking(self.ser)
            while not self.ser.getCTS():
                pass
                
            if buf != b'':
                    
                if buf[0] == 0x53: # S
                    buf = buf[1:]
                    sunits = buf[:2]
                    fractional = buf[-2:]
                    #print (sunits+"."+fractional)
                    strnum = str(int(sunits,16))+"."+str(int(fractional,16))
                    #print (strnum)
                    mysunits = float(strnum)
                    self.smeter = int(mysunits)
                    self.watts_forward = -1
                    self.watts_reflected = 0
                    #print (mysunits)
                # Encoder
                elif buf[0] == 0x21: # !
                    
                    # if set_volume_by_knob == 1 then we are doing a volume set
                    if self.set_volume_by_knob == "1":
                        #try:
                        my16 = struct.pack('BB',buf[1], buf[2])
                        myint = int.from_bytes(my16, 'big')
                        mytwo = self.twos_complement(myint, 16)
                        self.set_relative_speaker_volume(mytwo)
                        #except:
                            #pass
                    
                    # if set_volume_by_knob == 1 then we are doing a volume set
                    elif self.set_filter_by_knob == "1":
                        #try:
                        my16 = struct.pack('BB',buf[1], buf[2])
                        myint = int.from_bytes(my16, 'big')
                        mytwo = self.twos_complement(myint, 16)
                        self.set_relative_filter_value(mytwo)
                        #except:
                            #pass
                    
                    else: 
                        try:
                            my16 = struct.pack('BB',buf[1], buf[2])
                            myint = int.from_bytes(my16, 'big')
                            mytwo = self.twos_complement(myint, 16)
                            self.freq = self.freq + mytwo * self.step
                            controller.set_rx_freq(int(self.freq))
                        except:
                            pass
                        
                        
                     
                elif buf[0] == 0x55: # U
                        
                    #print ("Len of keypad buffer: ",len(buf))
                    if len(buf) > 1:
                        if buf[1] == 17:
                            print ("F1 pushed")
                        if buf[1] < 100:
                            #print (chr(buf[1]))
                            keypad_buffer = keypad_buffer + chr(buf[1])
                    elif len(buf) == 1:
                        #process_keypad(keypad_entry)
                        #print ("Buffer is: ",keypad_buffer)
                        myfreq = self.calculate_frequency(keypad_buffer)
                        controller.set_rx_freq(int(myfreq))
                        #controller.set_tx_freq(int(myfreq))
                        keypad_buffer = ''
                    else:
                            print ("Keypad buffer length error")
                elif buf[0] == 84:
                    try:
                        print ("Transmitter keyed now. Power forward = ",buf[1]," watts.")
                        self.smeter = -1
                        self.watts_forward = buf[1]
                        self.ser.write(b'\x3F\x52\r') # read SWR Reflected power
                    except:
                        print ("buf[1] exception - no value exists")
                elif buf[0] == 82:
                    try:
                        print ("Transmitter keyed now. Power reflected = ",buf[1]," watts.")
                        self.smeter = -1
                        self.watts_reflected = buf[1]
                    except:
                        print ("buf[1] exception - no value exists")
  
  
                else:
                    print ("exception in read loop: ")
                    
                    print ("I got a reply of buf[0]: ",buf[0])
                    
                    if buf[0] == 32 and buf[1] == 32:
                        self.ser.write(b'P1\r')
                        time.sleep(1)
                        controller.set_line_volume(70)
                        time.sleep(.1)
                        controller.set_speaker_volume(10)
                        time.sleep(.1)
                        controller.set_mode(self.mode)
                        time.sleep(.1)
                        controller.set_rx_filter(self.rx_filter)
                        time.sleep(.1)
                        controller.set_tx_filter(self.tx_filter)
                        time.sleep(.1)
                        controller.set_rx_freq(self.rx_freq)
                        time.sleep(.1)
                        controller.set_tx_freq(self.tx_freq)
                        
                    elif buf[0] == 90:
                        if self.antenna_auto_tune_in_progress == True:
                            pass
                        elif self.antenna_tuner_command_submitted == True:
                            self.antenna_tuner_command_submitted = False
                        else:
                            self.ser.write(b'P1\r')
                            time.sleep(3)
                            controller.set_line_volume(70)
                            time.sleep(.1)
                            controller.set_speaker_volume(10)

                    
                    try: 
                        print ("buf[0] value: ",buf[0])
                    except:
                        pass
                    try: 
                        print ("buf[1] value: ",buf[1])
                    except:
                        pass
     

    def set_rx_freq(self, freq, cwbfo=0):
        #print ("Set Frequency: ",freq)
        assert hasattr(self, 'mode')
        assert hasattr(self, 'rx_filter')

        if self.mode != PEGASUS.MODE_CW: 
            cwbfo = 0
            
        '''
        ASCII ‘0’ (0x30) for AM mode
        ASCII ‘1’ (0x31) for USB mode
        ASCII ‘2’ (0x32) for LSB mode
        ASCII ‘3’ (0x33) for CW mode
        ASCII ‘4’ (0x34) for FM mode
        '''   
            
        mcor = [0, 1, -1, -1, 0][self.mode]
        #print ("RX Filter index = ",self.rx_filter)
        #print ("RX filter value = ",PEGASUS.RX_FILTERS[int(self.rx_filter)])
        #print ("List index = ",PEGASUS.FILTERS[int(self.rx_filter)])
        fcor = PEGASUS.RX_FILTERS[int(self.rx_filter)]/2+200

        adjusted_freq = freq - 1250 + mcor*(fcor+cwbfo)

        coarse = int(18000 + (adjusted_freq // 2500))
        fine = int(5.46 * (adjusted_freq % 2500))
        bfo = int(2.73 * (fcor+cwbfo+8000))
        self.set_rx_tuning(coarse, fine, bfo)

        self.rx_freq = freq
        self.freq = freq
        self.cwbfo = cwbfo
        self.tx_freq = freq

    def set_rx_tuning(self, coarse, fine, bfo):
        self.tuning_in_motion = 3
        #print ("Set tuning - coarse:",coarse, "fine",fine, "bfo: ",bfo)
        assert coarse >= 0 and coarse < 65536
        assert fine >= 0 and fine < 65536
        assert bfo >= 0 and bfo < 65536
        
        #print ("rx_coarse = ", coarse)
        #print ("rx_fine = ", fine)
        #print ("rx_bfo = ", bfo)
        
        self.ser.write(b'\x4e%c%c%c%c%c%c\x0d' % 
                ((coarse>>8)&255, coarse&255, 
                (fine>>8)&255, fine&255, 
                (bfo>>8)&255, bfo&255))
        
        #self.ser.write(b'\x54%c%c%c%c%c%c\x0d' % 
                #((coarse>>8)&255, coarse&255, 
                #(fine>>8)&255, fine&255, 
                #(bfo>>8)&255, bfo&255))
        
        
        self.coarse = coarse
        self.fine = fine
        self.bfo = bfo
        
        
   
    '''
    The tuning factors Ch, Cl, Fh, Fl, Bh and Bl are calculated using the formulas presented here. 
    input:
        Tfreq = Tuned Frequency in MHz.
        Mcor = Mode Correction = +1 for USB, -1 for LSB, -1 for CW,0 for FM. 
        Fcor = Filter Correction calculated using (Bandwidth/2)+200 in Hz.
        Cbfo = Desired center frequency of filter.
            In CW mode this is the BFO setting.
            In SSB Transmit this value is typically 1500 Hz
    calculation:
        AdjTfreq = Adjusted Tuned Frequency = Tfreq-0.00125+((Mcor*Fcor)/1000000)
            where Fcor is determined as...
                if ((FilterBw/2)+200) >1500) then Fcor=FilterBw/2+200 else Fcor=1500. if (Mode=CW) Fcor=1500+Cbfo.
                
        Ctf = Coarse tuing factor = (int) (AdjTfreq/0.0025)+18000
            where (int) is the integer function to get the integer only portion of the division
        Ftf = Fine tuning factor = mod(AdjTfreq,0.0025) * 2500*5.46
            where the mod function is used to get the fractional remainder of a division operation.
        Btf = Bfo Tuning Factor = (int) ((fcor+cBFO+8000)*2.73)
            where (int) is the integer function to get the integer only portion of the division
    '''
    
    
        
    def set_tx_tuning(self, coarse, fine, bfo):
        #print ("Set tuning - coarse:",coarse, "fine",fine, "bfo: ",bfo)
        assert coarse >= 0 and coarse < 65536
        assert fine >= 0 and fine < 65536
        assert bfo >= 0 and bfo < 65536
        
        #print ("tx_coarse = ", coarse)
        #print ("tx_fine = ", fine)
        #print ("tx_bfo = ", bfo)
        
        self.ser.write(b'\x54%c%c%c%c%c%c\x0d' % 
                ((coarse>>8)&255, coarse&255, 
                (fine>>8)&255, fine&255, 
                (bfo>>8)&255, bfo&255))
   
        self.tx_coarse = coarse
        self.tx_fine = fine
        self.tx_bfo = bfo
        
    
    ########################################################    
    
    #def set_vfo_tx(self, freq, Cbfo=0):
        #void RIG_TT550::set_vfoTX(unsigned long int freq)
    def set_tx_freq(self, freq, Cbfo=0):
        if self.mode == self.MODE_CW:
            print ("transmitter freq set to CW mode")
            freq = freq + 31
        elif self.mode == self.MODE_FM:
            freq = freq + 36
        elif self.mode == self.MODE_AM:
            #freq = freq - 1100
            freq = freq - 0
        Bfo = 600
        #NVal = 0 
        #FVal = 0                    #N value / finetune value
        #TBfo = 0                    #// temporary BFO'''
        IBfo = 1500                 ##// Intermediate BFO Freq'''
        #bwBFO = 0                   ##// BFO based on selected bandwidth'''
        FilterBw = 0                ##// Filter Bandwidth determined from table'''
        tt550_use_xmt_bw = True

        #XitAdj = 0
        
        VfoAdj = 0
        #unsigned long int lFreq = freq * (1 + VfoAdj * 1e-6);
        #lFreq = freq * (1 + VfoAdj) * 1000000
        lFreq = freq * (1 + VfoAdj) 

        #lFreq += XitAdj = XitActive ? XitFreq : 0;

        if tt550_use_xmt_bw:
                #FilterBw = TT550_xmt_filter_width[progStatus.tt550_xmt_bw]
                FilterBw = PEGASUS.TX_FILTERS[int(self.tx_filter)]
        else:
                #FilterBw = TT550_filter_width[def_bw]
                FilterBw = 3000
                
        if FilterBw < 900:
            FilterBw = 900;
        elif FilterBw > 3900:
            FilterBw = 3900;
        #if (def_mode == TT550_DIGI_MODE) FilterBw = 3000;

        bwBFO = (FilterBw/2) + 200;
        #//IBfo = (bwBFO > IBfo) ?  bwBFO : IBfo ;
        
        if bwBFO > IBfo:
            IBfo = bwBFO
        else:
            IBfo = IBfo
            
        if self.mode == 0: # AM MODE
          
            #TT550setAMCARRIER[]         = "R%c\r";  00 to ff     // enables AM mode transmit
            #lFreq += IBfo
            #TBfo = int(IBfo * 2.73)
            #
            TBfo = 0
            IBfo = 0
            # 40 is 100 watts
            self.ser.write(b'R\x40\r')  #00 to ff     // enables AM mode transmit
        
        #if def_mode == TT550_USB_MODE or def_mode == TT550_DIGI_MODE:
        if self.mode == 1: # USB MODE
            lFreq += IBfo
            TBfo = int(IBfo * 2.73)

        if self.mode == 2: #LSB MODE
            lFreq -= IBfo;
            TBfo = int(IBfo * 2.73)

        #// CW Mode uses LSB Mode
        if self.mode == 3: # CW MODE
            IBfo = 1500 # fixed for CW
            lFreq += Bfo - IBfo
            TBfo = int(Bfo * 2.73)

        if self.mode == 4: #FM MODE
            IBfo = 0
            lFreq -= IBfo
            TBfo = 0

        lFreq -= 1250
        NVal = lFreq / 2500 + 18000
        FVal = int(lFreq % 2500) * 5.46 # was 5.46
        self.set_tx_tuning(int(NVal), int(FVal), int(TBfo))
        return
   
   
    def set_rf_gain(self, rf_gain):
        if rf_gain >= 0 and rf_gain <= 255:
            print ("Set RF gain: ",(b'\x41%c\x0d' % rf_gain))
            self.ser.write(b'\x41%c\x0d' % rf_gain)
            self.rf_gain = rf_gain
            
    def set_rf_attenuator(self, rf_attenuator):
        if rf_attenuator >= 0 and rf_attenuator <= 1:
            print ("Set RF attenuator: ",b'\x42%d\x0d' % rf_attenuator)
            self.ser.write(b'\x42%d\x0d' % rf_attenuator)
            self.rf_attenuator = rf_attenuator

    def set_agc(self, agc):
        if agc >= 0 and agc <= 3:
            print ("Set AGC: ",b'\x47%d\x0d' % agc)
            self.ser.write(b'\x47%d\x0d' % agc)
            self.agc = agc

    def set_mode(self, mode):
        print ("In Set mode. mode = ",mode)
        if mode >= 0 and mode <= 4:
            self.mode = mode
            if mode == 0:
                self.ser.write(b'M00\r')
                self.last_mode = b'M00\r'
                print ("Mode: ",b'M00\r')
            elif mode == 1:
                self.ser.write(b'M11\r')
                self.last_mode = b'M11\r'
                print ("Mode: ",b'M11\r')
            elif mode == 2:
                self.ser.write(b'M22\r')
                self.last_mode = b'M22\r'
                print ("Mode: ",b'M22\r')
            elif mode == 3:
                self.ser.write(b'M33\r')
                self.last_mode = b'M33\r'
                print ("Mode: ",b'M33\r')
            elif mode == 4:
                self.ser.write(b'M44\r')
                self.last_mode = b'M44\r'
                print ("Mode: ",b'M44\r')
            else:
                print ("Mode number out of range of mode >= 0 and mode <= 4")
                
           
            #print ("Set mode: ",b'\x4d%d%d\x0d' % (mode, mode))
            #self.ser.write(b'\x4d%d%d\x0d' % (mode, mode))
            #self.mode = mode

    def set_rx_filter(self, filter):
        if filter >= 0 and filter <= 33:
            self.rx_filter = filter
            match filter:
                case 0:
                    controller.filter_hz = "6000"
                    self.ser.write(b'\x57\x00\r')
                case 1:
                    controller.filter_hz = "5700"
                    self.ser.write(b'\x57\x01\r')
                case 2:
                    controller.filter_hz = "5400"
                    self.ser.write(b'\x57\x02\r')
                case 3:
                    controller.filter_hz = "5100"
                    self.ser.write(b'\x57\x03\r')
                case 4:
                    controller.filter_hz = "4800"
                    self.ser.write(b'\x57\x04\r')
                case 5:
                    controller.filter_hz = "4500"
                    self.ser.write(b'\x57\x05\r')
                case 6:
                    controller.filter_hz = "4200"
                    self.ser.write(b'\x57\x06\r')
                case 7:
                    controller.filter_hz = "3900"
                    self.ser.write(b'\x57\x07\r')
                case 8:
                    controller.filter_hz = "3600"
                    self.ser.write(b'\x57\x08\r')
                case 9:
                    controller.filter_hz = "3300"
                    self.ser.write(b'\x57\x09\r')
                case 10:
                    controller.filter_hz = "3000"
                    self.ser.write(b'\x57\x0a\r')
                case 11:
                    controller.filter_hz = "2850"
                    self.ser.write(b'\x57\x0b\r')
                case 12:
                    controller.filter_hz = "2700"
                    self.ser.write(b'\x57\x0c\r')
                case 13:
                    controller.filter_hz = "2550"
                    self.ser.write(b'\x57\x0d\r')
                case 14:
                    controller.filter_hz = "2400"
                    self.ser.write(b'\x57\x0e\r')
                case 15:
                    controller.filter_hz = "2250"
                    self.ser.write(b'\x57\x0f\r')
                case 16:
                    controller.filter_hz = "2100"
                    self.ser.write(b'\x57\x10\r')
                case 17:
                    controller.filter_hz = "1950"
                    self.ser.write(b'\x57\x11\r')
                case 18:
                    controller.filter_hz = "1800"
                    self.ser.write(b'\x57\x12\r')
                case 19:
                    controller.filter_hz = "1650"
                    self.ser.write(b'\x57\x13\r')
                case 20:
                    controller.filter_hz = "1500"
                    self.ser.write(b'\x57\x14\r')
                case 21:
                    controller.filter_hz = "1350"
                    self.ser.write(b'\x57\x15\r')
                case 22:
                    controller.filter_hz = "1200"
                    self.ser.write(b'\x57\x16\r')
                case 23:
                    controller.filter_hz = "1050"
                    self.ser.write(b'\x57\x17\r')
                case 24:
                    controller.filter_hz = "900"
                    self.ser.write(b'\x57\x18\r')
                case 25:
                    controller.filter_hz = "750"
                    self.ser.write(b'\x57\x19\r')
                case 26:
                    controller.filter_hz = "675"
                    self.ser.write(b'\x57\x1a\r')
                case 27:
                    controller.filter_hz = "600"
                    self.ser.write(b'\x57\x1b\r')
                case 28:
                    controller.filter_hz = "525"
                    self.ser.write(b'\x57\x1c\r')
                case 29:
                    controller.filter_hz = "450"
                    self.ser.write(b'\x57\x1d\r')
                case 30:
                    controller.filter_hz = "375"
                    self.ser.write(b'\x57\x1e\r')
                case 31:
                    controller.filter_hz = "330"
                    self.ser.write(b'\x57\x1f\r')
                case 32:
                    controller.filter_hz = "300"
                    self.ser.write(b'\x57\x20\r')
                case 33:
                    controller.filter_hz = "8000"
                    self.ser.write(b'\x57\x21\r')
                
    def set_relative_filter_value(self, relative):
        self.filter_value = self.filter_value - relative
        if self.filter_value >= 32:
            self.filter_value = 32
        elif self.filter_value < -1:
            self.filter_value = -1
             
        if (1 == 1):
        #if self.filter_value >= -1 and self.filter_value <= 32:
             
            match self.filter_value:
                case -1:
                    controller.filter_hz = "8000"
                    self.ser.write(b'\x57\x21\r')
                case 0:
                    controller.filter_hz = "6000"
                    self.ser.write(b'\x57\x00\r')
                case 1:
                    controller.filter_hz = "5700"
                    self.ser.write(b'\x57\x01\r')
                case 2:
                    controller.filter_hz = "5400"
                    self.ser.write(b'\x57\x02\r')
                case 3:
                    controller.filter_hz = "5100"
                    self.ser.write(b'\x57\x03\r')
                case 4:
                    controller.filter_hz = "4800"
                    self.ser.write(b'\x57\x04\r')
                case 5:
                    controller.filter_hz = "4500"
                    self.ser.write(b'\x57\x05\r')
                case 6:
                    controller.filter_hz = "4200"
                    self.ser.write(b'\x57\x06\r')
                case 7:
                    controller.filter_hz = "3900"
                    self.ser.write(b'\x57\x07\r')
                case 8:
                    controller.filter_hz = "3600"
                    self.ser.write(b'\x57\x08\r')
                case 9:
                    controller.filter_hz = "3300"
                    self.ser.write(b'\x57\x09\r')
                case 10:
                    controller.filter_hz = "3000"
                    self.ser.write(b'\x57\x0a\r')
                case 11:
                    controller.filter_hz = "2850"
                    self.ser.write(b'\x57\x0b\r')
                case 12:
                    controller.filter_hz = "2700"
                    self.ser.write(b'\x57\x0c\r')
                case 13:
                    controller.filter_hz = "2550"
                    self.ser.write(b'\x57\x0d\r')
                case 14:
                    controller.filter_hz = "2400"
                    self.ser.write(b'\x57\x0e\r')
                case 15:
                    controller.filter_hz = "2250"
                    self.ser.write(b'\x57\x0f\r')
                case 16:
                    controller.filter_hz = "2100"
                    self.ser.write(b'\x57\x10\r')
                case 17:
                    controller.filter_hz = "1950"
                    self.ser.write(b'\x57\x11\r')
                case 18:
                    controller.filter_hz = "1800"
                    self.ser.write(b'\x57\x12\r')
                case 19:
                    controller.filter_hz = "1650"
                    self.ser.write(b'\x57\x13\r')
                case 20:
                    controller.filter_hz = "1500"
                    self.ser.write(b'\x57\x14\r')
                case 21:
                    controller.filter_hz = "1350"
                    self.ser.write(b'\x57\x15\r')
                case 22:
                    controller.filter_hz = "1200"
                    self.ser.write(b'\x57\x16\r')
                case 23:
                    controller.filter_hz = "1050"
                    self.ser.write(b'\x57\x17\r')
                case 24:
                    controller.filter_hz = "900"
                    self.ser.write(b'\x57\x18\r')
                case 25:
                    controller.filter_hz = "750"
                    self.ser.write(b'\x57\x19\r')
                case 26:
                    controller.filter_hz = "675"
                    self.ser.write(b'\x57\x1a\r')
                case 27:
                    controller.filter_hz = "600"
                    self.ser.write(b'\x57\x1b\r')
                case 28:
                    controller.filter_hz = "525"
                    self.ser.write(b'\x57\x1c\r')
                case 29:
                    controller.filter_hz = "450"
                    self.ser.write(b'\x57\x1d\r')
                case 30:
                    controller.filter_hz = "375"
                    self.ser.write(b'\x57\x1e\r')
                case 31:
                    controller.filter_hz = "330"
                    self.ser.write(b'\x57\x1f\r')
                case 32:
                    controller.filter_hz = "300"
                    self.ser.write(b'\x57\x20\r')
    
         
    def set_tx_filter(self, filter):
        if filter >= 0 and filter <= 24:
            print ("set tx_filter :",b'C%c\r' % filter)
            self.ser.write(b'C%c\r' % filter)
            self.tx_filter = filter


    def set_line_volume(self, vol):
        if vol < 0: vol = 0
        if vol > 63: vol = 63
        #self.ser.write(b'L' % vol)
        print ("Line volume: ",b'\x43%c\x0d' % vol)
        self.ser.write(b'\x43%c\r' % vol)
        self.line_volume = vol
        
        
        
    def set_relative_speaker_volume(self, relative):
        vol = self.speaker_volume + relative
        
        if vol < 0: vol = 0
        if vol > 30: vol = 30
        
        self.speaker_volume = vol
        
        vol = vol + 20
        
        vol = int(vol * 2.5549)
        
        
        vol = int(hex(int(vol)),16)
        print ("volume by knob volume = ",vol)
        self.ser.write(b'V%c\r' % vol)
        
        

    def set_speaker_volume(self, vol):
        
        print ("vol = ", vol)
        vol = int(vol)
        if vol < 0: vol = 0
        if vol > 30: vol = 30
        self.speaker_volume = vol
        
        if vol == 0:
            print ("vol:",b'V%c\r' % vol)
            self.ser.write(b'V%c\r' % vol)
            return
            
        vol = vol + 20
        vol = int(vol * 2.5547)
        vol = int(hex(int(vol)),16)
        
        #self.ser.write(b'\x56\x00%c\x0d' % vol)
        print ("vol:",b'V%c\r' % vol)
        self.ser.write(b'V%c\r' % vol)
        
    def set_relative_volume(self, rel_vol):
        if self.speaker_volume == 0:
            print ("speaker volume is 0")
            return
        #if rel_vol < 0: rel_vol = 0
        #if rel_vol > 63: rel_vol = 63
        print ("relative volume = ",rel_vol, "speaker volume = ",self.speaker_volume)
        vol = self.speaker_volume + int(rel_vol)
        
        vol = vol + 20
        vol = int(vol * 2.5547)
        vol = int(hex(int(vol)),16)

        print ("Set relative volume: ",b'\x56%c\x0d' % vol)
        self.ser.write(b'\x56%c\x0d' % vol)
        
    
        
    def set_squelch(self, sunits):
        if sunits < 0: sunits = 0
        if sunits > 19: sunits = 19
        #self.ser.write(b'V100\r' % vol)
        self.squelch_value = "S" + str(sunits)
        self.ser.write(b'\x53%c\x0d' % sunits)
        print ("Set squelch: ",b'\x53%c\x0d')
        self.squelch = sunits

    def send_get_firmware(self):
        self.firmware = ''
        self.ser.write(b'\x3f\x0d')
        
     
    def set_audio_monitor_volume(self, audio_monitor_volume):
        if audio_monitor_volume >= 0 and audio_monitor_volume <= 255:
            self.ser.write(b'C%c\r' % audio_monitor_volume)
            print ("audio_monitor_volume: ",b'C%c\x0d' % audio_monitor_volume)
            self.audio_monitor_volume = audio_monitor_volume
           
    def set_cw_sidetone_volume(self, cw_sidetone_volume):
        if cw_sidetone_volume >= 0 and cw_sidetone_volume <= 255:
            self.ser.write(b'C%c\r' % cw_sidetone_volume)
            print ("cw_sidetone_volume: ",b'C%c\x0d' % cw_sidetone_volume)
            self.cw_sidetone_volume = cw_sidetone_volume
            
    def set_noise_reduction(self, noise_reduction):
        if noise_reduction >= 0 and noise_reduction <= 255:
            self.ser.write(b'\x4b%c\x00\x0d' % noise_reduction)
            print ("noise_reduction: ",b'\x4b%c\x00\x0d' % noise_reduction)
            self.noise_reduction = noise_reduction
            
    def set_automatic_notch(self, automatic_notch):
        if automatic_notch >= 0 and automatic_notch <= 255:
            self.ser.write(b'\x4b\x00%c\x0d' % automatic_notch)
            print ("automatic_notch: ",b'\x4b\x00%c\x0d' % automatic_notch)
            self.automatic_notch = automatic_notch
            
    def set_output_power(self, output_power):
        if output_power >= 0 and output_power <= 255:
            print ("Transmit output power:", b'\x50%c\x0d' % output_power)
            self.ser.write(b'\x50%c\x0d' % output_power)
            print ("output_power: ",b'\x50%c\x0d' % output_power)
            self.output_power = output_power
            
    def set_tune(self, tune):
        if tune >= 0 and tune <= 1:
            self.ser.write(b'\x51%d\x0d' % tune)
            print ("tune: ",b'\x51%d\x0d' % tune)
            self.tune = tune
               
    def set_noise_blanker(self, noise_blanker):
        if noise_blanker >= 0 and noise_blanker <= 1:
            self.ser.write(b'\x33%d\x0d' % noise_blanker)
            print ("set_noise_blanker: ",b'\x33%d\x0d' % noise_blanker)
            self.noise_blanker = noise_blanker
            
    def set_speech_processor(self, speech_processor):
        if speech_processor >= 0 and speech_processor <= 7:
            self.ser.write(b'\x59%d\x0d' % speech_processor)
            print ("set_speech_processor: ",b'\x59%d\x0d' % speech_processor)
            self.speech_processor = speech_processor
            
    def get_query(self, item):
            if item == "V":
                self.ser.write(b'\x3f\x56\x0d')
                print ("get_query: ",b'\x3f\x56\x0d')
            elif item == "X":
                self.ser.write(b'\x3f\x58\x0d')
                print ("get_query: ",b'\x3f\x58\x0d')
            elif item == "!":
                self.ser.write(b'\x3f\x21\x0d')
                print ("get_query: ",b'\x3f\x21\x0d')
            elif item == "F":
                self.ser.write(b'\x3f\x46\x0d')
                print ("get_query: ",b'\x3f\x46\x0d')
            elif item == "R":
                self.ser.write(b'\x3f\x72\x0d')
                print ("get_query: ",b'\x3f\x72\x0d')
            elif item == "S":
                self.ser.write(b'\x3f\x53\x0d')
                print ("get_query: ",b'\x3f\x53\x0d')
            else:
                print ("Get Query:",item," Is not valid. Must be V or X or ! or F or R or S")
          
            
    def set_transmitter_controls(self, num):
        if num >= 0 and num <= 3:
            self.ser.write(b'\x23%d\x0d' % num)
            print ("set_transmitter_controls: ",b'\x23%d\x0d' % num)
            if num == 0:
                print ("Disable Transmitter")
                self.transmitter_enabled = 0
            elif num == 1:
                print ("Enable Transmitter")
                self.transmitter_enabled = 1
            elif num == 2:
                print (" Disable ‘T’ loop (amplifier loop).")
                self.tloop_enabled = 0
            elif num == 3:
                print (" Enable ‘T’ loop.")
                self.tloop_enabled = 1
        elif num >= 6 and num <= 9:
            self.ser.write(b'\x23%d\x0d' % num)
            print ("set_transmitter_controls: ",b'\x23%d\x0d' % num)
            if num == 6:
                print ("Enable Keyer.")
                self.keyer_enabled = 1
            elif num == 7:
                print (" Disable Keyer.")
                self.keyer_enabled = 0
            elif num == 8:
                print ("Disable Keep Alive.")
                self.enable_keep_alive = 0
            elif num == 9:
                print ("Enable Keep Alive.")
                self.enable_keep_alive = 1
        else:
            print ("transmitter controls: ",num, "is out of range 0 to 9")
            
            
    def set_squelch_web(self, sunit):
        print ("Set squelch web:", sunit)
        self.squelch_value = sunit
        sunit = int(sunit[1:])
        self.ser.write(b'S%c\r' % sunit)
        
    def set_anr_notch(self, state):
        print ("Set anr notch:", state)
        print (state)
        if state == "ANR ON":
            self.anr = True
        elif state == "NOTCH ON":
            self.notch = True
        elif state == "ANR OFF":
            self.anr = False
        elif state == "NOTCH OFF":
            self.notch = False
        elif state == "ANR + NOTCH OFF":
            self.notch = False
            self.anr = False
        else:
            print ("Notch selection error")
            return 
        
        if self.anr == False and self.notch == False:
            self.anr_notch_value = "OFF"
            self.ser.write(b'K00\r')
        elif self.anr == False and self.notch == True:
            self.anr_notch_value = "NOTCH"
            self.ser.write(b'K01\r')
        elif self.anr == True and self.notch == False:
            self.anr_notch_value = "ANR"
            self.ser.write(b'K10\r')
        elif self.anr == True and self.notch == True:
            self.anr_notch_value = "ANR+NOTCH"
            self.ser.write(b'K11\r')
        else:
            print ("ANL Notch assignment - logic error")
            
        return
    
    def set_transmit_enable(self, state):
        print ("Set transmit enable:", state)
        if state == "Enable Transmitter":
            #control_code = 0x01
            self.ser.write(b'#2\r') # Disable T loop
            time.sleep(.1)
            self.ser.write(b'#7\r') # Disable Keyer
            time.sleep(.1)
            self.ser.write(b'#1\r') # Enable transmitter
            time.sleep(.1)
            self.transmit_enable = "ENABLED"
            #self.ser.write(b'#%c\r' % control_code)
            #self.ser.write(b'C7\r')
            # Vox off
            #self.ser.write(b'U0\r')
            # Keyer off
            #self.ser.write(b'#6\r')
            
        else:
            #control_code = 0x00
            #self.ser.write(b'#%c\r' % control_code)
            self.transmit_enable = "DISABLED"
            self.ser.write(b'#0\r')
            
    
    def set_transmit_power(self, power):
        print ("Set transmit power:", power)
        parts = power.split(" ")
        self.trasmit_power = parts[0] + " WATTS"
        watts = int(parts[0])
        print ("watts requested: ",watts)
        match watts:
            case 0:
                self.ser.write(b'P%c\r' % 0)
            case 1:
                print ("requesting 1 watt")
                self.ser.write(b'P%c\r' % 1)
            case 5:
                self.ser.write(b'P%c\r' % 18)
            case 10:
                self.ser.write(b'P%c\r' % 36)
            case 15:
                self.ser.write(b'P%c\r' % 54)
            case 20:
                self.ser.write(b'P%c\r' % 72)
            case 25:
                self.ser.write(b'P%c\r' % 90 )
            case 30:
                self.ser.write(b'P%c\r' % 108)
            case 35:
                self.ser.write(b'P%c\r' % 126 )
            case 40:
                self.ser.write(b'P%c\r' % 144)
            case 50:
                self.ser.write(b'P%c\r' % 162)
            case 60:
                self.ser.write(b'P%c\r' % 180)
            case 70:
                self.ser.write(b'P%c\r' % 198)
            case 80:
                self.ser.write(b'P%c\r' % 216 )
            case 90:
                self.ser.write(b'P%c\r' % 234 )
            case 100:
                self.ser.write(b'P%c\r' % 255)
                
    def set_transmit_bandwidth(self, bandwidth):
        myfilter = int(PEGASUS.TX_FILTERS.index(bandwidth))
        if myfilter >= 7 and myfilter <= 24:
            self.transmit_bandwidth = str(bandwidth) + " HZ"
            self.tx_filter = myfilter
            match myfilter:
                case 7:
                    self.ser.write(b'\x43\x07\r')
                case 8:
                    self.ser.write(b'\x43\x08\r')
                case 9:
                    self.ser.write(b'\x43\x09\r')
                case 10:
                    self.ser.write(b'\x43\x0a\r')
                case 11:
                    self.ser.write(b'\x43\x0b\r')
                case 12:
                    self.ser.write(b'\x43\x0c\r')
                case 13:
                    self.ser.write(b'\x43\x0d\r')
                case 14:
                    self.ser.write(b'\x43\x0e\r')
                case 15:
                    self.ser.write(b'\x43\x0f\r')
                case 16:
                    self.ser.write(b'\x43\x10\r')
                case 17:
                    self.ser.write(b'\x43\x11\r')
                case 18:
                    self.ser.write(b'\x43\x12\r')
                case 19:
                    self.ser.write(b'\x43\x13\r')
                case 20:
                    self.ser.write(b'\x43\x14\r')
                case 21:
                    self.ser.write(b'\x43\x15\r')
                case 22:
                    self.ser.write(b'\x43\x16\r')
                case 23:
                    self.ser.write(b'\x43\x17\r')
                case 24:
                    self.ser.write(b'\x43\x18\r')
               
           
            print ("Set transmitter bandwidth: ",b'C%x\r' % myfilter)
        else:
            print ("Error Setting transmit filter! Out of range",myfilter)
       
    def set_mic_gain(self, percent):
        print ("mic gain = ",percent)
        self.mic_gain = percent
        gain = int(percent[:-1])
        print ("int gain = ",gain)
        '''
        Bit 0 is set to mute the mic.
        
        '''
        
        match gain:
            case 100:
                self.ser.write(b'O1\xfe\r')
            case 93:
                self.ser.write(b'O1\xfd\r')
            case 86:
                self.ser.write(b'O0\xfc\r')
            case 80:
                self.ser.write(b'O1\xfb\r')
            case 73:
                self.ser.write(b'O1\x0a\r')
            case 66:
                self.ser.write(b'O1\x09\r')
            case 60:
                self.ser.write(b'O1\x08\r')
            case 53:
                self.ser.write(b'O1\x07\r')
            case 46:
                self.ser.write(b'O1\x06\r')
            case 40:
                self.ser.write(b'O1\x09\r')
            case 33:
                self.ser.write(b'O1\x05\r')
            case 26:
                self.ser.write(b'O1\x04\r')
            case 20:
                self.ser.write(b'O1\x03\r')
            case 14:
                self.ser.write(b'O1\x02\r')
            case 6:
                self.ser.write(b'O1\x01\r')
            case 0:
                self.ser.write(b'O1\x00\r')
            
         
         
            
    
    def set_speech_processor_web(self, percent):
        print ("Set speech  processor:", percent)
        self.speech_processor = percent
        if percent == "OFF":
            percent = "0%"
        level = int(percent[:-1])
        match level:
            case 0:
                self.ser.write(b'Y\x00\r')
            case 10:
                self.ser.write(b'Y\x11\r')
            case 20:
                self.ser.write(b'Y\x17\r')
            case 30:
                self.ser.write(b'Y\x22\r')
            case 40:
                self.ser.write(b'Y\x2e\r')
            case 50:
                self.ser.write(b'Y\x3a\r')
            case 60:
                self.ser.write(b'Y\x45\r')
            case 70:
                self.ser.write(b'Y\x51\r')
            case 80:
                self.ser.write(b'Y\x5c\r')
            case 90:
                self.ser.write(b'Y\x68\r')
            case 100:
                self.ser.write(b'Y\x74\r')
            case 100:
                self.ser.write(b'Y\x7f\r')
         
            
            
    def set_tx_monitor_level(self, percent):
        if percent == "0%":
            self.tx_monitor = "OFF"
        else:
            self.tx_monitor = percent
            
        print ("Set tx monitor:", percent)
        
        level = int(percent[:-1])
        print ("level = ",level)
        match level:
            case 0:
                self.ser.write(b'H\x00\r')
            case 15:
                self.ser.write(b'H\x06\r')
            case 20:
                self.ser.write(b'H\x0B\r')
            case 30:
                self.ser.write(b'H\x11\r')
            case 45:
                self.ser.write(b'H\x17\r')
            case 60:
                self.ser.write(b'H\x1d\r')
            case 75:
                self.ser.write(b'H\x22\r')
            case 90:
                self.ser.write(b'H\x28\r')
            case 80:
                self.ser.write(b'H\x2D\r')
            case 90:
                self.ser.write(b'H\x34\r')
            case 100:
                self.ser.write(b'H\x3F\r')
          
    def set_cw_sidetone(self, percent):
        self.cw_sidetone = percent
        if percent == "OFF":
            percent = "0%"
            
        print ("Set cw sidetone:", percent)
        
        level = int(percent[:-1])
        print ("level = ",level)
        match level:
            case 0:
                self.ser.write(b'J\x00\r')
            case 10:
                self.ser.write(b'J\x19\r')
            case 20:
                self.ser.write(b'J\x33\r')
            case 30:
                self.ser.write(b'J\x4C\r')
            case 40:
                self.ser.write(b'J\x66\r')
            case 50:
                self.ser.write(b'J\x7D\r')
            case 60:
                self.ser.write(b'J\x99\r')
            case 70:
                self.ser.write(b'J\xB2\r')
            case 80:
                self.ser.write(b'J\xCD\r')
            case 90:
                self.ser.write(b'J\xE6\r')
            case 100:
                self.ser.write(b'J\xFF\r')
          
             
   
    def set_tune_transmitter_state(self, state):
        print ("Set tune trasnmitter state:", state)
        if state == "TRANSMIT ON":
            # Disable T loop #2\r
            self.ser.write(b'#2\r')
            
            # Disable keep alive
            #self.ser.write(b'#8\r'
            #controller.set_tx_freq(10001500)
          
            print ("Keying Transmitter....")
            #self.ser.write(b'Q\x01\r')
            self.tune_transmitter = "ON"
            self.ser.write(b'Q1\r')
            
        else:
            self.ser.write(b'Q0\r')
            # Disable T loop
            #self.ser.write(b'Q\x02\r')
            # Disable keep alove
            #self.ser.write(b'Q\x08\r')
            self.tune_transmitter = "OFF"
            print ("transmitter off...")
            
    def my_set_agc(self, speed):
        print ("Set AGC speed:", speed)
        if speed == "SLOW":
            self.ser.write(b'G\x31\r')
        elif speed == "MEDIUM":
            self.ser.write(b'G\x32\r')
        elif speed == "FAST":
            self.ser.write(b'G\x33\r')
        else:
            print ("AGC speed set error")
            
    def request_smeter_from_pegasus(self):
        self.ser.write(b'?S\r')
        
    def command_antenna_tuner(self, ant_tuner_command):
        print ("Antenna tuner command = ",ant_tuner_command)
        if ant_tuner_command == "$0\r" or ant_tuner_command =="$1\r":
            self.antenna_auto_tune_in_progress = True
            time.sleep(.1)
            self.ser.write(b'M44\r') # Set mode FM
            self.ser.write(b'#1\r') # enable transmitter
            self.ser.write(b'P%c\r' % 15) # set transmit power low
            self.ser.write(b'Q1\r') # Turn on transmitter
            time.sleep(.1)
            self.ser.write(bytes(ant_tuner_command, 'utf-8'))
            if ant_tuner_command == "$1\r":
                time.sleep(4)
            else:
                time.sleep(.5)
            self.ser.write(b'Q0\r') # Turn off transmitter
            self.set_transmit_power(str(self.transmit_watts_setting)+" watts") # original transmit power
            self.ser.write(self.last_mode) # set the mode to the last mode selected from the web
            self.antenna_auto_tune_in_progress = False
        else:
            self.antenna_tuner_command_submitted = True
            self.ser.write(b'P%c\r' % 15) # set transmit power low
            time.sleep(.1)
            self.ser.write(bytes(ant_tuner_command, 'utf-8'))
            time.sleep(.1)
            self.set_transmit_power(str(self.transmit_watts_setting)+" watts")
            
    def my_antenna_tune_from_memory(self, capacitance, inductance, impedance):
        print ("capacitance = ",capacitance, "inductance = ",inductance)
        self.antenna_auto_tune_in_progress = True
        self.ser.write(b'M44\r') # Set mode FM
        self.ser.write(b'#1\r') # enable transmitter
        self.ser.write(b'P%c\r' % 15) # set transmit power low
        self.ser.write(b'Q1\r') # Turn on transmitter
        time.sleep(.1)
        self.ser.write(b'$0\r'); # set BYPASS
        time.sleep(.1)
        if int(capacitance) == 0 and int(inductance) == 0 and int(impedance) == 0:
            self.ser.write(b'$0\r');
        elif int(impedance) == 1: # 1 means set high impedance
            self.ser.write(b'$7\r'); # set HIGH Z
        else:
            self.ser.write(b'$8\r'); # set low Z
        time.sleep(.1)
        for L in range(1,int(inductance)):
            self.ser.write(b'$5\r') # Raise L by one.
            time.sleep(.02)
            
        for C in range(1,int(capacitance)):
            self.ser.write(b'$3\r') # Raise L by one.
            time.sleep(.02)
         
        self.ser.write(b'Q0\r') # Turn off transmitter
        self.set_transmit_power(str(self.transmit_watts_setting)+" watts") # original transmit power
        self.ser.write(self.last_mode) # set the mode to the last mode selected from the web
        self.antenna_auto_tune_in_progress = False
        
               
        
            
'''
#######################################################################################################
#    Pegasus Server
#######################################################################################################
'''
            
class pegasusConnection(threading.Thread):
    def __init__(self, connection, controller, *args, **kwargs):
        super(pegasusConnection,self).__init__(*args, **kwargs)
        self.connection = connection
        self.controller = controller
        self.daemon = True
        self.start()

    def linesplit(self):
        socket = self.connection
        buffer = socket.recv(4096)
        done = False
        while not done:
            if b'\n' in buffer:
                (line, buffer) = buffer.split(b'\n', 1)
                yield line.strip()
            else:
                more = socket.recv(4096)
                if not more:
                    done = True
                else:
                    buffer = buffer+more
        if buffer:
            yield buffer.strip()

    def run(self):
        try:
            for line in self.linesplit():
                result = self.handle(line.split())
                print (result) 
                #self.connection.sendall(b'%s\n' % result)
                self.connection.sendall(str.encode(result+"\n"))
        finally:
            self.connection.close()

    def handle(self, command):
        try:
            print (type(command))
            print ("command = ",command)
            command[0] = str(command[0], 'utf-8')
            print ("command -> ",command)
            if len(command) == 0:
                return "ERROR"
            print (command[0]) 
            if command[0] == 'ALL' and len(command) == 4:
                # ALL <freq> <mode> <filter>
                self.controller.set_mode(int(command[2]))
                self.controller.set_filter(int(command[3]))
                self.controller.set_freq(int(command[1]))
                return "Done"
            elif command[0] == 'FREQ' and len(command) == 2:
                self.controller.set_freq(int(command[1]))
                return "Done"
            elif command[0] == 'VOL' and len(command) == 2:
                self.controller.set_speaker_volume(int(command[1]))
                return "Done"
            elif command[0] == 'SQUELCH' and len(command) == 2:
                self.controller.set_squelch(int(command[1]))
                return "Done"
            elif command[0] == 'LINEVOL' and len(command) == 2:
                self.controller.set_line_volume(int(command[1]))
                return "Done"
            elif command[0] == 'MODE' and len(command) == 2:
                self.controller.set_mode(int(command[1]))
                return "Done"
            elif command[0] == 'RXFILTER' and len(command) == 2:
                self.controller.set_rx_filter(int(command[1]))
                return "Done"
            elif command[0] == 'TXFILTER' and len(command) == 2:
                self.controller.set_tx_filter(int(command[1]))
                return "Done"
            elif command[0] == 'AGC' and len(command) == 2:
                self.controller.set_agc(int(command[1]))
                return "Done"
            elif command[0] == 'GETMODE':
                if hasattr(self.controller, 'mode'):
                    return str(self.controller.mode)
                else:
                    return 'NA'
            elif command[0] == 'GETFILTER':
                if hasattr(self.controller, 'filter'):
                    return str(self.controller.filter)
                else:
                    return 'NA'
            elif command[0] == 'GETAGC':
                if hasattr(self.controller, 'agc'):
                    return str(self.controller.agc)
                else:
                    return 'NA'
            elif command[0] == 'GETSMETER':
                return str(self.controller.strength) 
            elif command[0] == 'GETVOL':
                if hasattr(self.controller, 'speaker_volume'):
                    return str(self.controller.speaker_volume)
                else:
                    return 'NA'
            elif command[0] == 'GETLINEVOL':
                if hasattr(self.controller, 'line_volume'):
                    return str(self.controller.line_volume)
                else:
                    return 'NA'
            elif command[0] == 'GETFREQ':
                if hasattr(self.controller, 'freq'):
                    return str(self.controller.freq)
                else:
                    return 'NA'
            elif command[0] == 'QUERY' and len(command) == 2:
                self.controller.get_query(command[1].decode("utf-8"))
                if hasattr(self.controller, 'query'):
                    return str(self.controller.query)
                else:
                    return 'NA'
            return "ERROR"
        except:
            return "COMMAND EXCEPTION ILLEGAL COMMAND"

            
           
if __name__ == '__main__':
    
    import optparse
    parser = optparse.OptionParser(
        usage = "%prog [options] device",
        description = "pegasus controller"
    )
    parser.add_option("-p", "--port",
        dest = "local_port",
        action = "store",
        type = "int",
        help = "TCP/IP port",
        default = 4665
    )
    parser.add_option("-s", "--sleep",
        dest = "sleep_time",
        action = "store",
        type = "float",
        help = "Seconds to wait between strength polls",
        default = 0.2
    )
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error('need device as argument, e.g. /dev/tty...')

    controller = PEGASUS(args[0], options.sleep_time)
    # initialize controller
    time.sleep(.1)
    controller.reset_radio()
    controller.set_speaker_volume(0)
    controller.set_mode(PEGASUS.MODE_LSB)
    
    
    
    controller.set_squelch(0)
    time.sleep(.1)
    controller.set_mode(PEGASUS.MODE_LSB)
    time.sleep(.1)
    controller.set_agc(PEGASUS.AGC_MEDIUM)
    time.sleep(.1)
    controller.set_transmit_bandwidth(3900)
    time.sleep(.1)
    controller.set_rx_filter(PEGASUS.RX_FILTERS.index(3000))
    controller.set_tx_filter(PEGASUS.TX_FILTERS.index(3900))
    controller.set_transmit_enable("Enable Transmitter")
    controller.set_transmit_power("5 watts")
    controller.set_mic_gain("100%")
    controller.set_speech_processor_web("80%")
    controller.set_tx_monitor_level("0%")
   
    
    time.sleep(.1)
    controller.set_rx_freq(7250000)
    time.sleep(.1)
    controller.set_tx_freq(7250000)
    time.sleep(.1)
    #controller.set_transmit_bandwidth(3900)
    #time.sleep(1)
    controller.set_line_volume(70)
    time.sleep(.1)
    
    controller.set_cw_sidetone("30%")
    controller.step = 100
    

    '''
    print ("Initialized pegasus '%s'" % args[0])
    

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('', options.local_port))
    srv.listen(1)
    


    print ("Waiting for connections on port %d..." % (options.local_port))
    

    while True:
        try:
            connection, addr = srv.accept()
            connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            c = pegasusConnection(connection, controller)
        except KeyboardInterrupt:
            break
        #except (socket.error, msg):
        except socket.error:
            pass  
    '''      


'''
########################################################################################################
# HTTP 
########################################################################################################
'''

@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/get_smeter', methods=['GET'])
def get_smeter():
    #print ("smeter = ",controller.smeter)
    controller.request_smeter_from_pegasus()
    return jsonify({ "sm" : controller.smeter, "wf" : controller.watts_forward, "wr" : controller.watts_reflected, "vo" : controller.speaker_volume, "fi" : controller.filter_hz, "mo" : controller.mode, "vo" : controller.speaker_volume,\
                    "sq" : controller.squelch_value, "an" : controller.anr_notch_value, "te" : controller.transmit_enable, "tp" : controller.trasmit_power, "tb" : controller.transmit_bandwidth, "mg" : controller.mic_gain,\
                    "sp" : controller.speech_processor, "tm" : controller.tx_monitor, "tt" : controller.tune_transmitter, "cs" : controller.cw_sidetone})
    
    
    '''
     self.transmit_enable = "DISABLED"
        self.trasmit_power = ""
        self.transmit_bandwidth = ""
        self.mic_gain = ""
        self.speech_processor = ""
        self.tx_monitor = ""
        self.tune_transmitter = "OFF"
    '''


@app.route('/set_rx_freq', methods=['GET'])
def set_rx_freq():
    freq = request.args.get('freq', default = 7300000, type = int)
    controller.set_rx_freq(freq)
    return jsonify({ "freq" : freq})


@app.route('/set_tx_freq', methods=['GET'])
def set_tx_freq():
    #freq = request.args.get('freq', default = 7300000, type = int)
    freq = controller.tx_freq
    print ("Set tx frequency = ", freq)
    controller.set_tx_freq(freq)
    return jsonify({ "freq" : freq})

@app.route('/get_freq', methods=['GET'])
def get_freq():
    currentfreq = str(controller.freq)
    if len(currentfreq) == 8:
        mhz = currentfreq[0] + currentfreq[1]
        khz = currentfreq[2]+currentfreq[3]+currentfreq[4]+currentfreq[5]+currentfreq[6]+currentfreq[7]
        decimal_freq = mhz + "." + khz
    elif len(currentfreq) == 7:
        mhz = currentfreq[0]
        khz = currentfreq[1]+currentfreq[2]+currentfreq[3]+currentfreq[4]+currentfreq[5]+currentfreq[6]
        decimal_freq = mhz + "." + khz
    else:
        decimal_freq =  "." + str(controller.freq)
    
    return jsonify({ "freq" : decimal_freq})
    #return jsonify({ "freq" : controller.freq})
    
@app.route('/set_speaker_volume', methods=['GET'])
def set_speaker_volume():
    volume = request.args.get('volume', default = 0, type = int)
    controller.set_speaker_volume(volume)
    return jsonify({ "volume" : volume})

@app.route('/set_relative_volume', methods=['GET'])
def set_relative_volume():
    relative_volume = request.args.get('rv', default = 0, type = int)
    controller.set_relative_volume(relative_volume)
    return jsonify({ "rv" : relative_volume}) 

@app.route('/set_agc', methods=['GET'])
def set_agc():
    speed = request.args.get('speed', default = "SLOW")
    controller.my_set_agc(speed)
    return jsonify({ "speed" : speed})

@app.route('/set_squelch', methods=['GET'])
def set_squelch():
    sunit = request.args.get('sunit', default = "S0")
    controller.set_squelch_web(sunit)
    return jsonify({ "sunit" : sunit})

@app.route('/set_anr_notch', methods=['GET'])
def set_anr_notch():
    state = request.args.get('state', default = "OFF")
    controller.set_anr_notch(state)
    return jsonify({ "state" : state})

    
'''
ASCII ‘0’ (0x30) for AM mode
ASCII ‘1’ (0x31) for USB mode
ASCII '2’ (0x32) for LSB mode
ASCII ‘3’ (0x33) for CW mode
ASCII ‘4’ (0x34) for FM mode
'''   
@app.route('/set_mode', methods=['GET'])
def set_mode():
    mymode = request.args.get('mode', default = 0, type = int)
    controller.set_mode(mymode)  
    return jsonify({ "mode" : mymode})
    
@app.route('/set_step', methods=['GET'])
def set_step():
    controller.step = request.args.get('step', default = 0, type = int)
    return jsonify({ "step" : controller.step })

@app.route('/set_rx_filter', methods=['GET'])    
def set_rx_filter():
    controller.rx_filter = int(request.args.get('rx_filter', default = "3000"))
    controller.filter_value = PEGASUS.RX_FILTERS.index(int(controller.rx_filter))
    controller.set_rx_filter(controller.filter_value)
    return jsonify({ "rx_filter" : controller.rx_filter })

@app.route('/set_tx_filter', methods=['GET'])    
def set_tx_filter():
    controller.tx_filter = int(request.args.get('tx_filter', default = "3000"))
    controller.set_tx_filter(PEGASUS.TX_FILTERS.index(int(controller.tx_filter)))
    return jsonify({ "tx_filter" : controller.rx_filter })

@app.route('/transmit_enable', methods=['GET'])    
def transmit_enable():
    controller.transmit_enable_state = request.args.get('state', default = "Disable Transmitter")
    controller.set_transmit_enable(controller.transmit_enable_state)
    return jsonify({ "state" : controller.transmit_enable_state })

@app.route('/transmit_power', methods=['GET'])    
def set_transmit_power():
    controller.transmit_power = request.args.get('power', default = "1 watts")
    controller.transmit_watts_setting = request.args.get('power', default = "1 watts")
    controller.set_transmit_power(controller.transmit_power)
    return jsonify({ "power" : controller.transmit_power })


@app.route('/transmit_bandwidth', methods=['GET'])    
def set_transmit_bandwidth():
    controller.transmit_bandwidth = request.args.get('bandwidth', default = 3900, type=int)
    print ("bandwidth from web = ",controller.transmit_bandwidth)
    controller.set_transmit_bandwidth(controller.transmit_bandwidth)
    return jsonify({ "bandwidth" : controller.transmit_bandwidth })

@app.route('/mic_gain', methods=['GET'])    
def set_mic_gain():
    controller.mic_gain = request.args.get('percent', default = "60%")
    controller.set_mic_gain(controller.mic_gain)
    #return jsonify({ "percent" : controller.set_mic_gain[:-1] })
    return jsonify({ "percent" : 0 })
    

@app.route('/speech_processor', methods=['GET'])    
def set_speech_processor():
    controller.speech_processor = request.args.get('percent', default = "OFF")
    controller.set_speech_processor_web(controller.speech_processor)
    return jsonify({ "percent" : controller.speech_processor })

@app.route('/cw_sidetone', methods=['GET'])    
def set_cw_sidetone():
    controller.cw_sidetone = request.args.get('percent', default = "0%")
    controller.set_cw_sidetone(controller.cw_sidetone)
    return jsonify({ "cw_sidetone" : controller.cw_sidetone})


@app.route('/tx_monitor', methods=['GET'])    
def set_tx_monitor():
    controller.tx_monitor_level = request.args.get('level', default = "0%")
    controller.set_tx_monitor_level(controller.tx_monitor_level)
    return jsonify({ "rx_filter" : controller.rx_filter })

@app.route('/tune_transmitter', methods=['GET'])    
def set_tune_transmitter():
    controller.tune_transmitter_state = request.args.get('state', default = "TRANSMIT OFF")
    controller.set_tune_transmitter_state(controller.tune_transmitter_state)
    return jsonify({ "state" : controller.tune_transmitter_state })


@app.route('/set_volume_by_knob', methods=['GET'])    
def set_volume_by_knob():
    controller.set_volume_by_knob = request.args.get('set_volume_by_knob', default = "0")
    return jsonify({ "vol_set_by_knob" : controller.set_volume_by_knob })


@app.route('/set_filter_by_knob', methods=['GET'])    
def set_filter_by_knob():
    controller.set_filter_by_knob = request.args.get('set_filter_by_knob', default = "0")
    return jsonify({ "filter_set_by_knob" : controller.set_filter_by_knob })


@app.route('/ant_tuner', methods=['GET'])    
def ant_tuner():
    controller.last_antenna_tuner_command = request.args.get('ant_tuner', default = "$0\r")
    controller.command_antenna_tuner(controller.last_antenna_tuner_command)
    return jsonify({ "ant_tuner" : controller.last_antenna_tuner_command })


@app.route('/ant_tuner_from_memory', methods=['GET'])    
def ant_tuner_from_memory():
    capacitance = request.args.get('capacitance', default = 0)
    inductance =  request.args.get('inductance', default = 0)
    impedance =  request.args.get('impedance', default = 0)
    controller.my_antenna_tune_from_memory(capacitance, inductance, impedance)
    return jsonify({ "capacitance" : capacitance, "inductance" : inductance, "impedance" : impedance })


'''
thr = threading.Thread(target=PEGASUS.read_thread, args=[self])
thr.daemon = True
thr.start()
'''

#while True:
    #pass
      
webbrowser.get().open("http://localhost:8080")

app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
#while True:
    #time.sleep(.01)
    
    
'''
// TT-550 / at-11 internal tuner i/o commands
void RIG_TT550::at11_bypass()
{
        cmd = "$0\r";
        sendCommand(cmd, 0);
        LOG_INFO("%s", info(cmd));
}

void RIG_TT550::at11_autotune()
{
        cmd = "$1\r";
        sendCommand(cmd, 0);
        LOG_INFO("%s", info(cmd));
}

void RIG_TT550::at11_cap_up()
{
        cmd = "$3\r";
        sendCommand(cmd, 0);
        LOG_INFO("%s", info(cmd));
}

void RIG_TT550::at11_cap_dn()
{
        cmd = "$4\r";
        sendCommand(cmd, 0);
        LOG_INFO("%s", info(cmd));
}

void RIG_TT550::at11_ind_up()
{
        cmd = "$5\r";
        sendCommand(cmd, 0);
        LOG_INFO("%s", info(cmd));
}

void RIG_TT550::at11_ind_dn()
{
        cmd = "$6\r";
        sendCommand(cmd, 0);
        LOG_INFO("%s", info(cmd));
}

void RIG_TT550::at11_hiZ()
{
        cmd = "$7\r";
        sendCommand(cmd, 0);
        LOG_INFO("%s", info(cmd));
        
void RIG_TT550::at11_loZ()
{
        cmd = "$8\r";
        sendCommand(cmd, 0);
        LOG_INFO("%s", info(cmd));
}
'''
