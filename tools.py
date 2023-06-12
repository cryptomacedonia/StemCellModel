import random
import time
import numpy
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import numpy as np
from PIL import ImageColor
clrs = [
    "#000000",  # Black
    "#FF0000",  # Red
    "#00FF00",  # Green
    "#0000FF",  # Blue
    "#FFFF00",  # Yellow
    "#FF00FF",  # Magenta
    "#00FFFF",  # Cyan
    "#800000",  # Maroon
    "#808000",  # Olive
    "#008000",  # Lime
    "#800080",  # Purple
    "#008080",  # Teal
    "#C0C0C0",  # Silver
    "#FFA500",  # Orange
    "#FFC0CB",  # Pink
    "#FF69B4",  # Hot Pink
    "#DC143C",  # Crimson
    "#FFD700",  # Gold
    "#FFFFE0",  # Light Yellow
    "#00FF7F",  # Spring Green
    "#40E0D0",  # Turquoise
    "#000080",  # Navy
    "#6B8E23",  # Olive Drab
    "#2E8B57",  # Sea Green
    "#BA55D3",  # Medium Orchid
    "#FF6347",  # Tomato
    "#FA8072",  # Salmon
    "#00BFFF",  # Deep Sky Blue
    "#9400D3",  # Dark Violet
    "#D2691E",  # Chocolate
    "#B0E0E6",  # Powder Blue
]
def bool_with_probability(percent=50):
    return random.randrange(100) < percent
def current_milli_time():
    return round(time.time() * 1000)
def send_signal(self, signal_class):
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        empty_cells = get_neighbors(self, empty=True)
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
        if agent.level == 0 or agent is None: # I am leaf cell.. cant reproduce...
            return
        if bool_with_probability(probability) == False:
            return
        empty_cells = []
        if agent.pos is not None:
            neighborhood = agent.model.grid.get_neighborhood(agent.pos, moore=True, include_center=False)
            empty_cells = [cell for cell in neighborhood if agent.model.grid.is_cell_empty(cell)]
        if empty_cells is not None and len(empty_cells) > 6:
            child = agent.__class__(unique_id=agent.model.current_id + 1,parent_id = str(agent.unique_id), model = agent.model,color= color_variant(agent.color,40), level=agent.level - 1)
            if len(clrs) > 0 and child.parent_id == "0":
                child.color = random.choice(clrs)
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
        self.grid = MultiGrid(width, height, torus=False)
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

    def move_agent_randomly_with_probability(self,agent,move_factor = 1):
         if bool_with_probability(agent.mobility) == False:
            return
         x, y = agent.pos
         move_factor = 2 if type(agent).__name__ == "Cell"  else random.randint(1, 13)
        # generate a random movement direction
         dx, dy = random.choice([(0, move_factor), (0, -move_factor), (move_factor, 0), (-move_factor, 0)])
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

def random_color():
    return  ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])]
def get_agents_around_me(agent):
    neighborhood = agent.model.grid.get_neighborhood(agent.pos, moore=True, include_center=False)
    non_empty_cells = [cell for cell in neighborhood if agent.model.grid.is_cell_empty(cell) != True]
    return non_empty_cells 
def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(int(r*255),int(g*255),int(b*255))
import matplotlib.colors as colors
def hex_to_rgb(value):
    val = value[0].lstrip('#')
    if val == "":
        val = value.lstrip('#')
    try:
         bytes.fromhex(val)
       #colors.hex2color(value[0].upper()) 
    except:
        print(val)
    rg = bytes.fromhex(val) 
    if len(rg) < 3:
        print(val)
    return (rg[0]/255,rg[1]/255,rg[2]/255)
    # tu = ImageColor.getcolor(value[0], "RGB") 
    # return (tu[0]/255,tu[1]/255,tu[2]/255)

def color_variant(hex_color, brightness_offset=1):
    """ takes a color like #87c95f and produces a lighter or darker variant """
    if len(hex_color) != 7:
        raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
    rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int] # make sure new values are between 0 and 255
    return "#{:02x}{:02x}{:02x}".format(new_rgb_int[0],new_rgb_int[1],new_rgb_int[2])
def adjust_lightness(color, amount=0.1):
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = hex_to_rgb(c)
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    rg = colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])
    return rgb2hex(rg[0], rg[1], rg[2])
def start_simulation(width,height,agents):
    grid = CanvasGrid(agent_portrayal,width, height, 500, 500)
  
    server = ModularServer(AgentModel, [grid], "Cell Model",
                           {
                            "width": width, 
                            "height": height, "agents":agents})
    server.port = 8521  #
    server.launch()
def get_neighbors(agent, empty=True, radius=4):
    grid = agent.model.grid
    if agent.pos is None:
        return []
    x, y = agent.pos
    empty_neighbors = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if (dx, dy) != (0, 0):  # Exclude the central cell
                neighbor_x = x + dx
                neighbor_y = y + dy

                # Ensure the neighbor coordinates are within the grid bounds
                if not grid.out_of_bounds((neighbor_x, neighbor_y)):
                    cell = grid.get_cell_list_contents([(neighbor_x, neighbor_y)])
                    if not cell and empty is True:  # Check if the cell is empty
                        empty_neighbors.append((neighbor_x, neighbor_y))
                    else :
                        if empty is False and cell:
                            empty_neighbors.append(cell[0])
    return empty_neighbors

def remove_agent_randomly_with_probability(agent, probability = 1):
    return False
    # if bool_with_probability(probability) == False:
    #     return False
    # agent.model.schedule.remove(agent)
    # agent.model.grid.remove_agent(agent)
    # return True