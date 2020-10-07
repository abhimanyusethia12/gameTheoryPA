import numpy as np

class NFG():
  def __init__(self):
    self.gameType = "NFG"
    self.version = 1
    self.isRational = True
    self.name = ""
    self.players = []
    self.strats = []
    self.utils = []

  def preprocess(self, filename):
    f = open(filename, "r")
    for j, x in enumerate(f):
      if j == 0:
        self.name = x[9:-2]

      elif j == 1:
        for i in range(len(x)):
          if x[i] == '{':
            if self.players == []:
              while x[i] != '}':
                i += 1
                if x[i] == '"':
                  playEnd = x.find('"', i+1)
                  self.players.append(x[i+1:playEnd])
                  i = playEnd + 1

            elif self.strats == []:
              stratEnd = x.find('}', i+1)
              temp = x[i+1:stratEnd]
              self.strats = list(map(int, temp.split()))
              i = stratEnd + 1 
            
      else:
        self.utils = list(map(int, x.split()))

        print(self.utils)
        temp = [*self.strats]
        temp[0] = self.strats[-1]
        temp[-1] = self.strats[0]
        self.utils = np.reshape(self.utils, (*temp, len(self.players))).swapaxes(0,-2) 
