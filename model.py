from mesa import Agent, Model
import tools

signalCountRequired = 3
class Example(Agent):
    def __init__(self, model = Model(), unique_id = 0, radius = 1.0, color = "#2042FB", pos = (0,0)):
        super().__init__(unique_id, model)
        self.radius = radius
        self.color = color
class Signal(Agent):
    def __init__(self, model = Model() , hash = "",unique_id = 0, radius = 0.2, color = "#FB4720", mobility = 1900, vitality = 20):
        super().__init__(unique_id, model)
        self.radius = radius
        self.color = color
        self.hash = hash
        self.mobility = mobility
        self.vitality = vitality
        self.step_count = 0
    def step(self):           
        self.model.move_agent_randomly_with_probability(self, move_factor = 3)
        self.step_count = self.step_count + 1
        # if self.step_count == 10:
        #     self.mobility = 300
class KillSignal(Agent):
    def __init__(self, model = Model() , hash = "",unique_id = 0, radius = 0.2, color = "#FB6320", mobility = 100, vitality = 20):
        super().__init__(unique_id, model)
        self.radius = radius
        self.color = color
        self.hash = hash
        self.mobility = mobility
        self.vitality = vitality
        self.step_count = 0
    def step(self):           
        self.model.move_agent_randomly_with_probability(self)
        self.step_count = self.step_count + 1
        
        
class Cell(Agent):
    def __init__(self, model = tools.AgentModel(), unique_id = 0, radius = 1.0, color = tools.random_color(), mobility = 1900,vitality = 70 , parent_id = "ABC", level = 6 ):
        super().__init__(unique_id, model)
        self.radius = radius
        self.parent_id = parent_id
        self.color = color # if self.parent_id != "ABC"  else tools.random_color()
        self.mobility = (mobility) * level
        
        self.step_count = 0
        self.level = level
        self.vitality = vitality  if self.parent_id != "ABC" else 100000
        self.last_full_signal_timestamp = tools.current_milli_time()
        self.last_time_I_received_parent_signal_and_attached_my_signature = tools.current_milli_time()
        
    def step(self):
        self.model.move_agent_randomly_with_probability(self)
        if tools.current_milli_time() - self.last_time_I_received_parent_signal_and_attached_my_signature > 12000 and str(self.parent_id) != "ABC":
              self.model.schedule.remove(self)
              self.model.grid.remove_agent(self)
        # tools.reproduce(self, probability=2)
        self.did_i_receive_signal()
        self.send_signal(probability=((self.level+1) ** 3)/50)
        self.step_count = self.step_count + 1
        if self.last_full_signal_timestamp != None and tools.current_milli_time() -  self.last_full_signal_timestamp > 8000:
            tools.reproduce(self, probability=100)
        if self.step_count == 10:
            tools.reproduce(self, probability=self.vitality / 3)
        if self.step_count == 30:
            self.mobility = 300
        #     tools.reproduce(self, probability=self.vitality / 3)
        # if self.step_count == 30:
        #     tools.reproduce(self, probability=self.vitality / 3)
        # if self.step_count == 40:
        #     tools.reproduce(self, probability=100)
        #     self.send_signal(probability=100)
    def custom_move(self):
        """
        Move the agent based on its mobility.
        """

        # Get the current coordinates of the agent.
        x, y = self.pos

        # Calculate the maximum distance the agent can move in one step.
        max_distance = min(self.mobility, self.model.grid.width, self.model.grid.height)

        # Calculate the possible destinations within the maximum distance.
        possible_destinations = []
        for dx in range(-max_distance, max_distance+1):
            for dy in range(-max_distance, max_distance+1):
                distance = abs(dx) + abs(dy)
                if distance <= max_distance and distance > 0:  # Exclude the current cell
                    nx = x + dx
                    ny = y + dy
                    if not self.model.grid.out_of_bounds((nx, ny)) and self.model.grid.is_cell_empty((nx, ny)):
                        possible_destinations.append((nx, ny))

        # Choose a destination randomly from the possible destinations.
        if len(possible_destinations) > 0:
            new_pos = random.choice(possible_destinations)
            self.model.grid.move_agent(self, new_pos)  

                  
    def did_i_receive_signal(self):
        if self.pos is not None:
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                #    if neighbor.__class__.__name__ == "Signal":
                #        print(neighbor)
                if neighbor.__class__.__name__ != "Signal" and  neighbor.__class__.__name__ != "KillSignal": #not a signal
                    continue
                if neighbor.hash.startswith(str(self.parent_id)) and tools.current_milli_time() - self.last_time_I_received_parent_signal_and_attached_my_signature > 60000 and self.parent_id != "ABC":
                        self.model.schedule.remove(self)
                        self.model.grid.remove_agent(self)
                        continue
                    
                
                if neighbor.hash.startswith(str(self.unique_id)):

                        # I sent this signal! # lets check if it FULLy signed
                        if len(neighbor.hash.split(sep='_')) == signalCountRequired:
                            # full signal 
                            self.model.schedule.remove(neighbor)
                            self.model.grid.remove_agent(neighbor)
                            self.send_signal(probability=100)
                            # self.send_kill_signal(probability= 10 )
                            # self.color = "Yellow"
                            # self.radius = 1.0
                            self.mobility = self.mobility  / 5
                            self.vitality = self.vitality + 300
                            self.last_full_signal_timestamp = tools.current_milli_time()
                            print("full hash:",neighbor.hash)
                        else:
                            #  signal not completed... ignore
                            continue      
                if neighbor.hash.startswith(self.parent_id): # My parent sent this!!
                    if len(neighbor.hash.split(sep='_')) == signalCountRequired:
                            continue
                    else:
                        # i will add my signature to this!!
                        if str(self.unique_id) not in neighbor.hash:
                                neighbor.hash = neighbor.hash + "_" + str(self.unique_id)
                                self.mobility = self.mobility / 10 
                                self.vitality = self.vitality + 200
                                self.last_time_I_received_parent_signal_and_attached_my_signature = tools.current_milli_time()
                                # neighbor.color = tools.random_color()
                                neighbor.vitality = neighbor.vitality + 20
                                if len(neighbor.hash.split(sep='_')) == signalCountRequired:
                                    neighbor.vitality = neighbor.vitality + 400 
                                # print("ADDED MY HASH:", neighbor.hash)
    def send_kill_signal(self, probability):
        if self.level == 0:
            return
        if tools.bool_with_probability(probability):
            empty_cells = tools.get_empty_around_me(self)
            if len(empty_cells) > 0 :
                self.model.add_agent( KillSignal(unique_id= self.model.current_id + 1 , hash = str(self.unique_id), color=self.color, radius=self.radius / 5), empty_cells[0])                    
    def send_signal(self, probability):
        # if self.parent_id != "":
        #     return
        if self.level == 0 or self is None:
            return
        if tools.bool_with_probability(probability):
            empty_cells = tools.get_empty_around_me(self)
            numberNeeded = 0 if probability == 100 else 8
            if len(empty_cells) > numberNeeded :
                self.model.add_agent( Signal(unique_id= self.model.current_id + 1 , hash = str(self.unique_id), color=self.color, radius=self.radius / 5, mobility = 10000/(self.level+1)**2, vitality= 50/(self.level+1)**2 ), empty_cells[0])
        
        
        
        
        
        
        

#start the simulation
# tools.start_simulation(80,80,[Cell(color="#f54242"),Cell(color="#15bce6"), Cell(color="#BF07F2"),  Cell(color="#1DA526"), Cell(color="#E5FF00"), Cell(color="#FF00EC"), Cell(color="#00FF11")])
tools.start_simulation(100,100,[Cell(color="#f54242")])


