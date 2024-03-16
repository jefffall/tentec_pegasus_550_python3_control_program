import struct
#from bitstring import Bits

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val   

def twos(val_str, bytes):
    import sys
    val = int(val_str, 2)
    b = val.to_bytes(bytes, byteorder=sys.byteorder, signed=False)                                                          
    return int.from_bytes(b, byteorder=sys.byteorder, signed=True)# return positive value as is

def twos_complement(value, bitWidth):
    if value >= 2**bitWidth:
        # This catches when someone tries to give a value that is out of range
        raise ValueError("Value: {} out of range of {}-bit value.".format(value, bitWidth))
    else:
        return value - int((value << 1) & 2**bitWidth)
my16 = struct.pack('BB',0x80,0x01)

print (twos_complement(0x8001,16))
 
#print(my16)

exit(0)

#my16 = struct.pack('BB',buf[1], buf[2])
#myint = struct.unpack('>i',my16)
myint = int.from_bytes(my16, 'big')

print (myint)
print (twos_comp(myint, 16))
exit(0)
myones = ~myint
mytwos = myones + 1
print (myones)
                       
                        
#print(self.signedHex(int(my16,16)))
#print (myint)
#my2comp = ~myint+1
#print (my2comp)
                        
#print (buf[1], buf[2], buf[3])