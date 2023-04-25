from mesa import Agent, Model
import tools
class Example(Agent):
    def __init__(self, model = Model(), unique_id = 0, radius = 1.0, color = "#2042FB", pos = (0,0)):
        super().__init__(unique_id, model)
        self.radius = radius
        self.color = color
class Signal(Agent):
    def __init__(self, model = Model() , hash = "",unique_id = 0, radius = 0.2, color = "#FB4720", mobility = 100, vitality = 20):
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
    def __init__(self, model = tools.AgentModel(), unique_id = 0, radius = 1.0, color = tools.random_color(), mobility = 50,vitality = 30 , parent_id = "ABC", level = 3 ):
        super().__init__(unique_id, model)
        self.radius = radius
        self.parent_id = parent_id
        self.color = color # if self.parent_id != "ABC"  else tools.random_color()
        self.mobility = mobility * level
        
        self.step_count = 0
        self.level = level
        self.vitality = vitality  if self.parent_id != "ABC" else 100000
        self.last_full_signal_timestamp = tools.current_milli_time()
        self.last_time_I_received_parent_signal_and_attached_my_signature = tools.current_milli_time()
        
    def step(self):
        self.model.move_agent_randomly_with_probability(self)
        # tools.reproduce(self, probability=2)
        self.did_i_receive_signal()
        self.send_signal(probability=((self.level+1) ** 3)/10)
        self.step_count = self.step_count + 1
        if self.last_full_signal_timestamp != None and tools.current_milli_time() -  self.last_full_signal_timestamp > 4000:
            tools.reproduce(self, probability=100)
        if self.step_count == 10:
            tools.reproduce(self, probability=100)
        if self.step_count == 20:
            tools.reproduce(self, probability=100)
        if self.step_count == 30:
            tools.reproduce(self, probability=100)
        # if self.step_count == 40:
        #     tools.reproduce(self, probability=100)
        #     self.send_signal(probability=100)
            
    def did_i_receive_signal(self):
        for neighbor in self.model.grid.iter_neighbors(self.pos, True):
               if neighbor.__class__.__name__ == "Signal":
                   print(neighbor)
               if neighbor.__class__.__name__ != "Signal" and  neighbor.__class__.__name__ != "KillSignal": #not a signal
                   continue
               if neighbor.__class__.__name__ == "KillSignal" and neighbor.hash.startswith(str(self.parent_id)) and tools.current_milli_time() - self.last_time_I_received_parent_signal_and_attached_my_signature > 10000 and self.parent_id != "ABC":
                    self.model.schedule.remove(self)
                    self.model.grid.remove_agent(self)
                    continue
                   
               print("hash:",neighbor.hash)
               if neighbor.hash.startswith(str(self.unique_id)):

                     # I sent this signal! # lets check if it FULLy signed
                    if len(neighbor.hash.split(sep='_')) == 3:
                        # full signal 
                        self.model.schedule.remove(neighbor)
                        self.model.grid.remove_agent(neighbor)
                        self.send_signal(probability=100)
                        # self.send_kill_signal(probability= 10 )
                        # self.color = "Yellow"
                        # self.radius = 1.0
                        self.mobility = self.mobility  = 0
                        self.vitality = self.vitality + 100
                        self.last_full_signal_timestamp = tools.current_milli_time()
                    else:
                         #  signal not completed... ignore
                        continue      
               if neighbor.hash.startswith(self.parent_id): # My parent sent this!!
                   if len(neighbor.hash.split(sep='_')) == 3:
                        continue
                   else:
                       # i will add my signature to this!!
                       if str(self.unique_id) not in neighbor.hash:
                            neighbor.hash = neighbor.hash + "_" + str(self.unique_id)
                            self.mobility = 0
                            self.vitality = self.vitality + 70
                            self.last_time_I_received_parent_signal_and_attached_my_signature = tools.current_milli_time()
                            # neighbor.color = tools.random_color()
                            neighbor.vitality = neighbor.vitality + 20
                            if len(neighbor.hash.split(sep='_')) == 3:
                                neighbor.vitality = neighbor.vitality + 50
                            print("ADDED MY HASH:", neighbor.hash)
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
            if len(empty_cells) > 0 :
                self.model.add_agent( Signal(unique_id= self.model.current_id + 1 , hash = str(self.unique_id), color=self.color, radius=self.radius / 5), empty_cells[0])
        
        
        
        
        
        
        

#start the simulation
tools.start_simulation(60,60,[Cell(color="#f54242"),Cell(color="#15bce6"), Cell(color="#BF07F2"),  Cell(color="#1DA526")])
#tools.start_simulation(20,20,[Cell(color="#f54242")])


