from vi import Agent, Simulation, Window, util, HeadlessSimulation
from vi.config import Config, dataclass, deserialize
from numpy import random as r
import polars as pl
import seaborn as sns
from pygame.math import Vector2
import matplotlib.pyplot as plt


@deserialize
@dataclass
class CompetitionConfig(Config):
    fox_energy: int = 500  # initial energy level of a fox
    hunger: int = 50  # time a fox has to wait before killing a rabbit
    r_rep: float = 0.8  # rabbit reproduction rate
    r_rep_buffer: int = 120  # time steps between each reproduction evaluation
    offspring: int = 2  # max offspring produced at reproduction
    reach_radius: int = 15  # mating and hunting radius
    stress_deviation: float = 0.5
    t: int = round(r.normal(30, 10))  # join buffer
    shelter_capacity: int = 15

    def weights(self) -> tuple[int, int, float, int, int, int, float, int, int]:
        return (self.fox_energy, self.hunger, self.r_rep, self.r_rep_buffer, self.offspring, self.reach_radius,
                self.stress_deviation, self.t, self.shelter_capacity)


class Fox(Agent):
    energy_t: int = 0
    hunger_t: int = 0

    config: CompetitionConfig

    def check_survival(self, energy):
        """
        Kills fox if energy is 0
        """
        if self.energy_t == energy:
            self.kill()

    def consume(self, hunger, offspring, reach_radius):
        """
        Checks whether there are nearby rabbits to consume and eventually does
        """
        if self.hunger_t >= hunger:

            prey = (self.in_proximity_accuracy()
                    .filter_kind(Rabbit)
                    .filter(lambda agent: not agent[0].on_site())  # does not take sheltered rabbits into account
                    .first())

            if prey is not None and prey[1] < reach_radius:
                prey[0].kill()
                self.hunger_t = 0
                self.energy_t = 0
                self.reproduction(offspring, reach_radius)

    def reproduction(self, offspring, reach_radius):
        """
        Reproduction of foxes gives some probability
        """
        mate = (self.in_proximity_accuracy()
                .filter_kind(Fox)
                .first())

        if mate is not None and mate[1] < reach_radius:
            for i in range(r.randint(1, offspring)):
                self.reproduce()
                self.move = util.random_angle(1.5)

    def avoid_shelter(self):
        '''Let foxes move away from shelters'''
        if self.on_site():
            # self.move = util.random_angle(1.5)
            self.move.rotate_ip(180)
            self.pos += 4 * self.move  # steps out to avoid infinite loop

    def change_position(self):
        self.there_is_no_escape()
        self.avoid_shelter()
        self.pos += self.move

    def update(self):
        self.save_data("agent_type", 1)

        energy, hunger, _, _, offspring, reach_radius, _, t, _ = self.config.weights()  # init params

        self.check_survival(energy)  # kill fox if no energy is left
        self.consume(hunger, offspring, reach_radius)

        self.energy_t += 1
        self.hunger_t += 1


class Rabbit(Agent):
    r_rep_buffer_t = 0
    t_step = 0
    state = 0  # 0=wandering, 1=joining, 2=still, 3=leaving

    config: CompetitionConfig

    def reproduction(self, r_rep, r_rep_buffer, offspring, stress_deviation, reach_radius):
        """
        Reproduction of Rabbits
        """
        if self.r_rep_buffer_t == r_rep_buffer:
            mate = (self.in_proximity_accuracy()
                    .filter_kind(Rabbit)
                    .first())

            if mate is not None and mate[1] < reach_radius:
                roll = r.uniform()

                if self.in_proximity_accuracy().filter_kind(Fox).count() > 0 and not self.on_site():
                    r_bias = r.normal(0, stress_deviation)
                    r_rep -= abs(r_bias)

                if roll > r_rep:
                    self.r_rep_buffer_t = 0
                    for i in range(r.randint(1, offspring)):
                        self.reproduce().move = util.random_angle(1.5)  # .move = Vector2(new_x, new_y)
        else:
            self.r_rep_buffer_t += 1

    def join(self, t):
        self.t_step += 1

        if self.t_step == t:

            self.t_step = 0

            if self.on_site():
                self.state = 2
            else:
                self.state = 0
        else:
            self.pos += self.move

    def still(self, capacity):
        sheltered = (self.in_proximity_accuracy()
                     .filter_kind(Rabbit)
                     .filter(lambda agent: agent[0].on_site())  # only takes sheltered rabbits into account
                     .count())

        if sheltered > capacity:
            self.state = 3

    def leave(self):

        if not self.on_site():
            self.state = 0
        else:
            self.pos += self.move

    def change_position(self):

        self.there_is_no_escape()
        _, _, _, _, _, _, _, t, shelter_capacity = self.config.weights()  # init params

        if self.state == 0:
            if self.on_site():
                self.state = 1
            else:
                self.pos += self.move
        if self.state == 1:
            self.join(t)
        if self.state == 2:
            self.still(shelter_capacity)
        if self.state == 3:
            self.leave()

    def update(self):
        self.save_data("agent_type", 2)

        _, _, r_rep, r_rep_buffer, offspring, reach_radius, stress_deviation, _, _ = self.config.weights()  # init params
        self.reproduction(r_rep, r_rep_buffer, offspring, stress_deviation, reach_radius)


energy_values = [500, 600, 700]
hunger_values = [20, 40, 60]
# reach_values = [10, 15]
stress_dev_values = [0.5, 0.6]

energy_value = energy_values[0]
hunger_value = hunger_values[0]
stress_dev_value = stress_dev_values[0]

df = (
      HeadlessSimulation(
          CompetitionConfig(
              image_rotation=True,
              movement_speed=1.5,
              radius=45,
              seed=30,
              fps_limit=60,
              window=Window.square(700),
              fox_energy=energy_value,
              hunger=hunger_value,
              stress_deviation=stress_dev_value,
              duration=100,

              )
          )
      .batch_spawn_agents(100, Fox, images=["Fox.png"])
      .batch_spawn_agents(100, Rabbit, images=["Rabbit.png"])
      .spawn_site("site_small.png", 600, 350)
      .run()
      .snapshots
      .groupby("frame")
      .agg(
          [
              (pl.col('agent_type') == 1).count().alias('Foxes'),
              (pl.col('agent_type') == 2).count().alias('Rabbits'),
          ]
      )
      .sort('frame')
)
df.write_csv(f'comp_{energy_value}_{hunger_value}_{stress_dev_value}.csv', sep=',')
