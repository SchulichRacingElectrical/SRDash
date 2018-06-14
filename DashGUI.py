import traceback
from tkinter import *


class DashGUI:
    def __init__(self, master):
        self.data = None
        # GUI Variables
        self.master = master
        master.title("SR19 GUI")
        master.geometry('{}x{}'.format(800, 480))
        master.resizable(width=False, height=False)
        self.rpmpng = PhotoImage(file="RPM_Gauge.png")
        self.rpmpng_max = PhotoImage(file="RPM_Gauge_red.png")
        self.rpmmax = 12400
        # CONFIGURATION
        self.upperLeftDict = "coolantTemperature"
        self.upperLeftLabel = 'WATER'
        self.upperLeftValue = 0.0
        self.lowerLeftDict = "afr"
        self.lowerLeftLabel = 'AFR'
        self.lowerLeftValue = 0.0
        self.upperCentreDict = "speed"
        self.upperCentreLabel = 'SPEED'
        self.upperCentreValue = 0.0
        self.lowerCentreDict = "battery"
        self.lowerCentreLabel = 'BATT'
        self.lowerCentreValue = 0.0
        self.upperRightDict = "oilTemperature"
        self.upperRightLabel = 'OIL T'
        self.upperRightValue = 0.0
        self.lowerRightDict = "fuelTemp"
        self.lowerRightLabel = 'FUEL T'
        self.lowerRightValue = 0.0

    def init_all_frames(self, master):
        self.masterFrame = Frame(master, width=800, height=480, bd=0, relief=FLAT, background='black')
        self.masterFrame.grid(column=0, row=0, columnspan=3, rowspan=2, sticky=N + E + S + W)

        self.rpmFrame = Frame(self.masterFrame, width=800, height=142, bd=0, relief=FLAT, background='black')
        self.rpmFrame.grid(column=0, row=0, columnspan=3, sticky=W)

        self.canvas = Canvas(self.rpmFrame, width=800, height=142, highlightthickness=0)
        self.canvas.grid(column=0, row=0, columnspan=3, sticky=W)
        self.canvas.create_line(0, 0, 200, 100, fill="red", dash=(4, 4))

        self.leftFrame = Frame(self.masterFrame, bd=0, relief=FLAT, background='black')
        self.leftFrame.grid(column=0, row=1, sticky=W)

        self.centreFrame = Frame(self.masterFrame, bd=0, relief=FLAT, background='black')
        self.centreFrame.grid(column=1, row=1, sticky=W)

        self.rightFrame = Frame(self.masterFrame, bd=0, relief=FLAT, background='black')
        self.rightFrame.grid(column=2, row=1, sticky=W)

        self.bottomFrame = Frame(self.masterFrame, bd=0, relief=FLAT, background='black', highlightthickness=0)
        self.bottomFrame.grid(column=0, row=2, columnspan=3, sticky=W)

    def init_all_dials(self, master):
        width = -1
        height = 1
        font = 'Arial'
        padx = 50
        pady = 5
        smallFontSize = 18
        bigFontSize = 60
        # self.canvas.create_rectangle(0, 0, 800, 40, fill='black')

        self.bottomBar = Button(self.bottomFrame, width=113, height=7, background='black')
        self.bottomBar.grid(column=0, row=0, columnspan=3, sticky=W)

        self.upperLeftLabel = Label(self.leftFrame, text=self.upperLeftLabel, width=width, padx=padx, pady=pady,
                                    background='black',
                                    foreground='white')
        self.upperLeftLabel.grid(column=0, row=0, sticky=W)
        self.upperLeftLabel.config(font=(font, smallFontSize))
        self.upperLeftValue = Label(self.leftFrame, text=self.upperLeftValue, height=height, padx=padx, pady=pady,
                                    background='black',
                                    foreground='white')
        self.upperLeftValue.grid(column=0, row=1, sticky=W)
        self.upperLeftValue.config(font=(font, bigFontSize))

        self.upperCentreLabel = Label(self.centreFrame, text=self.upperCentreLabel, width=width, pady=pady, padx=padx,
                                      background='black',
                                      foreground='white')
        self.upperCentreLabel.grid(column=0, row=0, sticky=N)
        self.upperCentreLabel.config(font=(font, smallFontSize))
        self.upperCentreValue = Label(self.centreFrame, text=self.upperCentreValue, height=height, pady=pady, padx=padx,
                                      background='black',
                                      foreground='white')
        self.upperCentreValue.grid(column=0, row=1, sticky=N)
        self.upperCentreValue.config(font=(font, bigFontSize + 12))

        self.upperRightLabel = Label(self.rightFrame, text=self.upperRightLabel, width=width, padx=padx, pady=pady,
                                     background='black',
                                     foreground='white')
        self.upperRightLabel.grid(column=0, row=0, sticky=E)
        self.upperRightLabel.config(font=(font, smallFontSize))
        self.upperRightValue = Label(self.rightFrame, text=self.upperRightValue, height=height, padx=padx,
                                     pady=pady, background='black', foreground='white')
        self.upperRightValue.grid(column=0, row=1, sticky=E)
        self.upperRightValue.config(font=(font, bigFontSize))

        self.lowerLeftLabel = Label(self.leftFrame, text=self.lowerLeftLabel, width=width, padx=padx, pady=pady,
                                    background='black',
                                    foreground='white')
        self.lowerLeftLabel.grid(column=0, row=2, sticky=W)
        self.lowerLeftLabel.config(font=(font, smallFontSize))
        self.lowerLeftValue = Label(self.leftFrame, text=self.lowerLeftValue, height=height, padx=padx, pady=pady,
                                    background='black',
                                    foreground='white')
        self.lowerLeftValue.grid(column=0, row=3, sticky=W)
        self.lowerLeftValue.config(font=(font, bigFontSize))

        self.lowerCentreLabel = Label(self.centreFrame, text=self.lowerCentreLabel, width=width, padx=padx, pady=pady,
                                      background='black',
                                      foreground='white')
        self.lowerCentreLabel.grid(column=0, row=2, sticky=N)
        self.lowerCentreLabel.config(font=(font, smallFontSize))
        self.lowerCentreValue = Label(self.centreFrame, text=self.lowerCentreValue, height=height, padx=padx, pady=pady,
                                      background='black',
                                      foreground='white')
        self.lowerCentreValue.grid(column=0, row=3, sticky=N)
        self.lowerCentreValue.config(font=(font, bigFontSize))

        self.lowerRightLabel = Label(self.rightFrame, text=self.lowerRightLabel, width=width, padx=padx, pady=pady,
                                     background='black',
                                     foreground='white')
        self.lowerRightLabel.grid(column=0, row=2, sticky=E)
        self.lowerRightLabel.config(font=(font, smallFontSize))
        self.lowerRightValue = Label(self.rightFrame, text=self.lowerRightValue, height=height, padx=padx, pady=pady,
                                     background='black',
                                     foreground='white')
        self.lowerRightValue.grid(column=0, row=3, sticky=E)
        self.lowerRightValue.config(font=(font, bigFontSize))

    def init_rpmbar(self, master):
        self.rpmBarBG = self.canvas.create_rectangle(0, 0, 800, 140, fill='black')
        self.rpmBar = self.canvas.create_rectangle(0, 0, 800, 120, fill='black')
        self.rpmVal = self.canvas.create_text(160, 40, fill='white', font=('arial', 60), text='0')

        # self.rpmBar.grid(column=0, row=0, columnspan=3, sticky=W)
        # self.canvas.tag_lower(self.rpmBar)

    def draw_aesthetics(self, master):
        self.rpmimage = self.canvas.create_image(400, 70, image=self.rpmpng, tags="rpmGauge")
        # self.circle = self.canvas.create_oval(-200, 20, 1600, 160, fill='green', outline='green')
        self.blocker1 = self.canvas.create_rectangle(0, 160, 800, 360, fill='black', outline='black')
        self.canvas.tag_raise(self.rpmBar)
        self.canvas.tag_raise(self.rpmVal)

    def updateRPM(self, value):
        self.canvas.coords(self.rpmBar, round((value * 800 / 12500)), 0, 800, 120)
        # self.rpmVal.text = str(round(value))
        self.canvas.itemconfigure(self.rpmVal, text=str(round(int((value + 50) / 100) * 100)))  # Rounding
        # TODO add blinking lights


    def updateUpLeft(self, value):
        self.upperLeftValue['text'] = round(value)

    def updateLowLeft(self, value):
        self.lowerLeftValue['text'] = round(value, 1)

    def updateUpCen(self, value):
        self.upperCentreValue['text'] = round(value)

    def updateLowCen(self, value):
        self.lowerCentreValue['text'] = round(value, 1)

    def updateUpRight(self, value):
        self.upperRightValue['text'] = round(value)

    def updateLowRight(self, value):
        self.lowerRightValue['text'] = round(value)

    def greet(self):
        print("Greetings!")

    def update(self, data):
        self.updateRPM(data["rpm"])
        self.updateUpLeft(data[self.upperLeftDict])
        self.updateLowLeft(data[self.lowerLeftDict])
        self.updateUpCen(data[self.upperCentreDict])
        self.updateLowCen(data[self.lowerCentreDict])
        self.updateUpRight(data[self.upperRightDict])
        self.updateLowRight(data[self.lowerRightDict])
