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
        temp = [*self.strats]
        temp.reverse()
        index = [*range(len(self.players)-1,-1,-1),len(self.players)]
        self.utils = np.reshape(self.utils, (*temp, len(self.players))).transpose(*index)
        
x = NFG()
x.preprocess("g1.nfg")
        
sdse = []
for i in range(len(x.players)):
  ut = x.utils[...,i]
  ut = ut.swapaxes(-1,i).copy(order='C')
  maxx = -1000000000
  maxind = []
  best = -2
  
  for l,j in enumerate(np.nditer(ut)):
    if maxx == j:
      maxind.append(l%x.strats[i])
    elif maxx < j:
      maxind = []
      maxind.append(l%x.strats[i])
      maxx = j
    
    if l%x.strats[i] == x.strats[i] - 1:
      if len(maxind) != 1:
        break
      else:
        if best == -2:
          best = maxind[0]
        elif best != maxind[0]:
          best = -1
          break
        maxx = -1000000000
        maxind = []

  put = np.zeros(x.strats[i], dtype=np.int8)
  if best >= 0:
    put[best] = 1
  put = list(put)
  for p in put:
    sdse.append(p)

print(sdse)
