# -*- coding: utf-8 -*-

import io

###############################################################################
class SetOutputEnableMAsk:
    def setOutputEnableMask(self, x):
        return
    def read(self):
        return 99
    def write(self, x):
        return


###############################################################################
class MyFileObject:
    def __init__(self, content):
        self.content = content
        self.pointer = 0

    def read(self, size=-1):
        result = self.content[self.pointer:self.pointer + size]
        self.pointer += len(result)
        return result

    def write(self, data):
        pass

    def seek(self, offset, whence=0):
        if whence == 0:
            self.pointer = offset
        elif whence == 1:
            self.pointer += offset
        elif whence == 2:
            self.pointer = len(self.content) + offset

    def tell(self):
        return self.pointer

    def close(self):
        pass

    def getDigitalPorts(self):
        dp0, dp1, dp2 = SetOutputEnableMAsk(), SetOutputEnableMAsk(), SetOutputEnableMAsk()
        return [dp0, dp1, dp2]

    def getSingleEndedInputs(self):
        return [SetOutputEnableMAsk(), SetOutputEnableMAsk(), SetOutputEnableMAsk(), SetOutputEnableMAsk(),
                SetOutputEnableMAsk(), SetOutputEnableMAsk(), SetOutputEnableMAsk(), SetOutputEnableMAsk(),
                SetOutputEnableMAsk(), SetOutputEnableMAsk(), SetOutputEnableMAsk(), SetOutputEnableMAsk(),
                SetOutputEnableMAsk()
                ]

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # Beispiel-Nutzung:
    content = "-------"
    my_file_object = MyFileObject(content)

    # io.StringIO, um das benutzerdefinierte Objekt mit der open-Funktion zu nutzen
    with io.StringIO(my_file_object.read()) as file:
        file_content = file.read()

    print("Inhalt der Datei:", file_content)