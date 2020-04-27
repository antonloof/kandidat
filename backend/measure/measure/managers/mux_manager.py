import pigpio

ENABLE_PIN = 12


class MuxManager:
    def __init__(self, pi):
        self.pi = pi
        self.spi = pi.spi_open(1, 50000, 0)
        self.last_command = None
        self.pi.set_mode(ENABLE_PIN, pigpio.OUTPUT)

    def begin(self):
        self.last_command = MuxCommand(self)
        self.last_command.send()
        self.pi.write(ENABLE_PIN, 1)

    def end(self):
        self.pi.write(ENABLE_PIN, 0)

    def close(self):
        self.pi.spi_close(self.spi)

    def transfer(self, command):
        self.last_command = command
        data = command.data
        bytes = [(data & 0xFF0000) >> 16, (data & 0xFF00) >> 8, data & 0xFF]
        self.pi.spi_write(self.spi, bytes)

    def command(self):
        return MuxCommand(self, self.last_command)

    def swap_voltage(self):
        command = self.command()
        command.vp = self.last_command.vn
        command.vn = self.last_command.vp
        command.send()


class MuxCommand:
    def __init__(self, mux_manager, command=None):
        self.mux_manager = mux_manager
        self.vp = 0
        self.vn = 0
        self.cp = 0
        self.cn = 0
        if command is not None:
            self.vp = command.vp
            self.vn = command.vn
            self.cp = command.cp
            self.cn = command.cn

    @property
    def data(self):
        sel_cs = self.convert(self.cp)
        sel_mn = self.convert(self.vn)
        sel_gs = self.convert(self.cn)
        sel_mp = self.convert(self.vp)

        cs_pos = (0, 1, 2, 3, 4)
        mn_pos = (5, 6, 18, 19, 17)
        gs_pos = (20, 21, 9, 23, 22)
        mp_pos = (10, 11, 12, 14, 13)

        data = self.position_bit(sel_cs, cs_pos)
        data |= self.position_bit(sel_mn, mn_pos)
        data |= self.position_bit(sel_gs, gs_pos)
        data |= self.position_bit(sel_mp, mp_pos)

        return data

    def convert(self, value):
        return ((value % 8) << 3) + (~(value // 8))

    def position_bit(self, value, poss):
        res = 0
        for i, pos in enumerate(poss):
            res |= (value & (1 << i)) << pos
        return res

    def send(self):
        self.mux_manager.transfer(self)
