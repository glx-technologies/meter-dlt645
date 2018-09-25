
import serial
import time
import sys

class Channel():
    def __init__(self, port_id='/dev/ttyUSB0', tmo_cnt = 10, wait_for_read = 0.5):
        self.tx_addr = []
        self.tx_ctrl = 0x0
        self.tx_payload = []
        
        self.rx_addr = []
        self.rx_ctrl = 0x0
        self.rx_payload = []
        
        self.tx_frame = []
        self.rx_frame = []
        self.tx_bytes = bytearray()
        self.rx_bytes = bytearray()
        
        self.ser = serial.Serial()
        self.ser.port = port_id
        self.ser.baudrate = 2400
        self.ser.parity = serial.PARITY_EVEN
        self.ser.timeout = 0
        
        self.wait_for_read = wait_for_read 
        self.TIMEOUT_COUNT = tmo_cnt

    def encode(self, addr, ctrl, payload=[]):
        self.tx_addr = addr
        self.tx_ctrl = ctrl
        self.tx_payload = payload
        self.tx_frame = [0xfe, 0xfe, 0x68] + list(reversed(self.tx_addr)) 
        self.tx_frame = self.tx_frame + [0x68, self.tx_ctrl] 
        self.tx_frame = self.tx_frame + [len(self.tx_payload)] + [ ((p + 0x33) & 0xff) for p in self.tx_payload ]
        self.tx_frame = self.tx_frame + [sum(self.tx_frame[2:]) & 0xff] + [0x16]
        self.tx_bytes = bytearray(self.tx_frame) 
    
    def decode(self):
        self.rx_addr = [c for c in self.rx_frame[1:7]]
        self.rx_addr.reverse()
        self.rx_ctrl = self.rx_frame[8]
        self.rx_payload = [ ((p - 0x33) & 0xff) for p in self.rx_frame[10:-2] ]
        
        return ((sum(self.rx_frame[0:-2]) & 0xff) == self.rx_frame[-2])
            
    def print_hex_list(self, frame, endl=1):
        for x in frame:
            sys.stdout.write('%02x ' % (x))
        if endl:
            sys.stdout.write('\n')
    

    def xchg_data(self, verbose=0, retry=4):
        
        if verbose:
            sys.stdout.write('tx_frame   : ')
            self.print_hex_list(self.tx_frame)
            sys.stdout.write('tx_addr    : ')
            self.print_hex_list(self.tx_addr)
            sys.stdout.write('tx_ctrl    : ')
            self.print_hex_list([self.tx_ctrl])
            sys.stdout.write('tx_payload : ')
            self.print_hex_list(self.tx_payload)
       
        n = 0
        rsp = 0
        while ( (n <= retry) and rsp == 0 ):
            if verbose:
                sys.stdout.write('wait...\n')
            n = n + 1
            self.write_frame()
            self.ser.flush()
            time.sleep(self.wait_for_read)
            if retry == 0:
                time.sleep(self.wait_for_read)
            rsp = self.read_frame()
        
        if rsp:
            if self.decode() :
                if verbose:
                    sys.stdout.write('\n')
                    sys.stdout.write('rx_frame   : ')
                    self.print_hex_list(self.rx_frame)
                    sys.stdout.write('rx_addr    : ')
                    self.print_hex_list(self.rx_addr)
                    sys.stdout.write('rx_ctrl    : ')
                    self.print_hex_list([self.rx_ctrl])
                    sys.stdout.write('rx_payload : ')
                    self.print_hex_list(self.rx_payload)
                    sys.stdout.write('\n')
                rsp = 1
            else :
                sys.stdout.write('Failed to decode.\n')
                rsp = 0
        else : 
            sys.stdout.write('*** Fail to read, timeout.\n')
            rsp = 0

        return rsp

    def open(self):
        try:
            self.ser.open()
            return True
        except serial.SerialException:
            return False

    def close(self):
        self.ser.close()


    def write_frame(self):
        return self.ser.write(self.tx_bytes)


    def in_waiting(self):
        return self.ser.inWaiting()

    def print_state(self, st):
        pass #sys.stdout.write(st)

    def read_frame(self):
        tmo_cnt = 0
        self.rx_bytes = bytearray()

        state = 'ST_FSTART'
        state_count = 0
        
        while True :  # only exit if Timeout or finsih the EOF state
            
            if self.in_waiting() == 0 :

                tmo_cnt = tmo_cnt + 1
                if tmo_cnt == self.TIMEOUT_COUNT :
                    #sys.stdout.write("Timeout\n")
                    return 0

                # wait for 250ms before the next check 
                time.sleep(0.25)

            else :

                # some data in read buffer
                tmo_cnt = 0

                read_data = bytearray(self.ser.read())

                for c in read_data:
                    
                    if state == 'ST_FSTART' :
                        self.print_state('ST_FSTART\n')
                        if c == 0x68 :
                            # append the byte to the rx_bytes
                            self.rx_bytes = self.rx_bytes + bytearray([c])
                            state = 'ST_ADDR'
                            state_count = 6    

                    elif state == 'ST_ADDR' :
                        self.print_state('ST_ADDR\n')
                        # append the byte to the rx_bytes
                        self.rx_bytes = self.rx_bytes + bytearray([c])
                        state_count = state_count - 1
                        if state_count == 0 :
                            state = 'ST_SSTART'

                    elif state == 'ST_SSTART' :
                        self.print_state('ST_SSTART\n')
                        # append the byte to the rx_bytes
                        self.rx_bytes = self.rx_bytes + bytearray([c])
                        state = 'ST_CTRL'
                    
                    elif state == 'ST_CTRL' :
                        self.print_state('ST_CTRL\n')
                        # append the byte to the rx_bytes
                        self.rx_bytes = self.rx_bytes + bytearray([c])
                        state = 'ST_LEN'

                    elif state == 'ST_LEN' :
                        self.print_state('ST_LEN\n')
                        # append the byte to the rx_bytes
                        self.rx_bytes = self.rx_bytes + bytearray([c])  
                        if (c > 0):
                            state = 'ST_PAYLOAD'
                            state_count = c
                        else:
                            state = 'ST_CKSUM'

                    elif state == 'ST_PAYLOAD' :
                        self.print_state('ST_PAYLOAD\n')
                        # append the byte to the rx_bytes
                        self.rx_bytes = self.rx_bytes + bytearray([c])
                        state_count = state_count - 1
                        if state_count == 0 :
                            state = 'ST_CKSUM'

                    elif state == 'ST_CKSUM' :
                        self.print_state('ST_CKSUM')
                        # append the byte to the rx_bytes
                        self.rx_bytes = self.rx_bytes + bytearray([c])
                        state = 'ST_EOF'

                    elif state == 'ST_EOF' :
                        self.print_state('ST_EOF\n')
                        self.rx_bytes = self.rx_bytes + bytearray([c])
                        
                        self.rx_frame = [c for c in self.rx_bytes]

                        #sys.stdout.write("^^^^^^^^^^^^^^^^^^^^^^^^^\n")
                        #self.print_hex_list(self.rx_frame)
                        #sys.stdout.write("^^^^^^^^^^^^^^^^^^^^^^^^^\n")
                        
                        return 1
                    



    

