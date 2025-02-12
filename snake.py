import streamlit as st
import random
import time
import numpy as np

# Impostazioni iniziali del gioco
BOARD_SIZE = 20
CELL_SIZE = 20
SNAKE_INIT_LEN = 3
FPS = 10  # Frame per secondo

# Inizializza lo stato del gioco
def init_game():
    snake = [(5, 5), (5, 4), (5, 3)]  # Corpo del serpente (partenza)
    direction = (0, 1)  # Direzione (destra)
    food = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))  # Posizione del cibo
    return snake, direction, food

# Funzione per aggiornare la posizione del serpente
def move_snake(snake, direction):
    head = snake[0]
    new_head = (head[0] + direction[0], head[1] + direction[1])
    snake = [new_head] + snake[:-1]
    return snake

# Funzione per gestire la crescita del serpente quando mangia il cibo
def grow_snake(snake):
    return [snake[0]] + snake

# Funzione per generare una nuova posizione del cibo
def generate_food(snake):
    food = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))
    while food in snake:
        food = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))
    return food

# Funzione per verificare se il serpente si è schiantato contro se stesso o i bordi
def check_collision(snake):
    head = snake[0]
    if head in snake[1:]:
        return True  # Collisione con il corpo
    if not (0 <= head[0] < BOARD_SIZE and 0 <= head[1] < BOARD_SIZE):
        return True  # Collisione con i bordi
    return False

# Funzione per disegnare il gioco
def draw_game(snake, food):
    grid = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    for segment in snake:
        grid[segment[0], segment[1]] = 1  # Corpo del serpente
    grid[food[0], food[1]] = 2  # Cibo
    return grid

# Funzione principale del gioco
def snake_game():
    snake, direction, food = init_game()
    score = 0
    game_over = False

    # Streamlit component per controllare l'input dell'utente
    keys = st.radio("Use arrow keys to control the snake:", ('Up', 'Down', 'Left', 'Right'))

    # Mappa delle direzioni in base alla scelta dell'utente
    direction_map = {
        'Up': (-1, 0),
        'Down': (1, 0),
        'Left': (0, -1),
        'Right': (0, 1)
    }
    
    direction = direction_map.get(keys, direction)

    # Ciclo di gioco
    while not game_over:
        snake = move_snake(snake, direction)

        if snake[0] == food:
            food = generate_food(snake)  # Genera nuovo cibo
            snake = grow_snake(snake)  # Cresce il serpente
            score += 1

        game_over = check_collision(snake)  # Verifica se il gioco è finito

        # Disegna la griglia del gioco
        grid = draw_game(snake, food)

        st.write(f"Score: {score}")
        st.image(grid, use_column_width=True)  # Visualizza la griglia del gioco

        time.sleep(1 / FPS)  # Pausa per controllare il frame rate

    st.write("Game Over!")

# Avvio del gioco
if __name__ == '__main__':
    snake_game()
