"""
pegasus controller
:copyright: (c) 2013 by Tom van Dijk
:license: BSD, see LICENSE for more details.
"""
import serial
#import io
import threading
import time


class PEGASUS():
    MODE_AM = 0
    MODE_USB = 1
    MODE_LSB = 2
    MODE_CW = 3

    AGC_SLOW = 1
    AGC_MEDIUM = 2
    AGC_FAST = 3

    FILTERS = [
        6000, 5700, 5400, 5100, 4800, 4500, 4200,
        3900, 3600, 3300, 3000, 2850, 2700, 2550,
        2400, 2250, 2100, 1950, 1800, 1650, 1500,
        1350, 1200, 1050, 900, 750, 675, 600,
        525, 450, 375, 330, 300, 8000,]

    def __init__(self, port, sleep_time=0.2):
        self.ser = serial.Serial('/dev/cu.usbserial-AQ00T6NF')
        #self.ser = serial.Serial(port, 57600, timeout=0,parity=serial.PARITY_NONE, rtscts=1, xonxoff=True)

        self.ser.baudrate = 57600
        self.ser.rtscts = True
        self.ser.timeout = 0

        #ser = serial.serial_for_url('\r', timeout=1)
        #sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        
        self.strength = 0
        self.firmware = ''
        
        thr = threading.Thread(target=PEGASUS.read_thread, args=[self])
        thr.daemon = True
        thr.start()
        
        '''
        thr = threading.Thread(target=PEGASUS.strength_thread, args=[self, sleep_time])
        thr.daemon = True
        thr.start()
        '''

        
    def init_radio(self, ser):
        mode = 0
        self.mode = mode
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
        agc = 3
        ser.write(b'\x47%d\x0d' % agc)
        time.sleep(.1)
        rx_filter = 33
        self.rx_filter = rx_filter
        #ser.write(b'\x57%d\r' % rx_filter)
        time.sleep(.1)
       
        #set_freq(ser, mode, 3630000)
        self.set_freq(5000000)
        
            
    def get_line_blocking(self, ser):
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
    
    #def rw_mutex(ser, op, bin_bytes):
    
    def reset_radio(self):
        print ("Sending restart XX to Pegasus...")  
        self.ser.write(b'XX\r') 
        print ("Looking for DSP START or RADIO START...")
        #     force radio restart
 
        while True:
            try:
                myline = self.get_line_blocking(self.ser)
            except:
                print ("read exception: reset radio")
            #print (myline)
            if myline == "    DSP START" or myline == "   RADIO START":
                print ("Got: ",myline)
                if myline == "    DSP START":
                    print ("DSP Start found.. Starting radio...")
                    self.ser.write(b'P1\r')
                    myline = self.get_line_blocking(self.ser)
                elif myline == "   RADIO START":
                    print ("RADIO START FOUND. Doing radio init....")
                    break
                else:
                    self.ser.write(b'XX\r') 
    '''
    Read Thread and Signal strength Thread
    '''
    def read_thread(self):
        #self.ser = serial.Serial('/dev/cu.usbserial-AQ00T6NF')
        #self.ser = serial.Serial(port, 57600, timeout=0,parity=serial.PARITY_NONE, rtscts=1, xonxoff=True)

        #self.ser.baudrate = 57600
        #self.ser.rtscts = True
        #self.ser.timeout = 0
    
        time.sleep(3) # let radio reset
        #self.ser.timeout = 0
        while True:
            try:
                time.sleep(.1)
                self.ser.write(b'?S\r')
                while not self.ser.getCTS():
                    pass
                print(self.get_line_blocking(self.ser))
                while not self.ser.getCTS():
                    pass
                #mystr = self.get_line_blocking(self.ser)
                #print (mystr,"\n")
                #self.handle_response(mystr)
                #print(self.get_line_blocking(self.ser))
            except:
                print ("Read thread exception")
  
    def strength_thread(self, sleep_time):
        time.sleep(3.5) # Let radio reset
        while True:
            #print ("strength thread")
            while not self.ser.getCTS():
                pass
            
            while not self.ser.getCTS():
                pass
           
            #print(self.get_line_blocking(self.ser))
            time.sleep(.5)
            
    '''
    Handle response
    '''

    def handle_response(self, buf):
        try:
            #print ("Handle Response buffer: ",buf)
            #print ("Handle Response buf[0] = ",buf[0])
            
            if buf[0] == 'S':
                buf = buf[1:]
                sunits = buf[:2]
                fractional = buf[-2:]
                #print (sunits+"."+fractional)
                strnum = str(int(sunits,16))+"."+str(int(fractional,16))
                #print (strnum)
                self.strength = float(strnum)
                print (self.strength)
           
            elif buf[0] == ord('\x5a'):
                pass # unrecognized command! (ignore)
            #elif len(buf) > 3 and str(bytearray(buf[:3])) == 'VER':
            elif len(buf) > 3 and buf[:3] == 'VER':
                self.firmware = str(bytearray(buf))
            #elif len(buf) > 3 and str(bytearray(buf[:3])) == 'DSP':
            elif len(buf) > 3 and buf[:3] == 'DSP':
                print ("handle response: Got DSP START")
                pass # power on! (ignore)
            elif len(buf) > 3 and buf[:3] == 'RAD':
                print ("handle response: Got RADIO START")
                pass # power on! (ignore)
            else:
                pass # unknown response! (ignore)
        except:
            print ("Handle Response - exception !")

    def set_freq(self, freq, cwbfo=0):
        print ("Set Frequency: ",freq)
        assert hasattr(self, 'mode')
        assert hasattr(self, 'rx_filter')

        if self.mode != PEGASUS.MODE_CW: 
            cwbfo = 0

        mcor = [0, 1, -1, -1][self.mode]
        fcor = PEGASUS.FILTERS[self.rx_filter]/2+200

        adjusted_freq = freq - 1250 + mcor*(fcor+cwbfo)

        coarse = int(18000 + (adjusted_freq // 2500))
        fine = int(5.46 * (adjusted_freq % 2500))
        bfo = int(2.73 * (fcor+cwbfo+8000))
        self.set_tuning(coarse, fine, bfo)

        self.freq = freq
        self.cwbfo = cwbfo

    def set_tuning(self, coarse, fine, bfo):
        print ("Set tuning - coarse:",coarse, "fine",fine, "bfo: ",bfo)
        assert coarse >= 0 and coarse < 65536
        assert fine >= 0 and fine < 65536
        assert bfo >= 0 and bfo < 65536
        
        self.ser.write(b'\x4e%c%c%c%c%c%c\x0d' % 
                ((coarse>>8)&255, coarse&255, 
                (fine>>8)&255, fine&255, 
                (bfo>>8)&255, bfo&255))
        
        self.coarse = coarse
        self.fine = fine
        self.bfo = bfo

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
        if mode >= 0 and mode <= 4:
            print ("Set mode: ",b'\x4d%d\x0d' % mode)
            self.ser.write(b'\x4d%d\x0d' % mode)
            self.mode = mode

    def set_rx_filter(self, filter):
        if filter >= 0 and filter <= 33:
            print ("rx filter: ",b'\x57%c\x0d' % filter)
            self.ser.write(b'\x57%c\r' % filter)
            self.rx_filter = filter
            
    def set_tx_filter(self, filter):
        if filter >= 0 and filter <= 33:
            print ("set tx_filter :",b'C%c\r' % filter)
            self.ser.write(b'C%c\r' % filter)
            print ("tx filter: ",b'C%c\x0d' % filter)
            self.tx_filter = filter


    def set_line_volume(self, vol):
        if vol < 0: vol = 0
        if vol > 63: vol = 63
        #self.ser.write(b'L' % vol)
        print ("Line volume: ",b'\x43%c\x0d' % vol)
        self.ser.write(b'\x43%c\r' % vol)
        self.line_volume = vol

    def set_speaker_volume(self, vol):
        if vol < 0: vol = 0
        if vol > 254: vol = 254
        #self.ser.write(b'\x56\x00%c\x0d' % vol)
        print ("vol:",b'V%c\r' % vol)
        self.ser.write(b'V%c\r' % vol)
        
        self.speaker_volume = vol
 
    def set_volume(self, vol):
        if vol < 0: vol = 0
        if vol > 63: vol = 63
        print ("Set volume: ",b'\x56%c\x0d' % vol)
        self.ser.write(b'\x56%c\x0d' % vol)
        self.line_volume = vol
        self.speaker_volume = vol
        
    def set_squelch(self, sunits):
        if sunits < 0: sunits = 0
        if sunits > 19: sunits = 19
        #self.ser.write(b'V100\r' % vol)
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
            
           
        
            
            
                
            