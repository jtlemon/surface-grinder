import configparser
import os


class GenerateCode:
    def __init__(self, x, y, z, x_start, y_start):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
        self.feed_speed = self.config.getfloat('grinding settings', 'feedspeed')
        self.step_over = self.config.getfloat('grinding settings', 'stepover')
        self.offset_x = self.config.getfloat('grinding settings', 'xoffset')
        self.offset_y = self.config.getfloat('grinding settings', 'yoffset')
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.x_start = float(x_start)
        self.y_start = float(y_start)
        self.g_code = []

    def calculate(self):

        number_of_passes = round((self.y + self.offset_y) / self.step_over) + 1
        print(f'number of passes : {number_of_passes}')
        length_of_pass = self.x + (self.offset_x * 2)
        print(f'Length of passes: {length_of_pass}')
        self.g_code.append('g90')
        self.g_code.append('m3s1000')
        self.g_code.append('m8')
        self.g_code.append(f'g0x-{self.x_start}y-{self.y_start}')
        self.g_code.append(f'g0z-{self.z}')
        self.g_code.append('g91')
        for each_pass in range(number_of_passes):
            if (each_pass % 2) == 0:
                self.g_code.append(f'g1x-{length_of_pass}f{self.feed_speed}')
            else:
                self.g_code.append(f'g1x{length_of_pass}f{self.feed_speed}')
            self.g_code.append(f'g0y-{self.step_over}')
        self.g_code.append('m5')
        self.g_code.append('m9')
        self.g_code.append('g90')
        self.g_code.append('g0z0')
        self.g_code.append('g0x0y0')
        return self.g_code


if __name__ == '__main__':

    x_length = input('Enter x:')
    y_length = input('Enter y:')
    generate = GenerateCode(x_length, y_length)
    f = open('g_code.nc', 'w')
    f.write('\n'.join(map(str, generate.calculate())))
    f.close()

