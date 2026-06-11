from dataclasses import dataclass
import random
from vi import Agent, Simulation, Window
from vi.config import Config

# randomness setup
random.seed(a=42)
@dataclass
class BestOf2Config(Config): ...

class SwarmAgent(Agent[BestOf2Config]):
    def __init__(self, images, simulation, pos = None, move = None):
        super().__init__(images, simulation, pos, move)
    def update():
        pass

class NestAgent(Agent[BestOf2Config]):
    def __init__(self, images, simulation, pos = None, move = None, nest_id = None, quality = None):
        super().__init__(images, simulation, move)
        self.pos.x = random.randint(0, 750)
        self.pos.y = random.randint(0, 750)
    def on_spawn(self):
        self.freeze_movement()
class ExperimentWindow(Window): ...


(
    Simulation(BestOf2Config(image_rotation=False, movement_speed=1, radius=10, window=ExperimentWindow()))
    .batch_spawn_agents(100, SwarmAgent, images=["images/triangle.png"])
    .spawn_agent(NestAgent, images=["images/red.png"])
    .spawn_agent(NestAgent, images=["images/green.png"])
    .run()
)
