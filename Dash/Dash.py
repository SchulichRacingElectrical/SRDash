import asyncio
from threading import Thread

import datetime
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BoundedNumericProperty
from kivy.lang import Builder
import socket
import json
from kivy.core.window import Window
from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')

#Window.fullscreen = True
# init values
eng_temperature = 99
air_temperature = 99
current_rpm = 999
current_speed = 999
current_gear = 999

Builder.load_file("Dashboard.kv")
"""
################TO DO LIST################
-PUT EVERYTHING IN FUNCTIONS
-GET THE DATA FROM DAQ
-TEST ON RASPERRY PI
-SEE IF SCREEN IS VISIBLE FROM ALL ANGLES
-MAYBE PUT SOME DESIGN PATTERNS
-MAKE IT PRETTIER
-TEST WITH DRIVERS
"""


class Display(Widget):
    # used for the flashing of the rpm
    counter = 0
    shiftIndicator = False

    '''
    ASSIGNING THE DEFUALT VALUES
    MUST BE NUMERICPROPERTY TO WORK WITH KIVY (IDK)
    '''
    rpm = NumericProperty(current_rpm)
    speed = NumericProperty(current_speed)
    gear = NumericProperty(current_gear)
    eng_temp = NumericProperty(eng_temperature)
    air_temp = NumericProperty(air_temperature)

    # This is how to load image file path
    img = StringProperty("green.png")

    glowUp = StringProperty("glow3.jpeg")
    glowDown = StringProperty("glow4.jpeg")
    '''add these for glow later
    Rectangle:
            id: myRect
            size: 760,30
            pos: 20, 500
            source: self.glowUp

        Rectangle:
            id: myRect
            size: 760,25
            pos: 20, 385
            source: self.glowDown    
    '''

    img_size = BoundedNumericProperty(0.9, max=1.0, min=0.1)
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    host = socket.gethostname()
    port = 5001

    buffer_size = 4096

    serverSocket.bind((host, port))
    #serverSocket.listen(1)
    data = {}
    worker_loop = asyncio.new_event_loop()
    def __init__(self, **kwargs):
        # needed for constructor
        super(Display, self).__init__(**kwargs)
        # these two lines needed to use the keyboard and stuff
        self._keyboard = Window.request_keyboard (self._keyboard_closed,self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        # timer just like in java, takes in a function and acts as a independent thread
        Clock.schedule_interval(self.update, 0.01)


        worker = Thread(target=self.start_worker, args=(self.worker_loop,))
        worker.start()

    def _keyboard_closed (self): #also part of the keyboard stuff
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down (self,keyboard,keycode,text,modeifires):
        if keycode[1] == 'q':
            exit()
    def start_worker(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def get_data(self):
        start = datetime.datetime.now()

        # print(self.serverSocket)
        data, server = self.serverSocket.recvfrom(self.buffer_size)
        jdata = json.loads(data.decode('utf-8'))
        self.data = jdata
        #print(datetime.datetime.now() - start)


    def update(self, *args):
        self.worker_loop.call_soon(self.get_data())
        #print(self.data)

        '''
        UPDATING VALUES
        '''
        self.rpm = self.data["rpm"]
        #self.speed = self.data["speed"]
        self.gear = self.data["gear"]
        self.eng_temp = self.data["temp"]
        self.air_temp = self.data["iat"]
        '''
        SHIFT LIGHTS TURN ON
        '''
        if (self.rpm > 10500):
            # now its time for shifting
            shiftIndicator = True
        else:
            shiftIndicator = False

        '''
        FLASHING EFFECT
        '''
        if (shiftIndicator == True):
            if self.counter < 100:
                self.img = "red.jpg"
            else:
                self.img = "blue.jpg"

            # change this to chang the timing of the flashes
            self.counter = self.counter + 20
            if self.counter == 200:
                self.counter = 0

        '''
        ###############################################################################
        TEST ZONE TEST ZONE TEST ZONE TEST ZONE TEST ZONE TEST ZONE TEST ZONE TEST ZONE
        ###############################################################################
        '''

        '''
        Simulate the shifting of gears by resetting everything
        '''
        if (self.rpm >= 12500):
            self.gear = self.gear + 1
            self.rpm = 0
            self.counter = 0
            self.img = "green.png"
            self.shiftIndicator = False


class DashboardApp(App):
    def build(self):
        return Display()


if __name__ == '__main__':
    DashboardApp().run()
