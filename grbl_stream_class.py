"""
Author: Jeremiah Lemon, Jeremy Cornett
Date: 8/23/2019
Purpose: Attempt to use perform GRBL streaming with Python 3. Craft a class around the streaming process. POC.
"""

import time
import serial

# This class needs to be written with a singleton pattern. When the time comes...

# i would like to figure out a way to track machine run time or total distance traveled in x, y and z axis to be able
# to keep track of maintenance intervals still need to add logging to this, also will need to manage cleaning up
# log file??
# if the grbl ever responds with anything but ok, need to stop spindle(m3), release clamp(m9),
# reset(0x18) and home($h).
# probably will need to pop up window notifying user of error and asking for confirmation.


class GrblSimulate:
    def __init__(self):
        pass

    def g_code(self, code):
        print(code)

    def reset_and_home(self):
        print('home')

class GrblStream:
    """A wrapper class around running a GRBL stream."""
    def __init__(self, port):
        self.requested_on_time = time.time()
        self.grbl_out = ''
        # need to add a way to specify which serial port to use.  this should be pulled from the config file
        self.machine_state = 'initializing'
        self.grbl_stream = serial.Serial(port, 115200)
        self.grbl_stream.write(bytes("\r\n\r\n", 'utf-8'))
        time.sleep(2)
        self.grbl_stream.flushInput()
        self.g_code('g4p1')
        self.grbl_state = self.grbl_out
        """
        if self.grbl_state == 'ok\r\n':
            print('homing not required')
                        
        else:
            self.reset_and_home()
            if self.grbl_state == 'ok\r\n':
                print('homing complete')
            else:
                print('unable to home')
                quit()
        """

        self.spindle_state = False
        self.clamp_state = False
        self.machine_state = 'Ready'
        self.g_code('g90g21')
        
    def g_code(self, code):
        """Send a g_code to GRBL.
        :param code: The code to send.
        :type code: str
        :return: None
        """
        self.machine_state = 'Pending'
        self.grbl_stream.write(bytes(code + '\n', 'utf-8'))
        print('sending ' + code, end='')
        self.grbl_out = self.grbl_stream.readline().decode('utf-8')
        print(' : ' + self.grbl_out.strip())
        self.machine_state = 'Ready'
        
    def spindle_on(self):
        """Send the appropriate G-Codes to turn on the spindle.
        :return: None
        """
        # whenever the spindle is requested on reset the timer.
        self.requested_on_time = time.time()
        # if the spindle is not already running
        if not self.spindle_state:
            self.spindle_state = True  # when the spindle is requested on i am setting the state to true
            self.g_code('m4')
            self.g_code('g4 p3')
            # pause to allow the spindle to reach full speed
            # time.sleep(3)
        else:
            # if the spindle is already running do nothing
            print('spindle is already running')

    def spindle_off(self):
        """Send the appropriate G-Codes to turn the spindle off.
        :return: None
        """
        # when the spindle times out i am setting the state to false
        self.spindle_state = False
        self.g_code('m3')

    def clamp_on(self):
        """Send the appropriate G-Codes to turn the clamp on.
        :return: None
        """
        self.clamp_state = True
        self.g_code('m8')
        
    def clamp_off(self):
        """Send the appropriate G-Codes to turn the clamp off.
        :return: None
        """
        self.clamp_state = False
        self.g_code('m9')
        
    def reset_and_home(self):
        self.machine_state = 'Homing'
        print('resetting and homing machine')
        self.grbl_stream.write(0x18)
        time.sleep(2)
        self.g_code('')
        self.g_code('$x')
        self.spindle_off()
        self.clamp_off()
        self.g_code('$h')
        self.g_code('g10 p0 l20 x0 y0 z0')
        self.machine_state = 'Homing Complete-Ready'


def main():
    pass


if __name__ == '__main__':
    main()
