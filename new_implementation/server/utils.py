import random
from entities import Fruit, Obstacle

GRID_SIZE = 100

def initialize_grid(size):
    return [['' for _ in range(size)] for _ in range(size)]

def place_entities(EntityClass, count_or_probability, probability=None):
    entities = []
    if probability is not None:
        # Place entities based on probability
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if random.random() < probability:
                    entities.append(EntityClass((x, y)))
    else:
        # Place a fixed number of entities
        for _ in range(count_or_probability):
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            entities.append(EntityClass((x, y)))
    return entities
