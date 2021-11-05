from pcaspy import Driver, SimpleServer

prefix = ""
pvdb = {
    "LA-CN:H1MPS-1:A2Temp2": {"prec": 3, "type": "float"},
}


class myDriver(Driver):
    def __init__(self):
        super(myDriver, self).__init__()

    def read(self, reason):
        return self.getParam(reason)

    def write(self, reason, value):
        self.setParam(reason, value)


if __name__ == "__main__":
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
        server.process(0.1)
