class FileUtil:

    @staticmethod
    def saveToFile(string, filepath):

        with open(filepath, "w") as f:
            f.write(string)



    @staticmethod
    def appendToFile(string, filepath):

        with open(filepath, "a") as f:
            f.write(string)


    @staticmethod
    def readFromFile(filepath):

        file = open(filepath, 'r')
        text = file.read()
        file.close()
        return text