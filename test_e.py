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
        self.counter: dict = {"A": 0, "B":0} 
        self.commitment: str = "uncommited"
        self.current_phase = "exploration"

    def update(self):
        if self.current_phase == "exploration":
            self.exploration_phase()

    def after_update(self):
        pass

    def exploration_phase(self):
        self.commitment = 'A'
        self.change_image(1)
        
class CustomSimulation(Simulation):
    def before_update(self) -> None:
        print("Checking stop condition inside ExperimentWindow...")
        
        agents = self._agents
        total_agents = 100 
        
        count_a: int = sum(1 for agent in agents if agent.commitment == 'A')
        count_b: int = sum(1 for agent in agents if agent.commitment == 'B')

        threshold_agents = 0.8 * total_agents 
        
        if count_a >= threshold_agents or count_b >= threshold_agents:
            print(f"Terminated due to Threshold Being Met A: {count_a}, B: {count_b}")
            self.stop()

class ExperimentWindow(Window): ...

(
    CustomSimulation(BestOf2Config(image_rotation=False, movement_speed=1, radius=10, window=ExperimentWindow()))
    .spawn_site("images/nl.png", x=375, y=375)
    .batch_spawn_agents(100, SwarmAgent, images=["images/triangle.png", "images/green.png"])
    .run()
)

