import copy

class EFG_general:  
  
  def __init__(self, line):
    nline = line.split(' ')
    self.player_name = ''
    self.player = '' # index of the player playing at a node
    self.info_set = '' # number of the information set
    self.actions = [] # name of actions avaliable for player at a node
    self.outcome_num = ''
    self.util = [] # a list containing utilities of all players (valid at terminal node)
    self.node_type = nline[0] # personal or terminal node
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
    print ("nline:", nline)
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
    print (self.player_names)


class Node(EFG_general):

  def __init__(self, line, prev_action = None):
    self.prev_action = prev_action
    self.children = [] # we append whole Nodes over here instead of just actions
    EFG_general.__init__(self, line)

  def append_child(self, child):
    self.children.append(child)

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

# class PlayerActions() : 
#   def __init__(self, num_players=0):
#     self.player_actions = []
#     for i in range(num_players):
#       self.player_actions.append({})

def construct_tree(line_index, file_arr, curr = None):
  if curr == None:
    curr = Node(file_arr[line_index])
  i = line_index
  for action in curr.actions:
    child = Node(file_arr[i+1], action)
    curr.append_child(child)
    if (child.node_type == 'p'):
      (i, _) = construct_tree(i+1, file_arr, child)
    i += 1
  return (i-1, curr)


file_arr = []
with open ('./test3.efg', 'r') as f:
  for x in f:
    file_arr.append(x)

first = EFG_first(file_arr[0])
numPlayers = len(first.player_names)
player_actions = []

for i in range (numPlayers):
  player_actions.append({})

def combine_action_sets(action_set1, action_set2) :
  action_set = []
  for i in range(len(action_set2)):
    action_set.append({})
    if len(action_set1[i]) == 0:
      action_set[i] = action_set2[i]
    elif len(action_set2[i]) == 0:
      action_set[i] = action_set1[i]
    else:
      #general case to be done
      for k2, v2 in action_set2.items():
        if k2 in action_set1:
          for a in v2:
            action_set1[i][k].append(a)
        action_set = action_set1
  return action_set

def BACKWARD_INDUCTION(history, num_players, depth=0):
  # print('entered ', history.player_name, history.actions)
  list_of_spne = []
  if history.node_type == 't':
    spne = SPNE(num_players)
    spne.utilities = history.util
    #spne.player_actions = []
    list_of_spne.append(spne)
    # print('Return utils ', spne.utilities)
    return list_of_spne
  
  player = int(history.player) - 1
  best_action_set = []
  
  for action_index, action in enumerate(history.actions) :
    print('Taking action ', action)
    #print(len(list_of_spne))
    list_of_child_spne = BACKWARD_INDUCTION(history.children[action_index], num_players, depth+1)
    #print('size of current spne ',len(list_of_spne))
    if len(list_of_spne) == 0:
      print('Current spne list is empty')
      for s in list_of_child_spne : 
        temp = {}
        #print(player, s.utilities)
        temp[s.utilities[player]] = [action]
        #print('create util, action pair ', temp)
        best_action_set.append(temp)
        #list_of_spne = list_of_child_spne
    
    else :
      temp_list_of_spne = []
      temp_best_action_set = []
      for i, s1 in enumerate(list_of_spne) :
        best_action = best_action_set[i]
        for s2 in list_of_child_spne :
          S = SPNE(num_players)
          S.player_actions = combine_action_sets(s1.player_actions, s2.player_actions)
          #print('Combining ', S.player_actions)
          temp = {}

          u = 1
          for k in best_action_set[i].keys():
            u = k
          if u > s2.utilities[player]:
            temp_best_action_set.append(best_action)
          elif u < s2.utilities[player]:
            temp[s2.utilities[player]] = action
            temp_best_action_set.append(temp) 
          else :
            best_action.append(action)
            temp_best_action_set.append(temp)
          temp_list_of_spne.append(S)
      best_action_set = temp_best_action_set
      list_of_spne = temp_list_of_spne

  temp_spne = []
  for i, spne in enumerate(list_of_spne):
    k = 1
    for i in best_action.keys():
      k  = i
    #k = (best_action.keys())[0]
    if len(best_action[k]) == 1:
      if depth in spne.player_actions[player-1]:
        spne.player_actions[player][depth].append(best_action[k])
      else:
        spne.player_actions[player][depth] = []
        spne.player_actions[player][depth].append(best_action[k])
      temp_spne.append(spne)

    else:
      for a in best_action[k]:
        spne1 = copy.deepcopy(spne)
        if depth in spne.player_actions[player-1]:
          spne1.player_actions[player][depth].append(a)
        else:
          spne1.player_actions[player][depth] = []
          spne1.player_actions[player][depth].append(a)
        temp_spne.append(spne1)
    #del list_of_spne[:]
  list_of_spne = temp_spne

  return list_of_spne
        





# print (file_arr[2])
(_, root) = construct_tree(2, file_arr)

spne = BACKWARD_INDUCTION(root, numPlayers)
print(len(spne))
# player_actions_final = []

# for i in range (numPlayers):
#   player_actions_final.append([])
#   for j in range(4):
#     if j in player_actions[i]:
#       for action in player_actions[i][j]:
#         player_actions_final[i].append(action)
# print(player_actions_final)