from dataclasses import dataclass
import random
from vi import Agent, Simulation, Window
from vi.config import Config

# randomness setup
random.seed(a=42)
# global vars to return
votes: dict = {"A": 0, "B":0}
@dataclass
class BestOf2Config(Config): ...
class SwarmAgent(Agent[BestOf2Config]):
    def __init__(self, images, simulation, pos = None, move = None):
        super().__init__(images, simulation, pos, move)
        self.counter: dict = {"A": 0, "B":0} #Amount of time spent in each nest during the exploretion
        self.commitment: str = "uncommited"
        self.states: dict = {"exploration": 1000, "dissamination": 0}
        self.state = "exploration"
        self.ticks = 0
        self.prng = random.Random()
        self.prng.seed(42)
    def update(self):
        if self.state == "exploration" and self.states["exploration"] >= self.ticks:
            if self.on_site():
                if self.prng.random() < 0.7:
                    self.counter["A"] += 1
            else:
                if self.prng.random() < 0.3:
                    self.counter["B"] += 1
            self.ticks += 1
        elif self.state == "exploration" and self.states["exploration"] < self.ticks:
            self.decision()
            self.state = "dissamination"
        elif self.state == "dissamination":
            self.freeze_movement()
            count = 0
            for agent, _ in self.in_proximity_accuracy():
                if agent.commitment == self.commitment:
                    count += 1
                elif agent.commitment != self.commitment:
                    count -= 1
                else: #change the commitment to first neighbour option if uncommited
                    self.commitment = agent.commitment 
                    break
            if count <= 0:
                self.commitment = "uncommited"
                self.state = "voting"
            else:
                self.state = "voting"
        elif self.state == "voting":
            self.voting()
        elif self.state == "wait":
            pass
    def decision(self):
        if self.counter["A"] > self.counter["B"]:
            self.commitment = "A"
        elif self.counter["B"] > self.counter["A"]:
            self.commitment = "B"
        #the ones with equal number of encounters (by chance) stay uncommited
    def voting(self):
        if self.commitment == "A":
            votes["A"] += 1
            self.change_image(1)
            self.state = "wait"
        elif self.commitment == "B":
            votes["B"] += 1
            self.change_image(2)
            self.state = "wait"
        else:
            self.state = "exploration"
            self.continue_movement()
        
class ExperimentWindow(Window): ...


(
    Simulation(BestOf2Config(image_rotation=False, movement_speed=1, radius=15, window=ExperimentWindow(), duration = 8000, visualise_chunks = True))
    .spawn_site(image_path="images/images.png", x = 750 //2, y = 750 //2)
    .batch_spawn_agents(100, SwarmAgent, images=["images/triangle.png", "images/green.png", "images/red.png"])   
    .run()
)
print(votes)
