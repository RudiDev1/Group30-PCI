from dataclasses import dataclass
import random
from vi import Agent, Simulation, Window, Matrix
from vi.config import Config
import time

start_time: float = time.perf_counter()
@dataclass
class SwarmAgent(Agent):
    config: Config
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
                    self.counter["A"] += 1
            else:
                    self.counter["B"] += 1
            self.ticks += 1
        elif self.state == "exploration" and self.states["exploration"] < self.ticks:
            self.decision()
            self.state = "dissamination"
            self.ticks = 0
        elif self.state == "dissamination":
            #self.freeze_movement()
            count = 0
            for agent, _ in self.in_proximity_accuracy():
                if agent.commitment == "uncommited":
                    pass
                elif agent.commitment == self.commitment:
                    count += 1
                elif agent.commitment != self.commitment:
                    count -= 1
                else: #change the commitment to first neighbour option if uncommited
                    self.commitment = agent.commitment 
                    break
            if count < 0:
                self.commitment = "uncommited"
                self.change_image(0)
            self.state = "voting"
        elif self.state == "voting":
            self.voting()
    def decision(self):
        if self.counter["A"] > self.counter["B"]:
            self.commitment = "A"
        elif self.counter["B"] > self.counter["A"]:
            self.commitment = "B"
        #the ones with equal number of encounters (by chance) stay uncommited
    def voting(self):
        if self.commitment == "A":
            self.change_image(1)
            x = self.prng.random()
            if x <= 0.5:
                self.state = "exploration"
                self.counter = {"A": 0, "B": 0}
            elif x > 0.5:
                self.state = "dissamination"
        elif self.commitment == "B":
            self.change_image(2)
            x = self.prng.random()
            if x <= 0.5:
                self.state = "exploration"
                self.counter = {"A": 0, "B": 0}
            elif x > 0.5:
                self.state = "dissamination"
        else:
            self.state = "exploration"
            self.continue_movement()

class CustomSimulation(Simulation):
    def __init__(self, config):
        super().__init__(config)
        self.current_tick = 0
    def before_update(self) -> None:
        super().before_update()

        current = self.current_tick

        agents = self._agents
        total_agents = 100 
        
        count_a: int = sum(1 for agent in agents if agent.commitment == 'A')
        count_b: int = sum(1 for agent in agents if agent.commitment == 'B')

        threshold_agents = 0.9 * total_agents 
        if current % 1002 == 0 and current != 0:
            print(f"Threshold of A: {count_a}, B: {count_b} at {current}")
        
        if count_a >= threshold_agents or count_b >= threshold_agents:
            final_time: float = time.perf_counter()
            total_time: float = final_time - start_time
            print(f"Terminated due to Threshold Being Met A: {count_a}, B: {count_b}")
            print(f"Time - {total_time}")
            self.stop()
        
        self.current_tick += 1

class ExperimentWindow(Window): ...

def run_simulation(config):
    (
    CustomSimulation(config)
    .spawn_site(image_path="images/images.png", x = 750 //2, y = 750 //2)
    .batch_spawn_agents(100, SwarmAgent, images=["images/triangle.png", "images/green.png", "images/red.png"])   
    .run()
    )

if __name__ == "__main__":
    matrix = Matrix(fps_limit= 60, movement_speed=1, radius=[15, 30, 50, 75, 100, 150], window=ExperimentWindow(), duration = 432000, seed= 42, visualise_chunks= True)
    configs = matrix.to_configs(Config)
    for config in configs:
        run_simulation(config)