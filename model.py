from mesa import Agent, Model
import tools
import random

signalCountRequired = 3

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
        if self.vitality <= 0:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
            return
        self.model.move_agent_randomly_with_probability(self, move_factor = 3)
        self.step_count = self.step_count + 1 
class Cell(Agent):
    def __init__(self, model = tools.AgentModel(), unique_id = 0, radius = 1.0, color = tools.random_color(), mobility = 1900,vitality = 150 , parent_id = "ABC", level = random.randint(2, 9), reproduceProbability = 1 ):
        super().__init__(unique_id, model)
        self.radius = radius
        self.parent_id = parent_id
        self.color = color 
        self.mobility = (mobility) * level
        
        self.step_count = 0
        self.level = level
        self.vitality = 400 / (self.level * 2 + 1)  if self.parent_id != "ABC" else 100000
        self.last_full_signal_timestamp = tools.current_milli_time()
        self.last_time_I_received_parent_signal_and_attached_my_signature = tools.current_milli_time()
        
    def step(self):
        # if tools.remove_agent_randomly_with_probability(self, probability = 1) == True:
        #     return
        if self.vitality <= 0:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
            return
        self.model.move_agent_randomly_with_probability(self)
        if tools.current_milli_time() - self.last_time_I_received_parent_signal_and_attached_my_signature > (10000 / (self.level+1)) and str(self.parent_id) != "ABC":
              self.model.schedule.remove(self)
              self.model.grid.remove_agent(self)
        self.did_i_receive_signal()
        self.send_signal(probability=((self.level+1) ** 3)/50)
        self.step_count = self.step_count + 1
        if self.last_full_signal_timestamp != None and tools.current_milli_time() -  self.last_full_signal_timestamp > (12000 / (self.level+1)):
            tools.reproduce(self, probability=100)
            tools.reproduce(self, probability=100)
        if self.step_count == 10:
            tools.reproduce(self, probability=self.vitality / 3)
        if self.step_count == 30:
            self.mobility = 300

           
    def did_i_receive_signal(self):
        if self.pos is not None:
            neighbors = tools.get_neighbors(self, empty=False, radius= int(20/((self.level+1)**2)))
            for neighbor in neighbors:
                if neighbor.__class__.__name__ != "Signal" and  neighbor.__class__.__name__ != "KillSignal": #not a signal
                    continue
                if neighbor.hash.startswith(str(self.parent_id)) and tools.current_milli_time() - self.last_time_I_received_parent_signal_and_attached_my_signature > 15000 and self.parent_id != "ABC":
                    try:
                        self.model.schedule.remove(self)
                        self.model.grid.remove_agent(self)
                        continue
                    except:
                        continue
                    
                if neighbor.hash.startswith(str(self.unique_id)):

                        # I sent this signal! # lets check if it FULLy signed
                        if len(neighbor.hash.split(sep='_')) == signalCountRequired:
                            # full signal 
                            self.model.schedule.remove(neighbor)
                            self.model.grid.remove_agent(neighbor)
                            self.send_signal(probability=100)
                            self.mobility = self.mobility  / 100
                            self.vitality = self.vitality + min(100,1000/(self.level+1)**2)
                            self.last_full_signal_timestamp = tools.current_milli_time()
                            neighbor.vitality = 0
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
                                self.mobility = self.mobility / 100
                                self.vitality = self.vitality + (100/(self.level+1)**2)
                                self.last_time_I_received_parent_signal_and_attached_my_signature = tools.current_milli_time()
                                neighbor.vitality = neighbor.vitality + 100
                                if len(neighbor.hash.split(sep='_')) == signalCountRequired:
                                    neighbor.vitality = neighbor.vitality + 100 
    def send_signal(self, probability):
        # if self.parent_id != "":
        #     return
        if self.level == 0 or self is None:
            return
        if tools.bool_with_probability(probability):
            empty_cells = tools.get_neighbors(self, empty = True)
            numberNeeded = 0 if probability == 100 else 8
            if len(empty_cells) > numberNeeded :
                self.model.add_agent( Signal(unique_id= self.model.current_id + 1 , hash = str(self.unique_id), color="#15bce6", radius=self.radius / 5, mobility = 100000/(self.level+1)**2, vitality= 1000/(self.level+1)**2 ), empty_cells[0])
        
   

#start the simulation
# tools.start_simulation(100,100,[Cell(color="#15bce6"), Cell(color="#BF07F2"),  Cell(color="#1DA526"), Cell(color="#E5FF00"), Cell(color="#FF00EC"), Cell(color="#00FF11")])
# tools.start_simulation(70,70,[ Cell(color="#BF07F2"),  Cell(color="#1DA526")])
tools.start_simulation(100,100,[Cell(color="#f54242")])


