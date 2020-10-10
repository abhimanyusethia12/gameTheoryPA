import numpy as np
import copy

def cartesianProduct(set_a, set_b): 
  result =[]
  for i in range(0, len(set_a)): 
    for j in range(0, len(set_b)): 

      if type(set_a[i]) != list:		 
        dummy = [set_a[i]] 
      else:
        dummy = set_a[i]
      temp = [num for num in dummy] 
       
      temp.append(set_b[j])			 
      result.append(temp) 
      
  return result 

def Cartesian(list_a, n): 
  
  temp = list_a[0] 
  
  for i in range(1, n): 
    temp = cartesianProduct(temp, list_a[i]) 
    
  return temp 

class EFG_general:
  
  def __init__(self, line):
    nline = line.split(' ')
    self.player_name = ''
    self.player = ''
    self.info_set = ''
    self.actions = []
    self.outcome_num = ''
    self.util = []
    self.node_type = nline[0]
    if nline[0] == 'p':
      self.player_name = nline[1][1:-1]
      self.player = nline[2]
      self.info_set = int(nline[3])
      self.actions = []
      i = 6
      while (nline[i] != '}'):
        self.actions.append(nline[i][1:-1])
        i += 1
    else:
      self.outcome_num = int(nline[2])
      self.util = []
      temp = nline[5:-1]
      tempstr = ''.join([str(elem) for elem in temp]).split(',')
      for elem in tempstr:
        self.util.append(int(elem))

class EFG_first:

  def __init__(self, line):
    i = 9
    self.game_name = ''
    while (line[i] != '"'):
      self.game_name += line[i]
      i += 1
    nline = line.split(" ")
    self.player_names = []
    for i in range(len(line)):
      if line[i] == '{':
        if self.player_names == []:
          while line[i] != '}':
            i += 1
            if line[i] == '"':
              playEnd = line.find('"', i+1)
              self.player_names.append(line[i+1:playEnd])
              i = playEnd + 1

class Node(EFG_general):

  def __init__(self, line, prev_action = None):
    self.prev_action = prev_action
    self.children = []
    EFG_general.__init__(self, line)

  def append_child(self, child):
    self.children.append(child)

class Player:
    def __init__(self):
        self.num_sets = 0
        self.information_set = []
        self.information_set_sizes = {}
        self.dictionary = []

    def complete_info(self) :
      self.num_sets =  len(self.information_set_sizes)
      for i in range(self.num_sets):
        self.information_set.append(-1)

def construct_tree(line_index, file_arr, d, players, curr = None):
  if curr == None:
    curr = Node(file_arr[line_index])
  i = line_index
  if curr.node_type == 'p':
        curr_player = int(curr.player)-1
        if curr.info_set not in players[curr_player].information_set_sizes:
            players[curr_player].information_set_sizes[curr.info_set - 1] = len(curr.actions)
        
  for action in curr.actions:
    child = Node(file_arr[i+1], action)
    curr.append_child(child)
    if (child.node_type == 'p'):
      (i, _) = construct_tree(i+1, file_arr, d+1, players, child)
    i += 1
  return (i-1, curr)

def dfs(history, depth, numPlayers, players, out) :
  if history.node_type == 't':
    indices = []
    for i in range(numPlayers):
      lis = []
      for j in range(players[i].num_sets):
        if players[i].information_set[j] == -1:
          temp_lis = []
          for k in range(players[i].information_set_sizes[j]):
            temp_lis.append(k)
          lis.append(temp_lis)
        else :
          temp_lis = []
          a = players[i].information_set[j]
          temp_lis.append(a)
          lis.append(temp_lis)

      temp_list = lis
      if len(temp_list) == 1:
        lis1 = temp_list[0]
        temp = []
        for k in lis1:
          temp.append(str(k))
        final_list = temp
        small_indices = []
        for seq in final_list:
          small_indices.append(players[i].dictionary.index(seq))
        indices.append(small_indices)
      else:
        final_list = Cartesian(temp_list, len(temp_list))

        temp = []
        for k in final_list:
            s = ''
            for j in k:
                s += str(j)
            temp.append(s)
        final_list = temp
        small_indices = []
        for seq in final_list:
          small_indices.append(players[i].dictionary.index(seq))
        indices.append(small_indices)
    if len(indices) == 1:
      lis1 = indices
      temp = []
      for i in lis1:
        temp.append([i])
      final_indices = temp
      for elem in final_indices:
        temp1 = out[tuple(elem)]
        temp2 = np.array(history.util)
        out[tuple(elem)] = np.array(history.util)
    else:        
      final_indices = Cartesian(indices, len(indices))
      for elem in final_indices:
        out[tuple(elem)] = np.array(history.util)
  else:
    player = int(history.player) -1 
    if players[player].information_set[history.info_set-1] != -1:
      ai = players[player].information_set[history.info_set-1]
      dfs(history.children[ai], depth+1, numPlayers, players, out)
    else : 

      for i,a in enumerate(history.actions):
        players[player].information_set[history.info_set-1] = i
        dfs(history.children[i], depth+1, numPlayers, players, out)
        players[player].information_set[history.info_set-1] = -1

def efg_NFG(filename):
    
    file_arr = []
    with open (filename, 'r') as f:
        for x in f:
            file_arr.append(x)

    first = EFG_first(file_arr[0])
    numPlayers = len(first.player_names)
    players = []

    for i in range (numPlayers):
        temp = Player()
        players.append(temp)

    (_, root) = construct_tree(2, file_arr, 0, players)

    for player in players:
        player.complete_info()
        lis = []
        for j in range(player.num_sets):
          temp_lis = []
          for k in range(player.information_set_sizes[j]):
            temp_lis.append(k)
          lis.append(temp_lis)

        if len(lis) == 1:
            lis1 = lis[0]
            temp = []
            for i in lis1:
                temp.append(str(i))
            player.dictionary.append(temp)
            player.dictionary = player.dictionary[0]
        else:
            lis1 = Cartesian(lis, len(lis))
            temp = []
            for i in lis1:
                s = ''
                for j in i:
                    s += str(j)
                temp.append(s)
            player.dictionary.append(temp)
            player.dictionary = player.dictionary[0]

    strats = []
    for player in players:
        dim = len(player.dictionary)
        strats.append(dim)

    out = np.zeros((*strats, len(players)), dtype=np.int32)

    dfs(root, 0, numPlayers, players, out)

    idx = [*range(len(players)-1,-1,-1),len(players)]
    out = out.transpose(*idx).reshape((np.prod(strats)*len(players),))

    result = ' '.join(np.array2string(out)[1:-1].split())

    final_ans = []
    string_start = 'NFG 1 R ' + '"' + first.game_name + '"'
    final_ans.append(string_start)
    next = '{ '

    for i in range (numPlayers):
        next += '"' + first.player_names[i] + '" '

    next += '} { '

    for i in strats:
        next += str(i) + ' '

    next += '}'
    final_ans.append(next)
    final_ans.append(result)
    print(final_ans)

efg_NFG('./efg_tests/test5.efg')
