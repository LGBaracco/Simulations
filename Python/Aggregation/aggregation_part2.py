from enum import Enum, auto
import pygame as pg
import vi
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import numpy as np
from numpy import random as r
import polars as pl
import seaborn as sns



@deserialize
@dataclass
class AggregationConfig(Config):
    a: float = 2.6
    b: float = 2.2
    t: int = round(r.normal(70,50)) # t = t_join = t_leave
    d: int = 300 # number of time steps between each p_leave is evaluated
    w: int = 500 # number of time steps it takes to move agent of site if not deciding to join or leaving


    def weights(self) -> tuple[float, float, int, int, int]:
        return (self.a, self.b, self.t, self.d, self.w)


class Bee(Agent):
    state = 0 # 0 -> wandering, 1 -> joining, 2 -> still, 3 -> leaving
    t_step = 0
    d_step = 0
    w_step = 0

    config: AggregationConfig

    def wandering(self, in_proximity, a, w):
        self.pos += self.move
        uniform_roll = r.uniform()
        p_join = 0.03 + 0.48 * (1 - np.exp(-a * in_proximity))


        if self.on_site():
            if self.w_step == 0:
                if p_join > uniform_roll:
                    self.state = 1
            else:
                self.w_step +=1

        if self.w_step == w:
            self.w_step = 0

    def join(self, t):
        self.t_step += 1
        
        if self.t_step == t:
            print(t)
            
            self.t_step = 0
            
            if self.on_site():
                self.state = 2
            else:
                self.state = 0
        else:
            self.pos += self.move



    def still(self, in_proximity, b, d):
        self.d_step += 1

        if self.d_step == d:
            self.d_step = 0
            
            uniform_roll = r.uniform()
            p_leave = np.exp(-b * in_proximity)
        
            if p_leave > uniform_roll:
                self.state = 3


    def leave(self, w):
        self.t_step += 1
        
        if self.t_step == w:
            self.t_step = 0
            self.state = 0
        else:
            self.pos += self.move

    def change_position(self):
        in_proximity = self.in_proximity_accuracy().count()
        a, b, t, d, w = self.config.weights()
        self.there_is_no_escape()

        if self.state == 0:
            self.wandering(in_proximity, a, w)
        if self.state == 1:
            self.join(t)
        if self.state == 2:
            self.still(in_proximity, b, d)
        if self.state == 3:
            self.leave(w)
            
    def update(self):
        if self.on_site_id() is not None:
            self.save_data("site_id", self.on_site_id())
        else:
            self.save_data("site_id", 2)


class Selection(Enum):
    A = auto()
    B = auto()
    T = auto()
    D = auto()


class AggregationLive(Simulation):
    selection: Selection = Selection.D
    config: AggregationConfig

    def handle_event(self, by: float):
        if self.selection == Selection.A:
            self.config.a += by
        elif self.selection == Selection.B:
            self.config.b += by
        elif self.selection == Selection.T:
            self.config.t += by
        elif self.selection == Selection.D:
            self.config.d += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=1.0)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-1.0)
                elif event.key == pg.K_1:
                    self.selection = Selection.A
                elif event.key == pg.K_2:
                    self.selection = Selection.B
                elif event.key == pg.K_3:
                    self.selection = Selection.T
                elif event.key == pg.K_4:
                    self.selection = Selection.D

        a, b, t, d, _ = self.config.weights()
        # print(f"A: {a:.1f} - C: {b:.1f} - T: {t:.1f} - D {d: .1f}")

df = (
    AggregationLive(
        AggregationConfig(
            image_rotation=True,
            movement_speed=2.0,
            radius=25,
            seed=30,
            fps_limit=60,
            duration=8000
        )
    )
        .spawn_site("site_medium.png", 200, 500)
        .spawn_site("site_medium.png", 700, 500)
        .batch_spawn_agents(100, Bee, images=["bees.png"])
        .run()
        .snapshots.groupby(["frame","site_id"])
        .agg(pl.count("id").alias("agent"))
        .sort(["frame", "site_id"])

)

plot = sns.relplot(x=df["frame"], y=df['agent'], hue=df["site_id"], kind='line')

plot.savefig("plot.png", dpi=300)
