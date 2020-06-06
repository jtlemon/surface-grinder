from tkinter import *
import configparser
from grbl_stream_class import GrblStream
from grbl_stream_class import GrblSimulate
from SettingsWindowClass import SettingsWindow
import os
from generateCode import GenerateCode
from table_grind import GenerateTableGrind


class SurfaceGrinder:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
        self.feed_speed = self.config.getfloat('grinding settings', 'feedspeed')
        self.step_over = self.config.getfloat('grinding settings', 'stepover')
        self.x_zero_position = self.config.getfloat('zero position', 'xzeroposition')
        self.y_zero_position = self.config.getfloat('zero position', 'yzeroposition')
        self.offset_x = self.config.getfloat('grinding settings', 'xoffset')
        self.offset_y = self.config.getfloat('grinding settings', 'yoffset')
        self.com_port = self.config.get('machine settings', 'grblserialport')
        self.dress_height = self.config.getfloat('wheel dressing', 'zcoord')
        self.spindle_state = False
        try:
            self.grblStream = GrblStream(self.com_port)
        except:
            print('unable to connect to grbl')
            self.grblStream = GrblSimulate()

    def spindle(self):
        if self.spindle_state:
            self.spindle_state = False
            self.grblStream.g_code('m5')
        else:
            self.spindle_state = True
            self.grblStream.g_code('m3s1000')

    def z_step_05(self):
        self.grblStream.g_code('g91')
        self.grblStream.g_code('g0z-.05')
        self.grblStream.g_code('g90')

    def z_step_1(self):
        self.grblStream.g_code('g91')
        self.grblStream.g_code('g0z-.1')
        self.grblStream.g_code('g90')

    def go_to_zero(self):
        self.grblStream.g_code('g90')
        self.grblStream.g_code('g0z0')
        self.grblStream.g_code('g0x0y0')

    def go_to_z(self, entry):
        z = float(go_to_z_entry.get())
        self.grblStream.g_code(f'g0z-{z}')

    def go_to_dressing(self):
        x_coord = self.config.getfloat('wheel dressing', 'xcoord')
        y_coord = self.config.getfloat('wheel dressing', 'ycoord')
        z = float(dress_z_entry.get())
        self.grblStream.g_code('g90')
        self.grblStream.g_code(f'g0z-{z - 10}')
        self.grblStream.g_code(f'g0x-{x_coord}y-{y_coord}')

    def go_to_dressing_z(self, event):
        z = float(dress_z_entry.get())
        self.grblStream.g_code(f'g0z-{z}')

    def dress_wheel(self):
        dress_amount = self.config.getfloat('wheel dressing', 'dressamount')
        dress_height = float(dress_z_entry.get())
        new_height = dress_height + dress_amount
        table_height = self.config.getfloat('machine settings', 'tableheight')
        new_table_height = dress_amount + table_height
        dress_z_entry.delete(0, END)
        dress_z_entry.insert(0, new_height)
        self.config.set('wheel dressing', 'zcoord', str(new_height))
        self.config.set('machine settings', 'tableheight', str(new_table_height))
        self.save_config()
        self.grblStream.g_code('g91')
        self.grblStream.g_code('m3s1000')
        self.grblStream.g_code('g4p2')
        self.grblStream.g_code('g90')
        self.grblStream.g_code(f'g1z-{new_height}f1500')
        self.grblStream.g_code('g91')
        self.grblStream.g_code('g0y-10')
        self.grblStream.g_code('g0y20')
        self.grblStream.g_code('g0y-20')
        self.grblStream.g_code('g0y20')
        self.grblStream.g_code('g0z10')
        self.go_to_dressing()

    def save_config(self):
        with open((os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')), 'w') as configfile:
            self.config.write(configfile)


def my_mainloop():

    main_window.after(50, my_mainloop)


def settings_window():
    SettingsWindow()


def x_grind():
    # self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
    dress_amount = main_app.config.getfloat('wheel dressing', 'dressamount')
    if dress_option.get() == 1:
        print('dressing wheel')
        main_app.go_to_dressing()
        main_app.dress_wheel()
        z = float(go_to_z_entry.get()) + dress_amount
    else:
        print('not dressing wheel')
        z = float(go_to_z_entry.get())
    x = float(x_dim_entry.get())
    y = float(y_dim_entry.get())
    # z = float(go_to_z_entry.get()) + dress_amount
    go_to_z_entry.delete(0, END)
    go_to_z_entry.insert(0, z)
    x_start = float(x_start_entry.get())
    y_start = float(y_start_entry.get())
    x_start_offset = 220
    y_start_offset = 175
    x_calc = x_start - x_start_offset
    y_calc = y_start - y_start_offset
    if x_calc <= 0:
        print('too close to x')
        return
    if y_calc <= 0:
        print('too close to y')
        return

    # generate = GenerateTableGrind(z)

    generate = GenerateCode(x, y, z, x_calc, y_calc)
    f = open('g_code.nc', 'w')
    f.write('\n'.join(map(str, generate.calculate())))
    f.close()
    print(generate)
    g = open('g_code.nc', 'r')
    for line in g:
        l = line.strip()  # Strip all EOL characters for consistency
        main_app.grblStream.g_code(l)
    g.close()
    os.remove('g_code.nc')
    del generate


def center_of_part():
    x = float(x_dim_entry.get())
    y = float(y_dim_entry.get())
    z = float(go_to_z_entry.get())
    x_start = float(x_start_entry.get())
    y_start = float(y_start_entry.get())
    x_start_offset = 220
    y_start_offset = 175
    x_center = x_start - x_start_offset + (x/2)
    y_center = y_start - y_start_offset + (y/2)
    main_app.grblStream.g_code(f'g0x-{x_center}y-{y_center}')
    print('go to center')


def z_down_5():
    z = round((float(go_to_z_entry.get()) + .05), 3)
    go_to_z_entry.delete(0, END)
    go_to_z_entry.insert(0, z)
    main_app.grblStream.g_code(f'g0z-{z}')


def z_down_1():
    z = round((float(go_to_z_entry.get()) + .1), 3)
    go_to_z_entry.delete(0, END)
    go_to_z_entry.insert(0, z)
    main_app.grblStream.g_code(f'g0z-{z}')


def z_down_01():
    z = round((float(go_to_z_entry.get()) + .01), 3)
    go_to_z_entry.delete(0, END)
    go_to_z_entry.insert(0, z)
    main_app.grblStream.g_code(f'g0z-{z}')


def dress_down_5():
    z = round((float(dress_z_entry.get()) + .05), 3)
    dress_z_entry.delete(0, END)
    dress_z_entry.insert(0, z)
    main_app.grblStream.g_code(f'g0z-{z}')


def dress_down_1():
    z = round((float(dress_z_entry.get()) + .1), 3)
    dress_z_entry.delete(0, END)
    dress_z_entry.insert(0, z)
    main_app.grblStream.g_code(f'g0z-{z}')


def dress_down_01():
    z = round((float(dress_z_entry.get()) + .01), 3)
    dress_z_entry.delete(0, END)
    dress_z_entry.insert(0, z)
    main_app.grblStream.g_code(f'g0z-{z}')


def y_grind():
    pass


if __name__ == '__main__':
    main_app = SurfaceGrinder()
    main_window = Tk()
    left_frame = Frame(main_window)
    right_frame = Frame(main_window)
    main_frame = Frame(left_frame)
    settings_frame = Frame(right_frame)
    soft_key_frame = Frame(left_frame)
    set_z_frame = Frame(left_frame)
    dress_wheel_frame = Frame(left_frame)
    dress_option = IntVar()
    dress_option.set(0)
    settings_img = PhotoImage(file=(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'settings_icon.png')))
    settings_button = Button(settings_frame, image=settings_img, command=settings_window)
    reset_img = PhotoImage(file=(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'reset_icon.png')))
    reset_button = Button(settings_frame, image=reset_img, command=main_app.grblStream.reset_and_home)
    spindle_img = PhotoImage(file=(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                'spindle_off_icon_small.png')))
    spindle_button = Button(settings_frame, image=spindle_img, command=main_app.spindle)
    zero_img = PhotoImage(file=(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'zero_icon.png')))
    go_to_zero_button = Button(settings_frame, image=zero_img, command=main_app.go_to_zero)
    dress_wheel_button = Button(dress_wheel_frame, text='Dress wheel', wraplength=120, height=2, width=10,
                                font='calibri 16', command=main_app.dress_wheel)

    main_window_label = Label(main_frame, text='Surface Grinder', width=50)
    start_x_softKey = Button(main_frame, text='Grind along x axis', width=20,
                             height=2, font='calibri 32', command=x_grind)
    start_y_softKey = Button(soft_key_frame, text='Grind along y axis', width=5,
                             height=2, font='calibri 32', command=y_grind)
    go_to_z_label = Label(set_z_frame, text='Z DEPTH: ', anchor='c', width=20)
    go_to_z_entry = Entry(set_z_frame, font='calibri 32', width=6, justify=CENTER)
    go_to_dress_button = Button(dress_wheel_frame, text='Go To Wheel Dresser', wraplength=120, height=2, width=10,
                                font='calibri 16', command=main_app.go_to_dressing)
    dress_z_entry = Entry(dress_wheel_frame, font='calibri 32', width=6, justify=CENTER)
    x_dim_label = Label(soft_key_frame, text='Length of part: ', justify=RIGHT, anchor='e', width=20)
    x_dim_entry = Entry(soft_key_frame)
    y_dim_label = Label(soft_key_frame, text='Width of part: ', justify=RIGHT, anchor='e', width=20)
    y_dim_entry = Entry(soft_key_frame)
    x_start_label = Label(soft_key_frame, text='X start: ', justify=RIGHT, anchor='e', width=20)
    x_start_entry = Entry(soft_key_frame)
    y_start_label = Label(soft_key_frame, text='Y start:', justify=RIGHT, anchor='e', width=20)
    y_start_entry = Entry(soft_key_frame)
    dress_checkbox = Checkbutton(dress_wheel_frame, text='dress between passes', variable=dress_option, onvalue=1,
                                 offvalue=0)
    z_setup_label = Label(set_z_frame, text='Set up Z')
    z_center_button = Button(set_z_frame, text='Go to Center of part', wraplength=120, width=10,
                             height=2, font='calibri 16', command=center_of_part)
    z_step_down_5 = Button(set_z_frame, text='step down .05mm', wraplength=120, height=2, font='calibri 16', width=10,
                           command=z_down_5)
    z_step_down_1 = Button(set_z_frame, text='Step down .1mm', wraplength=120, height=2, font='calibri 16', width=10,
                           command=z_down_1)
    z_step_down_01 = Button(set_z_frame, text='Step down .01mm', wraplength=120, height=2, font='calibri 16', width=10,
                            command=z_down_01)
    dress_step_down_5 = Button(dress_wheel_frame, text='step down .05mm', wraplength=120, height=2, font='calibri 16',
                               width=10, command=dress_down_5)
    dress_step_down_1 = Button(dress_wheel_frame, text='Step down .1mm', wraplength=120, height=2, font='calibri 16',
                               width=10, command=dress_down_1)
    dress_step_down_01 = Button(dress_wheel_frame, text='Step down .01mm', wraplength=120, height=2, font='calibri 16',
                                width=10, command=dress_down_01)

    left_frame.grid(row=0, column=0)
    right_frame.grid(row=0, column=1)
    main_frame.grid(row=0, column=0, rowspan=1, columnspan=2, padx=20, pady=20)
    settings_frame.grid(row=0, column=0, rowspan=2, padx=20, pady=20)
    soft_key_frame.grid(row=1, column=0, padx=20, pady=20)
    dress_wheel_frame.grid(row=1, column=2, padx=20, pady=20)
    set_z_frame.grid(row=1, column=1, padx=20, pady=20)
    settings_button.grid(row=0, column=0, pady=5)
    reset_button.grid(row=1, column=0, pady=5)
    spindle_button.grid(row=2, column=0, pady=5)
    go_to_zero_button.grid(row=3, column=0, pady=5)
    dress_z_entry.grid(row=1, column=0, pady=5)
    dress_wheel_button.grid(row=7, column=0, pady=5)
    go_to_dress_button.grid(row=0, column=0, pady=5)
    dress_checkbox.grid(row=8)
    dress_step_down_1.grid(row=6)
    dress_step_down_5.grid(row=5)
    dress_step_down_01.grid(row=4)

    main_window_label.grid(row=0)
    start_x_softKey.grid(row=1)
    # start_y_softKey.pack(pady=5)
    x_dim_label.grid(row=0, column=0)
    x_dim_entry.grid(row=0, column=1)
    y_dim_label.grid(row=1, column=0)
    y_dim_entry.grid(row=1, column=1, pady=5)
    x_start_label.grid(row=2, column=0)
    x_start_entry.grid(row=2, column=1, pady=5)
    y_start_label.grid(row=3, column=0)
    y_start_entry.grid(row=3, column=1, pady=5)
    go_to_z_label.grid(row=1, column=0)
    go_to_z_entry.grid(row=2, column=0, pady=5)
    z_center_button.grid(row=0, pady=5)
    z_step_down_01.grid(row=4, pady=5)
    z_step_down_5.grid(row=5, pady=5)
    z_step_down_1.grid(row=6, pady=5)
    dress_z_entry.bind('<Return>', main_app.go_to_dressing_z)
    go_to_z_entry.bind('<Return>', main_app.go_to_z)
    x_dim_entry.insert(0, 0)
    y_dim_entry.insert(0, 0)
    x_start_entry.insert(0, 645)
    y_start_entry.insert(0, 300)
    go_to_z_entry.insert(0, 0)
    dress_z_entry.insert(0, main_app.dress_height)
    main_window.title('Surface Grinder')
    main_window.after(0, my_mainloop())
    main_window.mainloop()
