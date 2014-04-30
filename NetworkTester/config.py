"""

"""

import os, time

class Config(object):
    def __init__(self, inipath):
        """
        inipath = path where to store .ini file
        """
        self.inipath = inipath
        self.logpath = os.path.join(self.inipath, 'Log')
        paths = [self.inipath, self.logpath]
        for path in paths:
            if not os.path.exists(path):
                try:
                    os.mkdir(path)
                    print("{0} created.".format(path))
                except os.error as err:
                    print("Could not create {0}: {1} ".format(path, err))
        # Create .ini
        if os.path.exists(self.inipath):
            self.inifile = os.path.join(self.inipath, "setup.ini")
            if not os.path.exists(self.inifile):
                with open(self.inifile, 'wt') as self.ini:
                    self.ini.write("[SERVERS] (1 or more, separated by carriage returns)\nmyserver\nmyserver2\n"
                                   "[WEBSITE] (1 max, must start with 'http')\nhttp://mywebsite\n")
                    print("Ini file created in: {0}".format(self.inifile))

    def __str__(self):
        return "IO handler for {0}".format(self.inifile)

    def read(self):
        servers = []
        website = ''
        try:
            with open(self.inifile, 'r') as file:
                file = file.readlines()
                for line in file:
                    if line.startswith('http'):
                        website = str(line.rstrip())
                    else:
                        if (len(line) > 5 and not line.startswith('[')):
                            servers.append(str(line.rstrip()))
                return servers, website
        except:
            print("Could not read settings from {0}".format(self.inifile))

def main():
    c = Config('C:\\Users\\r\\AppData\\Roaming\\NetworkTester')
    c.read()

if __name__ == '__main__':
    main()



