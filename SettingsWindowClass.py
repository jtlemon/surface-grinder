from tkinter import *
import configparser
import os


class SettingsWindow:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
        self.feed_speed = self.config.getfloat('grinding settings', 'feedspeed')
        self.step_over = self.config.getfloat('grinding settings', 'stepover')
        self.x_zero_position = self.config.getfloat('zero position', 'xzeroposition')
        self.y_zero_position = self.config.getfloat('zero position', 'yzeroposition')
        self.com_port = self.config.get('machine settings', 'grblserialport')

        self.settings_root = Tk()

        self.feed_speed_label = Label(self.settings_root, text='Feed Speed: ', anchor='e', width=40)
        self.feed_speed_entry = Entry(self.settings_root)
        self.feed_speed_label.grid(row=0, column=0)
        self.feed_speed_entry.grid(row=0, column=1, padx=(0, 10), pady=10)
        self.feed_speed_entry.insert(0, self.feed_speed)

        self.step_over_label = Label(self.settings_root, text='Step Over: ', anchor='e', width=40)
        self.step_over_entry = Entry(self.settings_root)
        self.step_over_label.grid(row=1, column=0)
        self.step_over_entry.grid(row=1, column=1, padx=(0, 10), pady=10)
        self.step_over_entry.insert(0, self.step_over)

        self.x_zero_position_label = Label(self.settings_root, text='X Zero Position: ', anchor='e', width=40)
        self.x_zero_position_entry = Entry(self.settings_root)
        self.x_zero_position_label.grid(row=2, column=0)
        self.x_zero_position_entry.grid(row=2, column=1, padx=(0, 10), pady=10)
        self.x_zero_position_entry.insert(0, self.x_zero_position)

        self.y_zero_position_label = Label(self.settings_root, text='Y Zero Position: ', anchor='e', width=40)
        self.y_zero_position_entry = Entry(self.settings_root)
        self.y_zero_position_label.grid(row=3, column=0)
        self.y_zero_position_entry.grid(row=3, column=1, padx=(0, 10), pady=10)
        self.y_zero_position_entry.insert(0, self.y_zero_position)

        self.com_port_label = Label(self.settings_root, text='Com Port: ', anchor='e', width=40)
        self.com_port_entry = Entry(self.settings_root)
        self.com_port_label.grid(row=4, column=0)
        self.com_port_entry.grid(row=4, column=1, padx=(0, 10), pady=10)
        self.com_port_entry.insert(0, self.com_port)

        self.save_settings_button = Button(self.settings_root, text='Save settings and close',
                                           command=self.close_settings_window, width=50, height=4)
        self.save_settings_button.grid(row=16, column=0, columnspan=2, padx=10, pady=10)

        self.settings_root.title('Settings')

        self.settings_root.mainloop()

    def close_settings_window(self):
        self.config.set('grinding settings', 'feedspeed', self.feed_speed_entry.get())
        self.config.set('grinding settings', 'stepover', self.step_over_entry.get())
        self.config.set('zero position', 'xzeroposition', self.x_zero_position_entry.get())
        self.config.set('zero position', 'yzeroposition', self.y_zero_position_entry.get())
        self.config.set('machine settings', 'grblserialport', self.com_port_entry.get())
        with open((os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')), 'w') as configfile:
            self.config.write(configfile)
        self.settings_root.destroy()


def main():
    SettingsWindow()


if __name__ == '__main__':
    main()
