import traceback
from tkinter import *

rpmmax = 12400
# CONFIGURATION
upperLeftLabel = 'WATER'
upperLeftValue = 0.0
lowerLeftLabel = 'AFR'
lowerLeftValue = 0.0
upperCentreLabel = 'RPM'
upperCentreValue = 0.0
lowerCentreLabel = 'SPEED'
lowerCentreValue = 0.0
upperRightLabel = 'OIL T'
upperRightValue = 0.0
lowerRightLabel = 'FUEL T'
lowerRightValue = 0.0


class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("SR19 GUI")
        master.geometry('{}x{}'.format(800, 480))
        master.resizable(width=False, height=False)

    def init_all_frames(self, master):
        self.masterFrame = Frame(master, width=800, height=480, bd=0, relief=FLAT, background='black')
        self.masterFrame.grid(column=0, row=0, columnspan=3, rowspan=2, sticky=N + E + S + W)

        self.rpmFrame = Frame(self.masterFrame, bd=0, relief=FLAT, background='black')
        self.rpmFrame.grid(column=0, row=0, columnspan=3, sticky=W)

        self.canvas = Canvas(self.rpmFrame, width=800, height=82, highlightthickness=0)
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
        padx = 60
        pady = 5
        smallFontSize = 24
        bigFontSize = 72
        # self.canvas.create_rectangle(0, 0, 800, 40, fill='black')

        self.bottomBar = Button(self.bottomFrame, width=113, height=7, background='black')
        self.bottomBar.grid(column=0, row=0, columnspan=3, sticky=W)

        self.upperLeftLabel = Label(self.leftFrame, text=upperLeftLabel, width=width, padx=padx, pady=pady,
                                    background='black',
                                    foreground='white')
        self.upperLeftLabel.grid(column=0, row=0, sticky=W)
        self.upperLeftLabel.config(font=(font, smallFontSize))
        self.upperLeftValue = Label(self.leftFrame, text=upperLeftValue, height=height, padx=padx, pady=pady,
                                    background='black',
                                    foreground='white')
        self.upperLeftValue.grid(column=0, row=1, sticky=W)
        self.upperLeftValue.config(font=(font, bigFontSize))

        self.upperCentreLabel = Label(self.centreFrame, text=upperCentreLabel, width=width, pady=pady, padx=padx,
                                      background='black',
                                      foreground='white')
        self.upperCentreLabel.grid(column=0, row=0, sticky=N)
        self.upperCentreLabel.config(font=(font, smallFontSize))
        self.upperCentreValue = Label(self.centreFrame, text=upperCentreValue, height=height, pady=pady, padx=padx,
                                      background='black',
                                      foreground='white')
        self.upperCentreValue.grid(column=0, row=1, sticky=N)
        self.upperCentreValue.config(font=(font, bigFontSize))

        self.upperRightLabel = Label(self.rightFrame, text=upperRightLabel, width=width, padx=padx, pady=pady,
                                     background='black',
                                     foreground='white')
        self.upperRightLabel.grid(column=0, row=0, sticky=E)
        self.upperRightLabel.config(font=(font, smallFontSize))
        self.upperRightValue = Label(self.rightFrame, text=upperRightValue, height=height, padx=padx,
                                     pady=pady, background='black', foreground='white')
        self.upperRightValue.grid(column=0, row=1, sticky=E)
        self.upperRightValue.config(font=(font, bigFontSize))

        self.lowerLeftLabel = Label(self.leftFrame, text=lowerLeftLabel, width=width, padx=padx, pady=pady,
                                    background='black',
                                    foreground='white')
        self.lowerLeftLabel.grid(column=0, row=2, sticky=W)
        self.lowerLeftLabel.config(font=(font, smallFontSize))
        self.lowerLeftValue = Label(self.leftFrame, text=lowerLeftValue, height=height, padx=padx, pady=pady,
                                    background='black',
                                    foreground='white')
        self.lowerLeftValue.grid(column=0, row=3, sticky=W)
        self.lowerLeftValue.config(font=(font, bigFontSize))

        self.lowerCentreLabel = Label(self.centreFrame, text=lowerCentreLabel, width=width, padx=padx, pady=pady,
                                      background='black',
                                      foreground='white')
        self.lowerCentreLabel.grid(column=0, row=2, sticky=N)
        self.lowerCentreLabel.config(font=(font, smallFontSize))
        self.lowerCentreValue = Label(self.centreFrame, text=lowerCentreValue, height=height, padx=padx, pady=pady,
                                      background='black',
                                      foreground='white')
        self.lowerCentreValue.grid(column=0, row=3, sticky=N)
        self.lowerCentreValue.config(font=(font, bigFontSize))

        self.lowerRightLabel = Label(self.rightFrame, text=lowerRightLabel, width=width, padx=padx, pady=pady,
                                     background='black',
                                     foreground='white')
        self.lowerRightLabel.grid(column=0, row=2, sticky=E)
        self.lowerRightLabel.config(font=(font, smallFontSize))
        self.lowerRightValue = Label(self.rightFrame, text=lowerRightValue, height=height, padx=padx, pady=pady,
                                     background='black',
                                     foreground='white')
        self.lowerRightValue.grid(column=0, row=3, sticky=E)
        self.lowerRightValue.config(font=(font, bigFontSize))

    def init_rpmbar(self, master):
        self.rpmBarBG = self.canvas.create_rectangle(0, 0, 800, 80, fill='black')
        self.rpmBar = self.canvas.create_rectangle(0,0,800,80, fill='black')

        # self.rpmBar.grid(column=0, row=0, columnspan=3, sticky=W)
        # self.canvas.tag_lower(self.rpmBar)

    def draw_aesthetics(self, master):
        self.circle = self.canvas.create_oval(-200, 20, 1600, 160, fill='green', outline='green')
        self.blocker1 = self.canvas.create_rectangle(0, 80, 800, 360, fill='black', outline='black')
        self.canvas.tag_raise(self.rpmBar)
        self.horizontalRedLine1 = self.canvas.create_line(0,80,800,80,width=5,fill='red')
        self.canvas.tag_raise(self.horizontalRedLine1)


    def rpmupdate(self, rpm):
        if rpm < rpmmax:
            self.canvas.coords(self.rpmBar, round(rpm), 0, round(rpm / 111)+800, 80)
        else:
            self.canvas.coords(self.rpmBar, round(rpmmax), 0, round(rpmmax / 111)+800, 80)

    def greet(self):
        print("Greetings!")


def main():
    root = Tk()
    my_gui = MyFirstGUI(root)
    my_gui.init_all_frames(root)
    my_gui.init_all_dials(root)
    my_gui.init_rpmbar(root)
    my_gui.draw_aesthetics(root)
    rpm = 0
    try:
        while True:
            my_gui.rpmupdate(rpm)
            rpm = rpm + 1
            if rpm >= rpmmax:
                rpm = 0
            root.update()
    except TclError:
        print('TKInter frame closed: {}'.format(traceback.print_exc(file=sys.stdout)))
        exit()


if __name__ == '__main__':
    main()
