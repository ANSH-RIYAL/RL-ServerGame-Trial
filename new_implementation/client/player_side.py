import requests

BASE_URL = 'http://localhost:5000/api'

def create_player(user_id):
    response = requests.post(f'{BASE_URL}/create_player', json={"user_id": user_id})
    return response.json()

def move_player(user_id, direction):
    response = requests.post(f'{BASE_URL}/move_player', json={"user_id": user_id, "direction": direction})
    return response.json()

def player_attack(user_id, target_position):
    response = requests.post(f'{BASE_URL}/player_attack', json={"user_id": user_id, "target_position": target_position})
    return response.json()

def start_game():
    response = requests.post(f'{BASE_URL}/start')
    return response.json()

def get_state():
    response = requests.get(f'{BASE_URL}/get_state')
    return response.json()

if __name__ == '__main__':
    # Example usage
    start_game()
    user_id = 'player1'
    print(create_player(user_id))
    print(move_player(user_id, 'up'))
    print(player_attack(user_id, (50, 50)))
    print(get_state())
