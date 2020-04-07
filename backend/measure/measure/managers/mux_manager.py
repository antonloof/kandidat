class MuxManager:
    def __init__(self, pi):
        self.pi = pi
        self.spi = pi.spi_open(1, 50000, 0)
        self.transfer([0, 0, 0])

    def close(self):
        self.pi.spi_close(self.spi)

    def transfer(self, data):
        self.pi.spi_write(self.spi, data)

    def command(self):
        return MuxCommand(self)


class MuxCommand:
    def __init__(self, mux_manager):
        self.mux_manager = mux_manager
        self.data = [0, 0, 0]

    def send(self):
        self.mux_manager.transfer(self.data)

    def set_vp(self, i):
        return self

    def set_vn(self, i):
        return self

    def set_ip(self, i):
        return self

    def set_in(self, i):
        return self
