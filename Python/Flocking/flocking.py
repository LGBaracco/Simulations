from enum import Enum, auto
import pygame as pg
import vi
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize

import numpy as np
MAX_VEL = 2



@deserialize
@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 5.0
    cohesion_weight: float = 5.0
    separation_weight: float = 5.0

    delta_time: float = 1.0

    mass: int = 20

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


class Bird(Agent):
    config: FlockingConfig

    def alignment(self, neighbours):
        '''
        Alignment of boids based on average velocity of x surrounding boids within range R
        '''
        self.neighbours = neighbours
        vectors = np.array([[self.move[0]],[self.move[1]]])
        in_proximity = self.in_proximity_accuracy().count()
        scalar = 1 / (self.neighbours +1)
        if in_proximity == self.neighbours:
            for agent, distance in self.in_proximity_accuracy():
                vectors = np.append(vectors, np.array([[agent.move[0]],[agent.move[1]]]), axis=1)

            new_move = scalar * np.sum(vectors, axis=1) * MAX_VEL
            new_move = Vector2(new_move[0], new_move[1]).normalize()
            return new_move - self.move


    def cohesion(self, neighbours):
        '''
        Cohesion of boids based on average position of x surrounding boids within range R
        '''
        vectors = np.array([[self.move[0]],[self.move[1]]])
        in_proximity = self.in_proximity_accuracy().count()
        scalar = 1 / (self.neighbours +1)
        if in_proximity == self.neighbours:
            for agent, distance in self.in_proximity_accuracy():
                vectors = np.append(vectors, np.array([[agent.pos[0]],[agent.pos[1]]]), axis=1)

            new_pos = scalar * np.sum(vectors, axis=1) * MAX_VEL
            new_pos = Vector2(new_pos[0], new_pos[1]).normalize()
            return new_pos - self.pos

    def seperation(self, neighbours):
        '''
        Seperation of boids based on average position of x surrounding boids within range R
        '''
        vectors = np.array([[self.pos[0]],[self.pos[1]]])
        in_proximity = self.in_proximity_accuracy().count()
        scalar = 1 / (self.neighbours+1)
        if in_proximity == self.neighbours:
            for agent, distance in self.in_proximity_accuracy():
                temp_vec = np.array([[self.pos[0] - agent.pos[0]],[self.pos[1] - agent.pos[1]]])
                temp_vec /= distance
                vectors = np.append(vectors, temp_vec, axis=1)
            new_pos = scalar * np.sum(vectors, axis=1) * MAX_VEL
            new_pos = Vector2(new_pos[0], new_pos[1]).normalize()
            return new_pos

    def change_position(self):
        global MAX_VEL
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        self.pos += self.move
        in_proximity = self.in_proximity_accuracy().count()
        if self.on_site():
            self.kill()
        self.p



class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.COHESION
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=1.0)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-1.0)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")


(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1.0,
            radius=35,
            seed=24,
            fps_limit =100,
        )
    )

        .batch_spawn_agents(1000, Bird, images=["green.png",
                                              "red.png",
                                              "bird.png"])
        .run()
)
