import configparser
import os


class GenerateTableGrind:
    def __init__(self, z):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
        self.feed_speed = self.config.getfloat('grinding settings', 'feedspeed')
        self.step_over = self.config.getfloat('grinding settings', 'stepover')
        self.x_max = self.config.getfloat('machine settings', 'xtravel')
        self.y_max = self.config.getfloat('machine settings', 'ytravel')
        self.table_height = self.config.getfloat('machine settings', 'tableheight')
        self.g_code = []
        self.z = z

    def calculate(self):
        number_of_passes = round((self.y_max / self.step_over) / 2)
        print(f'number of passes: {number_of_passes}')
        self.g_code.append('g90')
        self.g_code.append('m3s1000')
        self.g_code.append(f'f{self.feed_speed}')
        self.g_code.append('m8')
        self.g_code.append('g0x0y0')
        self.g_code.append(f'g0z-{self.z}')
        y = 1.5
        for each_pass in range(number_of_passes):
            self.g_code.append(f'g1x-{self.x_max}')
            self.g_code.append(f'g1y-{y}')
            y = y + self.step_over
            self.g_code.append('g1x0')
            self.g_code.append(f'g1y-{y}')
            y = y + self.step_over

        self.g_code.append('m9m5')
        self.g_code.append('g0z0')



        return self.g_code


if __name__ == '__main__':

    generate = GenerateTableGrind()
    f = open('table_grind_g_code.nc', 'w')
    f.write('\n'.join(map(str, generate.calculate())))
    f.close()
