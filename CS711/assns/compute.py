"""Midsem Programming Assignment submission: GroupID-7"""

# DO NOT CHANGE THE NAME OF THIS SCRIPT

import numpy as np
import copy
# DO NOT IMPORT ANY GAME THEORY RELATED PACKAGES

# DO NOT CHANGE THE NAME OF ANY METHOD OR ITS INPUT OUTPUT BEHAVIOR
# INPUT CONVENTION
# file_name: Name of the game file either in .efg or .nfg depending on the fuction


#class definitions
# NFG class
class NFG():
  def __init__(self):
    self.gameType = "NFG"
    self.version = 1
    self.isRational = True
    self.name = ""
    self.players = []
    self.strats = []
    self.utils = []

  #preprocess- creates an instance of NFG class, based on input
  def preprocess(self, file_name):
    f = open(file_name, "r")
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
        self.utils = np.fromstring(x, dtype=np.int32, sep = ' ')
        temp = [*self.strats]
        temp.reverse()
        index = [*range(len(self.players)-1,-1,-1),len(self.players)]
        self.utils = self.utils.reshape((*temp, len(self.players))).transpose(*index)

#EFG_general
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

#EFG_first
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

#Node(EFG_general)
class Node(EFG_general):

  def __init__(self, line, prev_action = None):
    self.prev_action = prev_action
    self.children = []
    EFG_general.__init__(self, line)

  def append_child(self, child):
    self.children.append(child)

#Player
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

#SPNE class
class SPNE() :
  def __init__(self, num_players, spne = None):
    if spne is not None:
      self.utilities = spne.utilities # a list containing utility of all the players
      self.player_actions = spne.player_actions # a list of dictionaries (players) where (key : value) refers to the depth and the the actions chosen
    else :
      self.utilities = []
      self.player_actions = []  
      for i in range (num_players):
        self.player_actions.append({})

#BestActions class
class BestActions():
  def __init__(self):
    self.player_utility = 0
    self.possible_actions = []
    self.corresponding_utilities = []

#defining auxiliary functions
# Cartesian Product
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

# function that calls Cartesian product
def Cartesian(list_a, n): 
  
  temp = list_a[0] 
  
  for i in range(1, n): 
    temp = cartesianProduct(temp, list_a[i]) 
    
  return temp 

# function that constructs tree
#for Q4
def construct_tree1(line_index, file_arr, d, players, curr = None):
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
      (i, _) = construct_tree1(i+1, file_arr, d+1, players, child)
    i += 1
  return (i-1, curr)

#for Q5
def construct_tree2(line_index, file_arr, curr = None):
  if curr == None:
    curr = Node(file_arr[line_index])
  i = line_index
  for action in curr.actions:
    child = Node(file_arr[i+1], action)
    curr.append_child(child)
    if (child.node_type == 'p'):
      (i, _) = construct_tree2(i+1, file_arr, child)
    i += 1
  return (i-1, curr)

#traversing the tree
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

#combines actions sets
def combine_action_sets(action_set1, action_set2) :
  action_set = []
  for i in range(len(action_set2)):
    action_set.append({})
    action_set[i] = action_set1[i]
    for k2,v2 in action_set2[i].items():
      action_set[i][k2] = v2
  return action_set

#Backward induction
def BACKWARD_INDUCTION(history, num_players, depth=0):
  list_of_spne = []
  if history.node_type == 't':
    spne = SPNE(num_players)
    spne.utilities = history.util
    list_of_spne.append(spne)
    return list_of_spne
  
  player = int(history.player) - 1
  best_action_set = []
  depth = history.info_set
  
  for action_index, action in enumerate(history.actions) :
    list_of_child_spne = BACKWARD_INDUCTION(history.children[action_index], num_players, depth+1)
    if len(list_of_spne) == 0:
      for s in list_of_child_spne :  
        temp = BestActions()
        temp.player_utility = s.utilities[player]
        temp.possible_actions.append(action)
        temp.corresponding_utilities.append(s.utilities)
        best_action_set.append(temp)
        list_of_spne = list_of_child_spne
    else :
      temp_list_of_spne = []
      temp_best_action_set = []
      for i, s1 in enumerate(list_of_spne) :
        best_action = copy.deepcopy(best_action_set[i])
        for s2 in list_of_child_spne :
          S = SPNE(num_players)
          set1 = copy.deepcopy(s1.player_actions)
          set2 = copy.deepcopy(s2.player_actions)
          S.player_actions = combine_action_sets(set1, set2)
          temp = {}

          u = best_action.player_utility

          if u > s2.utilities[player]:
            S.utilities = list_of_spne[i].utilities
            temp_best_action_set.append(best_action)
          elif u < s2.utilities[player]:
            S.utilities = s2.utilities
            temp = BestActions()
            temp.player_utility = s2.utilities[player]
            temp.possible_actions.append(action)
            temp.corresponding_utilities.append(s2.utilities)
            temp_best_action_set.append(temp) 
          else :
            S.utilities = s2.utilities
            temp = copy.deepcopy(best_action)
            temp.possible_actions.append(action)
            temp.corresponding_utilities.append(s2.utilities)
            temp_best_action_set.append(temp)
          temp_list_of_spne.append(S)
      best_action_set = temp_best_action_set
      list_of_spne = temp_list_of_spne

  temp_spne = []

  for i, spne in enumerate(list_of_spne):
    k = best_action_set[i].player_utility
    if len(best_action_set[i].possible_actions) == 1:
      if depth in spne.player_actions[player]:
        spne.player_actions[player][depth] = best_action_set[i].possible_actions[0]
      else:
        spne.player_actions[player][depth] = best_action_set[i].possible_actions[0]
      temp_spne.append(spne)
      
    else:
      for j, a in enumerate(best_action_set[i].possible_actions):
        spne1 = copy.deepcopy(spne)
        if depth in spne.player_actions[player]:
          spne1.player_actions[player][depth] = a
          spne1.utilities = best_action_set[i].corresponding_utilities[j]
        else:
          spne1.player_actions[player][depth] = a
          spne1.utilities = best_action_set[i].corresponding_utilities[j]
        temp_spne.append(spne1)
  list_of_spne = temp_spne
  return list_of_spne

#QUESTION 1
def computeSDS(file_name):
  nfg_game = NFG()
  nfg_game.preprocess(file_name)

  sds = []
  for i in range(len(nfg_game.players)):
    ut = nfg_game.utils[...,i]
    ut = ut.swapaxes(-1,i).copy(order='C')
    maxx = -1000000000
    maxind = []
    best = -2

    for l,j in enumerate(np.nditer(ut)):
      if maxx == j:
        maxind.append(l%nfg_game.strats[i])
      elif maxx < j:
        maxind = []
        maxind.append(l%nfg_game.strats[i])
        maxx = j

      if l%nfg_game.strats[i] == nfg_game.strats[i] - 1:
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
          
    for k in range(nfg_game.strats[i]):
      if k == best:
        sds.append(1)
      else:
        sds.append(0)

  return sds

#QUESTION 2
def computeWDS(file_name):
  nfg_game = NFG()
  nfg_game.preprocess(file_name)
  
  wds = []
  for i in range(len(nfg_game.players)):
    ut = nfg_game.utils[...,i]
    ut = ut.swapaxes(-1,i).copy(order='C')
    maxx = -1000000000
    maxind = []
    best = set([_ for _ in range(nfg_game.strats[i])])
    for l,j in enumerate(np.nditer(ut)):
      if maxx == j:
        maxind.append(l%nfg_game.strats[i])
      elif maxx < j:
        maxind = []
        maxind.append(l%nfg_game.strats[i])
        maxx = j

      if l%nfg_game.strats[i] == nfg_game.strats[i] - 1:
        best = best.intersection(maxind)
        if len(best) == 0:
          break
        maxx = -1000000000
        maxind = []

    put = -1

    if len(best) == 1:
      put = best.pop()
    for k in range(nfg_game.strats[i]):
      if k == put:
        wds.append(1)
      else:
        wds.append(0)

  return wds

#QUESTION 3
def computePSNE(file_name):
  nfg_game = NFG()
  nfg_game.preprocess(file_name)
  psne = np.zeros_like(nfg_game.utils[...,0])

  for p in range(len(nfg_game.players)) : 

    up = nfg_game.utils[...,p].swapaxes(-1,p)
    maxind =[]
    max = -1000000000
    for i,u in  np.ndenumerate(up) :
      i = list(i)
      i[p],i[-1] = i[-1],i[p]
      if u == max :
        maxind.append(i)

      elif max < u :
        #new max is {u}
        maxind = []
        maxind.append(i)
        #appending {i}  to new array
        max = u

      if i[p] == nfg_game.strats[p] - 1 :
        #maxind is {maxind}
        for ind in maxind :
          #processing {ind} at {psne[tuple(ind)]}
          psne[tuple(ind)]+=1
        
        maxind =[]
        max = -1000000000
  
  src = np.where(psne==len(nfg_game.players))

  for i in range(len(src)) :

    if i == 0 :
      strr = src[i].reshape(-1,1)
    else :
      strr = np.hstack((strr,src[i].reshape(-1,1))) 

  ans = []
  n = len(nfg_game.players)
  for i in strr :
    subpsne = []
    for j in range(len(i)) :
      temp = list(np.zeros(nfg_game.strats[j],dtype=int))
      temp[i[j]] = 1
      subpsne.extend(temp)
    ans.append(subpsne)

  return ans

#QUESTION 4
def efg_NFG(file_name):
    
    file_arr = []
    with open (file_name, 'r') as f:
        for x in f:
            file_arr.append(x)

    first = EFG_first(file_arr[0])
    numPlayers = len(first.player_names)
    players = []

    for i in range (numPlayers):
        temp = Player()
        players.append(temp)

    (_, root) = construct_tree1(2, file_arr, 0, players)

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
    return final_ans

#QUESTION 5
def computeSPNE(file_name):
  file_arr = []
  with open (file_name, 'r') as f:
    for x in f:
      file_arr.append(x)

  first = EFG_first(file_arr[0])
  numPlayers = len(first.player_names)
  player_actions = []

  for i in range (numPlayers):
    player_actions.append({})
  
  (_, root) = construct_tree2(2, file_arr)

  spne = BACKWARD_INDUCTION(root, numPlayers)
  ans = []

  for s in spne:
    player_actions_final = []
    player_actions = s.player_actions
    for i in range (numPlayers):
      player_actions_final.append([])
      num_info_sets = 0
      for k in player_actions[i].keys():
        if k > num_info_sets:
          num_info_sets = k
      for j in range(num_info_sets+1):
        if j in player_actions[i]:
          player_actions_final[i].append(player_actions[i][j])
    ans.append(player_actions_final)
    
  return ans
