from enum import Enum, auto
import pygame as pg
import vi
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import numpy as np
from numpy import random as r


@deserialize
@dataclass
class AggregationConfig(Config):
    a: float = 2.6
    b: float = 2.2
    
    t: int = 30 + round(r.normal(0,10)) # t = t_join = t_leave
    d: int = 150 # number of time steps between each p_leave is evaluated

    delta_time: float = 1.0

    def weights(self) -> tuple[float, float, int, int]:
        return (self.a, self.b, self.t, self.d)


class Bee(Agent):
    state: int = 0 # 0 -> wandering, 1 -> joining, 2 -> still, 3 -> leaving
    t_step = 0
    d_step = 0


    config: Config

    def wandering(self, in_proximity, a):
        self.pos += self.move
        uniform_roll = r.uniform()
        p_join = 0.03 + 0.48 * (1 - np.exp(-a * in_proximity))

        if self.on_site():
            if p_join > uniform_roll:
                self.state = 1

    def join(self, t):
        self.t_step += 1
        
        if self.t_step == t:
            
            self.t_step = 0
            self.state = 2
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


    def leave(self, t):
        self.t_step += 1
        
        if self.t_step == t:
            self.t_step = 0
            self.state = 0
        else:
            self.pos += self.move

    def change_position(self):
        in_proximity = self.in_proximity_accuracy().count()
        a, b, t, d= self.config.weights()
        self.there_is_no_escape()

        if self.state == 0:
            self.wandering(in_proximity, a)
        if self.state == 1:
            self.join(t)
        if self.state == 2:
            self.still(in_proximity, b, d)
        if self.state == 3:
            self.leave(t)


'''class Selection(Enum):
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
                    print('change')
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-1.0)
                    print('change')
                elif event.key == pg.K_1:
                    self.selection = Selection.A
                elif event.key == pg.K_2:
                    self.selection = Selection.B
                elif event.key == pg.K_3:
                    self.selection = Selection.T
                elif event.key == pg.K_4:
                    self.selection = Selection.D
                    print('change')

        a, b, t, d = self.config.weights()'''
(
    Simulation(
        AggregationConfig(
            image_rotation=True,
            movement_speed=1.5,
            radius=40,
            seed=2,
            fps_limit=150,
        )
    )
        .spawn_site("bubble-full.png", 375, 375)
        .batch_spawn_agents(50, Bee, images=["green.png"])
        .run()
)
