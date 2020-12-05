TUNES = {
     "a": [1000, 1400],
     "b": [1200, 1400]
}

class TuneList:

    def isTune(self, pitchList):
        for key, value in TUNES.items():
            for i in range(len(pitchList)):
                if(pitchList[i] == value[0] and (value[1] in pitchList[i:])):
                    return True
        return False

