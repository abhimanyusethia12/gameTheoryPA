# with open ('./test1.efg', 'r') as f:
#   for x in f:
#     print (x)

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

# Testing

# with open ('/test1.efg', 'r') as f:    
#   obj1 = EFG_first(f.readline())
#   print (obj1.game_name, obj1.player_names)
#   f.readline()
#   obj2 = EFG_general(f.readline())
#   print(obj2.player_name,
#     obj2.player,
#     obj2.info_set,
#     obj2.action,
#     obj2.outcome_num,
#     obj2.util,
#     obj2.node_type)
#   f.readline()
#   obj3 = EFG_general(f.readline())
#   print(obj3.player_name,
#     obj3.player,
#     obj3.info_set,
#     obj3.action,
#     obj3.outcome_num,
#     obj3.util,
#     obj3.node_type)

class Node(EFG_general):

  def __init__(self, line, prev_action = None):
    self.prev_action = prev_action
    self.children = []
    EFG_general.__init__(self, line)

  def append_child(self, child):
    self.children.append(child)

def construct_tree(line_index, file_arr, curr = None):
  if curr == None:
    curr = Node(file_arr[line_index])
  i = line_index
  # print (i)
  for action in curr.actions:
    child = Node(file_arr[i+1], action)
    # print (child.util)
    curr.append_child(child)
    if (child.node_type == 'p'):
      (i, _) = construct_tree(i+1, file_arr, child)
    i += 1
  # print (curr.children)
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

def backward_induction(history, depth = 0) :
  if history.node_type == 't':
    return history.util, history.prev_action
  
  player = int(history.player)
  best_util = -1000000000000
  best_action = history.actions[0]
  i = 0
  for a in history.actions :
    utils_at_child, _ = backward_induction(history.children[i], depth+1)
    if utils_at_child[player-1] > best_util :
      best_util = utils_at_child[player-1]
      best_action = a
      best_utils =  utils_at_child
    i += 1
  #print(best_utils, best_action)
  if depth in player_actions[player-1]:
    player_actions[player-1][depth].append(best_action)
  else:
    player_actions[player-1][depth] = []
    player_actions[player-1][depth].append(best_action)

  return best_utils, best_action


# print (file_arr[2])
(_, root) = construct_tree(2, file_arr)

backward_induction(root)
player_actions_final = []

for i in range (numPlayers):
  player_actions_final.append([])
  for j in range(4):
    if j in player_actions[i]:
      for action in player_actions[i][j]:
        player_actions_final[i].append(action)
      #player_actions_final[i].append(elem for elem in player_actions[i][j])
      # player_actions_final[i] += player_actions[i][j]
print(player_actions_final)