import numpy as np
import copy

def cartesianProduct(set_a, set_b): 
	result =[] 
	for i in range(0, len(set_a)): 
		for j in range(0, len(set_b)): 

			if type(set_a[i]) != list:		 
				dummy = [set_a[i]] 
				
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
        self.info_sets = {}
        self.dictionary = []

file_arr = []
with open ('./test3.efg', 'r') as f:
  for x in f:
    file_arr.append(x)

first = EFG_first(file_arr[0])
numPlayers = len(first.player_names)
players = []

for i in range (numPlayers):
    temp = Player()
    players.append(temp)

def construct_tree(line_index, file_arr, d, curr = None):
  if curr == None:
    curr = Node(file_arr[line_index])
  i = line_index
  # print (i)
  if curr.node_type == 'p':
        curr_player = int(curr.player)-1
        curr_infoset = curr.info_set
        curr_depth = d
        if curr_depth in players[curr_player].info_sets:
            if len((players[curr_player].info_sets)[curr_depth]) < curr_infoset:
                lis = []
                for x in range (len(curr.actions)):
                  lis.append(x)
                (players[curr_player].info_sets)[curr_depth].append(lis)
        else:
            (players[curr_player].info_sets)[curr_depth] = []
            lis = []
            for x in range (len(curr.actions)):
              lis.append(x)
            (players[curr_player].info_sets)[curr_depth].append(lis)
        curr.info_set = len(players[curr_player].info_sets[curr_depth]) - 1

  for action in curr.actions:
    child = Node(file_arr[i+1], action)
    # print (child.util)
    curr.append_child(child)
    if (child.node_type == 'p'):
      (i, _) = construct_tree(i+1, file_arr, d+1, child)
    i += 1
  # print (curr.children)
  return (i-1, curr)

# print (file_arr[2])
(_, root) = construct_tree(2, file_arr, 0)

## Code for EFG->NFG

for player in players:
    lis = []
    temp1 = player.info_sets
    for x, y in temp1.items():
        for z in y:
            lis.append(z)
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

for player in players:
  print (player.info_sets)

# def tree_traversal(curr, depth, history = None):
#   if curr.node_type == 't':
#     # do stuff

#   curr_player = curr.player
#   actions = curr.actions
#   for a in actions:
#     new_history = history.append()

def dfs(history, depth, player_actions) :
  #print(player_actions)
  if history.node_type == 't':
    indices = []
    for i in range (numPlayers):
      temp_list = []
      actions = player_actions[i]
      #print (actions, i)
      curr_player = players[i]
      max_height = max(curr_player.info_sets.keys())
      info_sets = curr_player.info_sets
      #print (curr_player, info_sets)
      for d in range(max_height+1):
        if d in actions:
          (a, info_num) = actions[d][0]
          if d in info_sets:
            for j in range (len(info_sets[d])):
              if (j == info_num):
                temp_list.append([a])
              else:
                temp_list.append(info_sets[d][j])
          #print (temp_list, "if")
        else:
          if d in info_sets:
            for j in range (len(info_sets[d])):
              temp_list.append(info_sets[d][j])
        #print(temp_list, "else")
      if len(temp_list) == 1:
        lis1 = temp_list[0]
        temp = []
        for i in lis1:
          temp.append(str(i))
        final_list = temp
        small_indices = []
        for seq in final_list:
          small_indices.append(curr_player.dictionary.index(seq))
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
          small_indices.append(curr_player.dictionary.index(seq))
        indices.append(small_indices)
    
    final_indices = Cartesian(indices, len(indices))
    print (final_indices)
  else:
    player = int(history.player)
    for i,a in enumerate(history.actions):
      cpy = copy.deepcopy(player_actions)
      if depth in player_actions[player-1]:
        cpy[player-1][depth].append((i, history.info_set))
      else:
        cpy[player-1][depth] = []
        cpy[player-1][depth].append((i, history.info_set))
      if i < len(history.children):
        dfs(history.children[i], depth+1, cpy)

player_actions = []

for i in range(numPlayers):
  player_actions.append({})

dfs(root, 0, player_actions)
