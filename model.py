from mesa import Agent, Model
import tools
class Example(Agent):
    def __init__(self, model = Model(), unique_id = 0, radius = 0.5, color = "Blue", pos = (0,0)):
        super().__init__(unique_id, model)
        self.radius = radius
        self.color = color
class Signal(Agent):
    def __init__(self, model = Model() , hash = "",unique_id = 0, radius = 0.2, color = "Red", mobility = 100, vitality = 200):
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
    def __init__(self, model = tools.AgentModel(), unique_id = 0, radius = 0.5, color = tools.random_color(), mobility = 30,vitality = 300 , parent_id = ""):
        super().__init__(unique_id, model)
        self.radius = radius
        self.color = tools.random_color()
        self.mobility = mobility
        self.vitality = vitality
        self.parent_id = parent_id
        self.step_count = 0
        
    def step(self):
        self.model.move_agent_randomly_with_probability(self)
        # tools.reproduce(self, probability=2)
        self.did_i_receive_signal()
        self.send_signal(probability=5)
        self.step_count = self.step_count + 1
        if self.step_count == 10:
            tools.reproduce(self, probability=100)
        if self.step_count == 20:
            tools.reproduce(self, probability=100)
        if self.step_count == 30:
            tools.reproduce(self, probability=100)
        #     self.send_signal(probability=100)
            
    def did_i_receive_signal(self):
        for neighbor in self.model.grid.iter_neighbors(self.pos, True):
            
               if neighbor.__class__.__name__ != "Signal": #not a signal
                   continue
               print("hash:",neighbor.hash)
               if neighbor.hash.startswith(str(self.unique_id)):

                     # I sent this signal! # lets check if it FULLy signed
                    if len(neighbor.hash.split(sep='_')) == 3:
                        # full signal 
                        self.model.schedule.remove(neighbor)
                        self.model.grid.remove_agent(neighbor)
                        self.send_signal(probability = 100)
                        # self.color = "Yellow"
                        # self.radius = 1.0
                        self.mobility = 1
                        self.vitality = self.vitality + 200
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
                            self.mobility = 1
                            self.vitality = self.vitality + 30
                            # neighbor.color = tools.random_color()
                            if len(neighbor.hash.split(sep='_')) == 3:
                                neighbor.vitality = neighbor.vitality + 20
                            print("ADDED MY HASH:", neighbor.hash)
                         
    def send_signal(self, probability):
        if self.parent_id != "":
            return
        if tools.bool_with_probability(probability):
            empty_cells = tools.get_empty_around_me(self)
            if len(empty_cells) > 0 :
                self.model.add_agent( Signal(unique_id= self.model.current_id + 1 , hash = str(self.unique_id), color=self.color, radius=self.radius / 5), empty_cells[0])
        
        
        
        
        
        
        

#start the simulation
tools.start_simulation(20,20,[Cell(), Cell(),Cell()])

