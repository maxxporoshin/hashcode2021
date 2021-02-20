import random
import argparse


class CONFIG:
  in_file = None
  out_file = None
  in_file_pattern = '../data/%s.in'
  out_file_pattern = '%s.out'

  TEAM_CNT_IND_2 = 0
  TEAM_CNT_IND_3 = 1
  TEAM_CNT_IND_4 = 2

  TEAMS_CNT = [0, 0, 0]

  ingredients = {}

  rm = None

  debug = False


class Pizza:
  def __init__(self, i, ing):
    self.i = i
    self.ing = ing


class Log:
  @staticmethod
  def debug(message):
    if CONFIG.debug:
      print(message)

  @staticmethod
  def info(message):
    print(message)


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
    Log.debug("ASSIGN: %d %s" %(team_id, pizzas_ids))
    for pizza_id in pizzas_ids:
      self.pizzas_b[pizza_id] = team_id
      self.free_pizzas -= 1
    self.teams_b[team_id] = tuple(pizzas_ids)
    self.free_teams -= 1

  def deassign_delivery(self, team_id):
    pizzas_ids = self.teams_b[team_id]
    Log.debug("DeASSIGN: %d %s" %(team_id, pizzas_ids))
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
    Log.info(delivered_teams_cnt)
    for team_ind, t_b in enumerate(self.teams_b):
      if t_b is not None:
        team_people_cnt = team_ind_to_team_people_cnt(team_ind)
        assert(team_people_cnt == len(t_b))

        res = [team_people_cnt] + list(t_b)
        res = [str(e) for e in res]
        line = ' '.join(res)
        Log.info(line)

  def _block_change_pair_operation(self, N, pair_attempts=1):
    teams_ids = [team_id for team_id, t_b in enumerate(self.teams_b) if t_b is not None]

    score_update = 0
    success = 0
    while N > 0:
      cur_team_id_1 = random.choice(teams_ids)
      cur_team_id_2 = random.choice(teams_ids)

      if cur_team_id_1 == cur_team_id_2:
        continue
      
      pizzas_1 = list(self.teams_b[cur_team_id_1])
      pizzas_2 = list(self.teams_b[cur_team_id_2])

      before_score = self.calc_team_score(pizzas_1) + self.calc_team_score(pizzas_2)
      
      results = None
      for _ in range(pair_attempts):
        p_i_1 = random.randrange(0, len(pizzas_1))
        p_i_2 = random.randrange(0, len(pizzas_2))

        t = pizzas_1[p_i_1] 
        pizzas_1[p_i_1] = pizzas_2[p_i_2]
        pizzas_2[p_i_2] = t

        after_score = self.calc_team_score(pizzas_1) + self.calc_team_score(pizzas_2)

        if after_score > before_score:
          if results is None or results[0] < after_score:
            results = (after_score, list(pizzas_1), list(pizzas_2))

        # revert back
        t = pizzas_1[p_i_1] 
        pizzas_1[p_i_1] = pizzas_2[p_i_2]
        pizzas_2[p_i_2] = t
      
      if results is not None:
        (after_score, pizzas_1, pizzas_2) = results
        assert(after_score == self.calc_team_score(pizzas_1) + self.calc_team_score(pizzas_2))

        self.deassign_delivery(cur_team_id_1)
        self.deassign_delivery(cur_team_id_2)
        self.assign_delivery(cur_team_id_1, pizzas_1)
        self.assign_delivery(cur_team_id_2, pizzas_2)
        success += 1
        score_update += after_score - before_score

      N -= 1

    Log.debug("Block change pair: %d teams, %d operations, %d success, +%d score_update" % (len(teams_ids), N, success, score_update))

  def _block_change_new_pizzas_operation(self, N):
    pass


  def iteratively_update_spread(self):
    for _ in range(100):
      self._block_change_pair_operation(100, pair_attempts=2)


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


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Pizza task.')
  parser.add_argument('in_file', type=str, help='name of example')
  parser.add_argument('--debug', action='store_true', help='for debug logs')

  args = parser.parse_args()
  CONFIG.in_file = CONFIG.in_file_pattern % args.in_file
  CONFIG.out_file = CONFIG.out_file_pattern % args.in_file
  CONFIG.debug = args.debug

  read_file()
  CONFIG.rm.random_spread()
  CONFIG.rm.iteratively_update_spread()
  Log.info("SCORE: %d, Free teams: %d, Free pizzas: %d" % (CONFIG.rm.calc_score(), CONFIG.rm.free_teams, CONFIG.rm.free_pizzas))
  CONFIG.rm.print_answer()
