import random

class Player:
    def __init__(self, user_id):
        self.user_id = user_id
        self.health = 100
        self.mana = 100
        self.attack_power = 10
        self.position = (random.randint(0, 9), random.randint(0, 9))

    def move(self, direction, grid):
        # Define direction vectors
        direction_vectors = {
            "up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1),
            "up-left": (-1, -1), "up-right": (-1, 1),
            "down-left": (1, -1), "down-right": (1, 1)
        }
        if direction in direction_vectors:
            new_position = (
                self.position[0] + direction_vectors[direction][0],
                self.position[1] + direction_vectors[direction][1]
            )
            # Check bounds and obstacles
            if (0 <= new_position[0] < len(grid) and
                    0 <= new_position[1] < len(grid[0]) and
                    grid[new_position[0]][new_position[1]] != 'obstacle'):
                self.position = new_position

    def attack(self, target_position, grid, monsters, players):
        # Calculate distance to the target
        distance = max(abs(self.position[0] - target_position[0]),
                       abs(self.position[1] - target_position[1]))
        if distance <= 1:
            # Regular attack on monsters or players
            for monster in monsters:
                if monster.position == target_position:
                    monster.health -= self.attack_power
                    if monster.health <= 0:
                        monsters.remove(monster)
            for player in players.values():
                if player.position == target_position and player.user_id != self.user_id:
                    player.health -= self.attack_power
                    if player.health <= 0:
                        del players[player.user_id]

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "health": self.health,
            "mana": self.mana,
            "position": self.position
        }

class Monster:
    def __init__(self, position):
        self.health = 10
        self.attack_power = 2
        self.position = position

    def attack(self, players):
        for player in players.values():
            if max(abs(self.position[0] - player.position[0]),
                   abs(self.position[1] - player.position[1])) <= 1:
                player.health -= self.attack_power
                if player.health <= 0:
                    del players[player.user_id]

    def to_dict(self):
        return {
            "health": self.health,
            "position": self.position
        }

class Fruit:
    def __init__(self, position):
        self.position = position

    def to_dict(self):
        return {
            "position": self.position
        }

class Obstacle:
    def __init__(self, position):
        self.position = position

    def to_dict(self):
        return {
            "position": self.position
        }

class CenterSquare:
    def __init__(self, size, center_x, center_y):
        self.size = size
        self.center_x = center_x
        self.center_y = center_y
        self.healing_rate = 2

    def random_position(self):
        return (
            random.randint(self.center_x - self.size // 2, self.center_x + self.size // 2),
            random.randint(self.center_y - self.size // 2, self.center_y + self.size // 2)
        )

    def heal_players(self, players):
        for player in players.values():
            if (self.center_x - self.size // 2 <= player.position[0] <= self.center_x + self.size // 2 and
                    self.center_y - self.size // 2 <= player.position[1] <= self.center_y + self.size // 2):
                player.health = min(100, player.health + self.healing_rate)

    def to_dict(self):
        return {
            "center": (self.center_x, self.center_y),
            "size": self.size
        }
