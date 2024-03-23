import csv
import copy
import time
import sys
import os
import math
import random

class State:
    # stores all the information needed for states
    def __init__(self, position, c_onboard=0, n_onboard=0, remaining_energy=0, patients_to_pick=[], parent=None, g=0, h=0, f=0):
        self.position = position
        # number of contagious onboard
        self.c_onboard = c_onboard
        # number of noncontagious onboard
        self.n_onboard = n_onboard
        # number of noncontagious onboard
        self.remaining_energy = remaining_energy
        # waiting patients
        self.patients_to_pick = patients_to_pick
        self.parent = parent
        self.g = g
        self.h = h
        self.f = f

    def __lt__(self, other):
        return self.f < other.f
    def __hash__(self):
        # to compare states
        return hash("".join([str(self.position),str(self.patients_to_pick),str(self.c_onboard),str(self.n_onboard)]))

# set full energy
max_e = 50

def parse_map(file_path):
    map_data = []
    with open(file_path, newline='') as csvfile:
        map_reader = csv.reader(csvfile, delimiter=';')
        for row in map_reader:
            # convert numeric strings to integers for energy costs
            processed_row = [int(cell) if cell.isdigit() else cell for cell in row]
            map_data.append(processed_row)
    return map_data
def find_patients(map_data):
    # vector of patients with their type and positions
    patients = []
    for x, row in enumerate(map_data):
        for y, cell in enumerate(row):
            if cell in ['N', 'C']:
                patients.append((cell, (x, y)))
    patients.sort(key=lambda x: x[0], reverse=True)
    return patients
def get_energy_cost(x,y, map_data):
    e = map_data[x][y]
    # makes the energy cost of alphabet letter cells 1
    return 1 if isinstance(e, str) else int(e)
def can_pickup_patient(state, patient_type):
    if patient_type not in ['N', 'C']:
        return False
    waiting = any(p[1] == state.position for p in state.patients_to_pick)
    if waiting == False:
        return False
    total_seats = 10
    if patient_type == 'C':
        # C can board if there are open seats
        return state.c_onboard+state.n_onboard < total_seats 
    else:  # N case
        # N can only board if there are open seats and no C onboard (C always picked up last)
        return state.c_onboard+state.n_onboard < total_seats and state.c_onboard == 0
def can_dropoff_patient(state, care_center_type):
    if care_center_type == 'CC':
        # can only drop off if there are C onboard
        return state.c_onboard > 0
    if care_center_type == 'CN':
        # can only drop off if there are N onboard and no C onboard (C always dropped off first)
        return state.n_onboard > 0 and state.c_onboard == 0 
    return False
def is_goal_state(state, map_data, parking_location):
    # Goal is achieved when all patients have been transported (no patients waiting and none onboard) and vehicle is back at the parking spot
    return state.c_onboard + state.n_onboard == 0 and state.position == parking_location and len(state.patients_to_pick) == 0 

# calculates manhattan distance
def manhattan_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x1 - x2) + abs(y1 - y2)

def heuristic_1(state,parking_location,care_centers,closest_care_center):
    if state.remaining_energy < manhattan_distance(state.position, parking_location):
        # if not enough energy then push system to not expand that node by high f
        return 100000
    # if vehicle only needs to go back to parking to reach goal state
    if state.c_onboard + state.n_onboard + len(state.patients_to_pick)  == 0:
        return manhattan_distance(state.position, parking_location)
    total_distance = 0
    # figures out which patient types in waiting
    patient_types = set ([p[0] for p in state.patients_to_pick])
    # figures out which patient types onboard
    if state.c_onboard > 0:
        patient_types.add('C')
    if state.n_onboard > 0:
        patient_types.add('N')
    # only uses the care centers that match the type of patients needing to be dropped off
    center_locations = [care_centers[t] for t in patient_types]
    # takes all the patients and care centers necessary for current state and puts into list with parking and current position (Critical list)
    unvisited = list(set([p[1]  for p in state.patients_to_pick] + center_locations + [parking_location,state.position]))
    # means vehicle is at goal state
    if len(unvisited) == 1:
        return 0
    # means vehicle only has to go to parking (done with patient transferring)
    if len(unvisited) < 3:
        return manhattan_distance(state.position, parking_location)
    # means vehicle only has to drop off patients(no more waiting patients)
    if len(unvisited) == 3:
        return manhattan_distance(parking_location, center_locations[0])+manhattan_distance(state.position, center_locations[0])
    # select random starting point
    current = random.choice(unvisited)
    unvisited.remove(current)
    while unvisited:
        # find next nearest critical point according to distance from current point
        nearest = min(unvisited, key=lambda point: manhattan_distance(current, point))
        # add the distance from current to nearest, preparing nearest to now be the position of the vehicle
        total_distance += manhattan_distance(current, nearest)
        # set the next nearest point now as the current point
        current = nearest
        # remove current from list
        unvisited.remove(current)
    return total_distance
 
def heuristic_2(state,parking_location,care_centers,closest_care_center):
    if state.remaining_energy < manhattan_distance(state.position, parking_location):
        return 100000
    if state.c_onboard + state.n_onboard + len(state.patients_to_pick)  == 0:
        return manhattan_distance(state.position, parking_location)
    total_distance = 0
    unvisited = list (set([p[1]  for p in state.patients_to_pick ] + [closest_care_center,parking_location,state.position]))
    if len(unvisited) == 1:
        return 0
    if len(unvisited) < 3:
        return manhattan_distance(state.position, parking_location)
    if len(unvisited) == 3:
        return manhattan_distance(parking_location, closest_care_center)+manhattan_distance(state.position, closest_care_center)
    energy = state.remaining_energy
    current = random.choice(unvisited)
    unvisited.remove(current)
    while unvisited:
        nearest = min(unvisited, key=lambda point: manhattan_distance(current, point))
        d = manhattan_distance(current, nearest)+manhattan_distance(nearest,parking_location)
        # ensure enough energy to go to the next critical point but also return to parking from said critical point
        # else, return to parking first and set parking as the current point
        if d > energy:
            total_distance += manhattan_distance(current, parking_location)
            current = parking_location
            energy = max_e
        # add distance to nearest point from current to total
        total_distance += manhattan_distance(current, nearest)
        # subtract energy it takes to go to nearest
        energy -= manhattan_distance(current, nearest)
        current = nearest
        unvisited.remove(current)
    return total_distance
  
  
class AStarWithBuckets:
    def __init__(self):
        # at least the test cases I'm running, f value will never get to 1000 (usually up to 100 or so)
        self.max_num_buckets = 1000
        self.buckets = [[] for _ in range(self.max_num_buckets)]
        # to maintain minimum f value
        self.min_f = self.max_num_buckets
    def add_bucket_elem(self, e):
        # node f is out of bounds so ignored
        if e.f >= self.max_num_buckets:
            return
        self.min_f = min(self.min_f, e.f)
        # add e to desired bucket 
        if not self.buckets[e.f]:
            self.buckets[e.f]=[e]
        else:
            self.buckets[e.f].append(e)
        
    #add child nodes into buckets
    def merge(self, other):
        for f,states in other.items():
            if f >= self.max_num_buckets:
                continue
            self.buckets[f].extend(states)
            self.min_f = min(self.min_f, f)

    def is_empty(self):
        return any(b for b in self.buckets) == False
    
    def pop(self):
        if self.min_f >= self.max_num_buckets:
            return None
        # remove last node in min f val bucket
        result = self.buckets[self.min_f].pop()
        # find next min f
        for bucket in self.buckets[self.min_f:]:
            if bucket:
                self.min_f = bucket[0].f
                return result
        # if couldn't find min f, reset min to invalid
        self.min_f = self.max_num_buckets
        return result
    
def a_star_search(start_state, map_data,parking_location,care_centers,closest_care_center):
    h_funct_name = "heuristic_"+str(sys.argv[2])
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(h_funct_name)
    frontier = AStarWithBuckets()
    # when updating h or g, the f needs be recalculated
    start_state.h = method(start_state, parking_location,care_centers,closest_care_center)
    start_state.f = start_state.h+start_state.g
    frontier.add_bucket_elem(start_state)
    count = 1
    explored = {}
    while not frontier.is_empty():
        current_state = frontier.pop()
        if is_goal_state(current_state, map_data,parking_location):
            return reconstruct_path(current_state), count
        current_hash = hash(current_state)
        # filter out higher f and g val nodes, check if it's already explored
        if current_hash in explored and current_state.f >= explored[current_hash].f and current_state.g >= explored[current_hash].g:
            continue
        # put node in explored
        explored [current_hash] = current_state
        # expand node
        neighbors = {}
        for next_state in get_neighbors(current_state, map_data,parking_location):
            next_state.parent = current_state
            next_state.h = method(next_state, parking_location,care_centers,closest_care_center)
            next_state.f = next_state.g+next_state.h
            has = hash(next_state)
            if has in explored and next_state.h >= explored[has].h and next_state.g >= explored[has].g:
                continue
            if next_state.f in neighbors:
                neighbors[next_state.f].append(next_state)
            else:
                neighbors[next_state.f] = [next_state]
            count += 1
        # add successors to frontier
        frontier.merge(neighbors)
    return None, count

def get_neighbors(state, map_data,parking_location):
    x, y = state.position
    current_cell = map_data[x][y]
    new_state = copy.copy(state)  
    # pick-up actions - considering vehicle capacity and patient type
    if can_pickup_patient(state, current_cell):
        if current_cell == 'C':
            new_state.c_onboard+=1
        else:
            new_state.n_onboard+=1
        # find and remove the patient that got picked up from the list 
        temp = [p for p in new_state.patients_to_pick if p[1] != (x,y)]
        new_state.patients_to_pick = temp
        return [new_state]
    # drop-off actions - contagious patients are dropped off first
    if can_dropoff_patient(state, current_cell):
        if current_cell == 'CC':
            new_state.c_onboard=0
        else:
            new_state.n_onboard=0
        return [new_state]
    if current_cell == 'P' and state.remaining_energy < max_e:
        new_state.remaining_energy = max_e
        return [new_state]
    # movement actions - possible neighbors
    neighbors = []
    max_x, max_y = len(map_data), len(map_data[0])
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Left, Right, Up, Down
        new_x, new_y = x + dx, y + dy
        # ensure neighbors are not out of bounds or untraversable
        if new_x in range(0, max_x) and new_y in range(0, max_y) and map_data[new_x][new_y] != 'X':
            energy_cost = get_energy_cost(new_x, new_y, map_data)
            # ensure enough energy to make that move
            if state.remaining_energy >= energy_cost:
                neighbor = copy.copy(new_state)  
                neighbor.position = (new_x, new_y)
                neighbor.remaining_energy -= energy_cost
                neighbor.g += energy_cost
                neighbors.append(neighbor)
    return neighbors
def reconstruct_path(goal_state):
    path = []
    current_state = goal_state
    while current_state is not None:
        # for pickup, recharge, and dropoff operators, position doesn't change so don't write in path
        if current_state.parent is None or current_state.position != current_state.parent.position:
            path.append(current_state)
        current_state = current_state.parent
    path.reverse()  # path is constructed in reverse order, so we need to reverse it at the end
    return path
def main(map_file_path):
    # parse the map from the file
    map_data = parse_map(map_file_path)
    care_centers = {}
    for x, row in enumerate(map_data):
        for y, cell in enumerate(row):
            if cell == 'C':
                care_centers['C'] = (x, y)
            if cell == 'N':
                care_centers['N'] = (x, y)
            if cell == 'P':
                parking_location = (x, y)
    initial_state = State(
        position=parking_location,
        c_onboard = 0,
        n_onboard = 0,
        remaining_energy=max_e,
        patients_to_pick=find_patients(map_data),
        parent = None,
        g = 0,
        h = 0,
        f = 0
    )    
    closest_care_center = None
    min_dist = float('inf')
    for p in initial_state.patients_to_pick:
        for type, care_center in care_centers.items():
            d = manhattan_distance(p[1], care_center) 
            if d < min_dist:
                min_dist = d
                closest_care_center = care_center
    # run the A* search algorithm
    start=time.time()
    path, count = a_star_search(initial_state, map_data, parking_location,care_centers,closest_care_center)
    end=time.time()
    total_time = end-start
    if path:
        # reconstruct and print the path if a solution is found
        plan_length = 0
        total_cost = path[-1].g
        file_ext = os.path.splitext(sys.argv[1])
        # create a result file
        resultfile= file_ext[0]+'-'+sys.argv[2]+'.output'
        out_file = open(resultfile, 'w')
        # write path into file
        for state in path:
            plan_length+=1
            cell_value = map_data[state.position[0]][state.position[1]]
            out_file.write(str(state.position) + ":" + str(cell_value) + ":" + str(state.remaining_energy)+"\n")
        out_file.close()
        print(f"Data written to {resultfile}")
        # create a stats file
        statsfile= file_ext[0]+'-'+sys.argv[2]+'.stat'
        s_file = open(statsfile, 'w')
        # write state into file
        s_file.write(f"Total time: {float(total_time):.2f}\nPlan length: {plan_length}\nTotal cost: {total_cost}\nExpanded nodes: {count}\n")
        s_file.close()
        print(f"Data written to {statsfile}")
    else:
        print("No solution found.")
if __name__ == "__main__":
    map_file_path = sys.argv[1]
    main(map_file_path)