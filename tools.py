import random
import time
import numpy
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def bool_with_probability(percent=50):
    return random.randrange(100) < percent
def current_milli_time():
    return round(time.time() * 1000)
def send_signal(self, signal_class):
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        empty_cells = [cell for cell in neighborhood if self.model.grid.is_cell_empty(cell)]
        if len(empty_cells) == 0:
            return
        signal = signal_class(self.model.current_id + 1, empty_cells[0], self.model)
        signal.receivers = [self.unique_id]
        self.model.current_id += 1
        self.model.grid.place_agent(signal, empty_cells[0])
        self.model.schedule.add(signal)
def remove(self):
        self.model.schedule.remove(self)
        self.grid.remove_agent(self)
def reproduce(agent, probability):
        if bool_with_probability(probability) == False:
            return
        if agent.parent_id != "": #only master stem cell can reproduce - change later !!
            return
        neighborhood = agent.model.grid.get_neighborhood(agent.pos, moore=True, include_center=False)
        empty_cells = [cell for cell in neighborhood if agent.model.grid.is_cell_empty(cell)]
        if len(empty_cells) > 2:
            child = agent.__class__(unique_id=agent.model.current_id + 1,parent_id = str(agent.unique_id), model = agent.model)
            agent.model.current_id += 1
            agent.model.grid.place_agent(child, empty_cells[0])
            agent.lastReproduceTime = current_milli_time()
            child.radius = agent.radius *0.8
            agent.model.schedule.add(child)
      
def agent_portrayal(agent):
    return {
        "Shape": "circle",
        "Filled": "true",
        "r": agent.radius,
         "Color": agent.color,
        "Layer": 0,
    }

class AgentModel(Model):
    def __init__(self, width = 100, height = 100, agents = []):
        self.num_agents = 0
        self.agents = []
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.current_id = 0
        self.width = width
        self.height = height
        self.num_agents = self.num_agents + len(agents)
        for i in range(len(agents)):
            while True:
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                if  self.grid.is_cell_empty((x, y)):
                    break
            agent = agents[i]
            agent.pos = (x,y)
            agent.x = x
            agent.y = y
            agent.model = self
            agent.current_id = self.current_id
            agent.unique_id = self.current_id
            self.agents.append(agent)
            self.current_id += 1
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
    def add_agent(self, agent, pos):
            agent.model = self
            agent.current_id = self.current_id
            agent.unique_id = self.current_id + 1
            self.agents.append(agent)
            self.current_id += 1
            self.grid.place_agent(agent, pos)
            self.schedule.add(agent)
    def move_agent_randomly_with_probability(self,agent):
         if bool_with_probability(agent.mobility) == False:
            return
         x, y = agent.pos
        # generate a random movement direction
         dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        # calculate the new position of the agent
         new_x = int(x + dx)
         new_y = int(y + dy)
         if new_x < 0 or new_x >= self.grid.width or new_y < 0 or new_y >= self.grid.height:
            # if the new position is outside the grid, don't move the agent
            return
        # move the agent to the new position if it's valid
         if self.grid.is_cell_empty((new_x, new_y)) :
            self.grid.move_agent(agent, (new_x, new_y))
    def step(self):
        for agent in self.schedule.agents:
            if agent.vitality == 0:
                self.schedule.remove(agent)
                self.grid.remove_agent(agent)
                return
            agent.vitality = agent.vitality - 2
        self.schedule.step()

def get_empty_around_me(agent):
    neighborhood = agent.model.grid.get_neighborhood(agent.pos, moore=True, include_center=False)
    empty_cells = [cell for cell in neighborhood if agent.model.grid.is_cell_empty(cell)]
    return empty_cells
def random_color():
    return  ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])]
def get_agents_around_me(agent):
    neighborhood = agent.model.grid.get_neighborhood(agent.pos, moore=True, include_center=False)
    non_empty_cells = [cell for cell in neighborhood if agent.model.grid.is_cell_empty(cell) != True]
    return non_empty_cells            
def start_simulation(width,height,agents):
    grid = CanvasGrid(agent_portrayal,width, height, 500, 500)
    server = ModularServer(AgentModel, [grid], "Cell Model",
                           {
                            "width": width, 
                            "height": height, "agents":agents})
    server.port = 8521  #
    server.launch()