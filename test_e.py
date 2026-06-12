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
        self.counter: dict = {"A": 0, "B":0} #Amount of nests of given type encountered during the exploretion
        self.commitment: str = "uncommited"
        self.current_phase = "exploration"
    def update(self):
        if self.current_phase == "exploration":
            self.exploration_phase()
    def after_update(self):
        pass
    def exploration_phase(self):
        pass
class NestAgent(Agent[BestOf2Config]):
    def __init__(self, images, simulation, pos = None, move = None, nest_id = None):
        super().__init__(images, simulation, move)
        self.pos.x = random.randint(0, 750)
        self.pos.y = random.randint(0, 750)
        self.nest_id 
    def on_spawn(self):
        self.freeze_movement()
        if 100 <= self.id <= 119:
            self.nest_id = "A"
        elif 120 <= self.id:
            self.nest_id = "B"
        
class ExperimentWindow(Window): ...


(
    Simulation(BestOf2Config(image_rotation=False, movement_speed=1, radius=10, window=ExperimentWindow()))
    .spawn_site("images/nl.png", x=375, y=375)
    .batch_spawn_agents(100, SwarmAgent, images=["images/triangle.png"])
    .batch_spawn_agents(20, NestAgent, images=["images/red.png"])
    .batch_spawn_agents(10, NestAgent, images=["images/green.png"])
    .run()
)

