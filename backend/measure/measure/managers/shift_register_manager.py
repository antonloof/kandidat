class ShiftRegisterManager:
    def __init__(self, pi, data):
        self.pi = pi
        self.spi = pi.spi_open(1, 50000, 0)
        self.data = data
        self.transfer()

    def close(self):
        self.pi.spi_close(self.spi)

    def transfer(self):
        self.pi.spi_write(self.spi, self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.transfer()
