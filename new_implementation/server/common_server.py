from flask import Flask, jsonify, request, render_template
from entities import Player, Monster, Fruit, Obstacle, CenterSquare
from utils import initialize_grid, place_entities
from apscheduler.schedulers.background import BackgroundScheduler
import logging

app = Flask(__name__)

# Constants
GRID_SIZE = 10
MONSTER_SPAWN_RATE = 1  # Spawn one monster every timestep
FRUIT_SPAWN_PROBABILITY = 0.1
OBSTACLE_COUNT = 10
CENTER_SIZE = 3

# Global variables
timestep = 0
grid = initialize_grid(GRID_SIZE)
players = {}
monsters = []
fruits = []
obstacles = []
center_square = CenterSquare(CENTER_SIZE, GRID_SIZE // 2, GRID_SIZE // 2)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the APScheduler
scheduler = BackgroundScheduler()

def increment_timestep():
    global timestep
    timestep += 1
    logger.info(f"Timestep: {timestep}")
    handle_monster_spawning()
    update_display()

def handle_monster_spawning():
    if timestep % MONSTER_SPAWN_RATE == 0:
        new_monster = Monster(center_square.random_position())
        monsters.append(new_monster)

def update_display():
    # Update grid and heal players in the center square
    center_square.heal_players(players)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_game():
    # Start the scheduler
    if not scheduler.running:
        scheduler.start()
    return jsonify({"message": "Game started!"}), 200

@app.route('/api/create_player', methods=['POST'])
def create_player():
    user_id = request.json.get('user_id')
    if user_id in players:
        return jsonify({"error": "User ID already exists."}), 400
    player = Player(user_id)
    players[user_id] = player
    return jsonify({"user_id": user_id, "position": player.position}), 201

@app.route('/api/move_player', methods=['POST'])
def move_player():
    user_id = request.json.get('user_id')
    direction = request.json.get('direction')
    if user_id not in players:
        return jsonify({"error": "User ID does not exist."}), 400
    player = players[user_id]
    player.move(direction, grid)
    return jsonify({"user_id": user_id, "position": player.position}), 200

@app.route('/api/player_attack', methods=['POST'])
def player_attack():
    user_id = request.json.get('user_id')
    target_position = request.json.get('target_position')
    if user_id not in players:
        return jsonify({"error": "User ID does not exist."}), 400
    player = players[user_id]
    player.attack(target_position, grid, monsters, players)
    return jsonify({"message": "Attack executed."}), 200

@app.route('/api/get_state', methods=['GET'])
def get_state():
    return jsonify({
        "timestep": timestep,
        "players": [player.to_dict() for player in players.values()],
        "monsters": [monster.to_dict() for monster in monsters],
        "fruits": [fruit.to_dict() for fruit in fruits],
        "obstacles": [obstacle.to_dict() for obstacle in obstacles],
        "center_square": center_square.to_dict()
    }), 200

def setup_game():
    global grid, fruits, obstacles
    grid = initialize_grid(GRID_SIZE)
    fruits = place_entities(Fruit, GRID_SIZE, FRUIT_SPAWN_PROBABILITY)
    obstacles = place_entities(Obstacle, OBSTACLE_COUNT, None)

if __name__ == '__main__':
    setup_game()
    # Add a job to the scheduler to increment timestep every second
    scheduler.add_job(increment_timestep, 'interval', seconds=1)
    app.run(debug=True)
