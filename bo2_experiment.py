from dataclasses import dataclass
import random
from multiprocessing import Pool
from vi import Agent, HeadlessSimulation, Simulation, Window, Matrix
from vi.config import Config
import time

import pandas as pd
import matplotlib.pyplot as plt
@dataclass
class BestOf2Config(Config): ...
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
        self.belief_strength: float = 0.0
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
        total_time = self.counter['A'] + self.counter['B']
        if total_time == 0:
            total_time = 1
        if self.counter["A"] > self.counter["B"]:
            self.commitment = "A"
            self.belief_strength = self.counter['A'] / total_time
        elif self.counter["B"] > self.counter["A"]:
            self.commitment = "B"
            self.belief_strength = self.counter['B'] / total_time
        else:
            self.commitment = 'uncommited'
            self.belief_strength = 0.0
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

class CustomSimulation(HeadlessSimulation):
    def __init__(self, config):
        super().__init__(config)
        self.current_tick = 0
        self.start_time: float = time.perf_counter()
        with open(f"results{current_radius}seed{current_seed}.txt", "w") as f:
            f.write("")
        self.archive = []
    def before_update(self) -> None:
        super().before_update()
        current = self.current_tick

        agents = self._agents
        total_agents = 100 
        
        count_a: int = sum(1 for agent in agents if agent.commitment == 'A')
        count_b: int = sum(1 for agent in agents if agent.commitment == 'B')

        consensus = count_a - count_b

        strength_a = sum(agent.belief_strength for agent in agents if agent.commitment == 'A')
        strength_b = sum(agent.belief_strength for agent in agents if agent.commitment == 'B')

        self.archive.append({
            "timestep": current,
            "consensus_diff": consensus,
            "strength_a": strength_a,
            "strength_b": strength_b
        })

        threshold_agents = 0.9 * total_agents 
        if current % 1002 == 0 and current != 0:
            with open(f"results{current_radius}seed{current_seed}.txt", "a") as f:
                f.write(f"Threshold of A: {count_a}, B: {count_b} at {current} \n")
        
        if count_a >= threshold_agents or count_b >= threshold_agents:
            final_time: float = time.perf_counter()
            total_time: float = final_time - self.start_time
            print(f"Terminated due to Threshold Being Met A: {count_a}, B: {count_b}")
            print(f"Time - {total_time}")
            print(f"Tick - {current}")
            with open(f"results{current_radius}seed{current_seed}.txt", "a") as f:
                f.write(f"Terminated due to Threshold Being Met A: {count_a}, B: {count_b} \n")
                f.write(f"Time - {total_time} \n")
                f.write(f"Tick - {current} \n")
            self.generate_graphs()    
            self.stop()
        
        self.current_tick += 1
    def generate_graphs(self):
        df = pd.DataFrame(self.archive)

        plt.figure(figsize=(10,4))
        plt.plot(df['timestep'], df['consensus_diff'], label='Consensus (A-B)')
        plt.xlabel("Timestep") 
        plt.ylabel("Difference (Count A - Count B)") 
        plt.title(f"Consensus Over Time (Radius: {current_radius}) (Seed: {current_seed})") 
        plt.legend() 
        plt.grid(True) 
        plt.savefig(f"consensus_radius_{current_radius}.png") 
        plt.close()

        plt.figure(figsize=(10, 4)) 
        plt.plot(df["timestep"], df["strength_a"], label="Total Strength A", color="green") 
        plt.plot(df["timestep"], df["strength_b"], label="Total Strength B", color="red") 
        plt.xlabel("Timestep") 
        plt.ylabel("Summed Belief Strength") 
        plt.title(f"Collective Strength of Belief (Radius: {current_radius}) (Seed: {current_seed})") 
        plt.legend() 
        plt.grid(True) 
        plt.savefig(f"belief_strength_radius_{current_radius}{current_radius}.png") 
        plt.close()
class ExperimentWindow(Window): ...

def run_simulation(config):
    (
    CustomSimulation(config)
    .spawn_site(image_path="images/images.png", x = 750 //2, y = 750 //2)
    .batch_spawn_agents(100, SwarmAgent, images=["images/triangle.png", "images/green.png", "images/red.png"])   
    .run()
    )

if __name__ == "__main__":
    radius_experiment = [num for num in range(10, 61, 5)] 
    seed_experiment = [42, 78, 93, 128, 256, 512, 789, 10234, 8908, 65894, 873492, 29823]
    matrix = Matrix(fps_limit=60, movement_speed=1, radius=radius_experiment, window=ExperimentWindow(), duration = 432000, seed= seed_experiment, visualise_chunks= True)
    configs = matrix.to_configs(Config)
    for config in configs:
        current_radius = config.radius
        current_seed = config.seed
        print(f"Radius Tested {current_radius} PRNG Seed: {current_seed}")
        run_simulation(config)
        
        print("--------------")