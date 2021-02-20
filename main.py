import random


class CONFIG:
  in_file = 'b.in'
  out_file = 'a.out'

  TEAM_CNT_IND_2 = 0
  TEAM_CNT_IND_3 = 1
  TEAM_CNT_IND_4 = 2

  TEAMS_CNT = [0, 0, 0]

  ingredients = {}

  rm = None

class Pizza:
  def __init__(self, i, ing):
    self.i = i
    self.ing = ing

def team_ind_to_team_people_cnt(team_ind):
  if team_ind < CONFIG.TEAMS_CNT[CONFIG.TEAM_CNT_IND_2]:
    return 2
  if team_ind < CONFIG.TEAMS_CNT[CONFIG.TEAM_CNT_IND_2] + CONFIG.TEAMS_CNT[CONFIG.TEAM_CNT_IND_3]:
    return 3
  return 4


class ResourceManager():
  def __init__(self, pizzas_cnt, teams_cnt):
    self.pizzas_b = [ -1 ] * pizzas_cnt  # -1 FREE -2 PRESERVED
    self.teams_b = [ None ] * teams_cnt 

    self.pizzas = []

    self.random_pizzas = list(range(pizzas_cnt))
    random.shuffle(self.random_pizzas)
    self._random_pizzas_ind = 0

    self.random_teams = list(range(teams_cnt))
    random.shuffle(self.random_teams)
    self._random_teams_ind = 0

    self.free_pizzas = pizzas_cnt
    self.free_teams = teams_cnt
  
  def _get_free_team_id(self):
    while True:
      team_id = self.random_teams[self._random_teams_ind]
      if self.teams_b[team_id] is None:
        return team_id
      self._random_teams_ind += 1
      if self._random_teams_ind == len(self.teams_b):
        self._random_teams_ind = 0

  def _get_free_pizza_id(self):
    while True:
      pizza_id = self.random_pizzas[self._random_pizzas_ind]
      if self.pizzas_b[pizza_id] == -1:
        self.pizzas_b[pizza_id] = -2
        return pizza_id

      self._random_pizzas_ind += 1
      if self._random_pizzas_ind == len(self.pizzas_b):
        self._random_pizzas_ind = 0

  def assign_delivery(self, team_id, pizzas_ids):
    print("ASSIGN: %d %s" %(team_id, pizzas_ids))
    for pizza_id in pizzas_ids:
      self.pizzas_b[pizza_id] = team_id
      self.free_pizzas -= 1
    self.teams_b[team_id] = tuple(pizzas_ids)
    self.free_teams -= 1

  def deassign_delivery(self, team_id):
    pizzas_ids = self.teams_b[team_id]
    print("DeASSIGN: %d %s" %(team_id, pizzas_ids))
    for pizza_id in pizzas_ids:
      self.pizzas_b[pizza_id] = -1
      self.free_pizzas += 1
    self.teams_b[team_id] = None
    self.free_teams += 1

  def add_pizza(self, pizza):
    self.pizzas.append(pizza)

  def random_spread(self):
    while True:
      if self.free_teams == 0:
        return
      
      current_team_id = self._get_free_team_id()
      pizzas_required = team_ind_to_team_people_cnt(current_team_id)
      if self.free_pizzas < pizzas_required:
        return
      pizzas = [self._get_free_pizza_id() for _ in range(pizzas_required)]
      self.assign_delivery(current_team_id, pizzas)
     
  def calc_team_score(self, pizzas_indexes):
    s = set([ing_ind for ind in pizzas_indexes for ing_ind in self.pizzas[ind].ing])
    return len(s)

  def calc_score(self):
    score = 0
    for t_b in self.teams_b:
      if t_b is not None:
        team_score = self.calc_team_score(t_b)
        score += team_score * team_score
    return score

  def print_answer(self):
    delivered_teams_cnt = 0
    for t_b in self.teams_b:
      if t_b is not None:
        delivered_teams_cnt += 1
    print(delivered_teams_cnt)
    for team_ind, t_b in enumerate(self.teams_b):
      if t_b is not None:
        team_people_cnt = team_ind_to_team_people_cnt(team_ind)
        assert(team_people_cnt == len(t_b))

        res = [team_people_cnt] + list(t_b)
        res = [str(e) for e in res]
        line = ' '.join(res)
        print(line)

  def iteratively_update_spread(self):
    a = 0


def read_file():
  with open(CONFIG.in_file, 'r') as f:
    line = f.readline()

    nums = line.strip().split(' ')
    nums = [int(v) for v in nums]
    n, CONFIG.TEAMS_CNT[CONFIG.TEAM_CNT_IND_2], CONFIG.TEAMS_CNT[CONFIG.TEAM_CNT_IND_3], CONFIG.TEAMS_CNT[CONFIG.TEAM_CNT_IND_4] = nums[0], nums[1], nums[2], nums[3]
    CONFIG.rm = ResourceManager(n, sum(CONFIG.TEAMS_CNT))

    for pizza_ind in range(n):
      line = f.readline()
      values = line.strip().split(' ')

      for ing_name in values[1:]:
        if ing_name not in CONFIG.ingredients:
          CONFIG.ingredients[ing_name] = len(CONFIG.ingredients)
        
      ing_indexes = [CONFIG.ingredients[ing_name] for ing_name in values[1:]]
      pizza = Pizza(pizza_ind, ing_indexes)
      CONFIG.rm.add_pizza(pizza)


read_file()
CONFIG.rm.random_spread()
rm.iteratively_update_spread()
print("SCORE: ", CONFIG.rm.calc_score())
CONFIG.rm.print_answer()
