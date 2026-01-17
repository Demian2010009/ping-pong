from pygame import *
import socket
import json
from threading import Thread

# --- НАЛАШТУВАННЯ КОЛЬОРІВ ---
COLOR_BG_MAIN = (0 ,127 ,255)       
COLOR_BG_WIN = (20, 20, 30)        
COLOR_BG_COUNTDOWN = (10, 10, 10)  
COLOR_PADDLE_LEFT = (0, 255, 150)  
COLOR_PADDLE_RIGHT = (255, 100, 255)
COLOR_BALL = (0, 0, 0)       
COLOR_TEXT = (255, 215, 0)         

# --- ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

# --- СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080)) # ---- Підключення до сервера
            buffer = ""
            game_state = {}
            my_id_data = client.recv(24).decode().strip()
            my_id = int(my_id_data)
            return my_id, game_state, buffer, client
        except:
            pass

def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            if not data: break
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)

# --- ГРА ---
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()

while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    # 1. Екран відліку
    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.fill(COLOR_BG_COUNTDOWN)
        countdown_text = font_win.render(str(game_state["countdown"]), True, COLOR_BALL)
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue 

    # 2. Екран переможця
    if "winner" in game_state and game_state["winner"] is not None:
        screen.fill(COLOR_BG_WIN)

        if you_winner is None: 
            you_winner = (game_state["winner"] == my_id)

        text = "Ти переміг!" if you_winner else "Пощастить наступним разом!"
        
        win_text = font_win.render(text, True, COLOR_TEXT)
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        restart_text = font_main.render('К - рестарт', True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        screen.blit(restart_text, restart_rect)

        display.update()
        continue 

    # 3. Основний ігровий процес
    if game_state:
        screen.fill(COLOR_BG_MAIN) # ЗМІНА КОЛЬОРУ ФОНУ ТУТ
        
        # Малюємо платформи
        draw.rect(screen, COLOR_PADDLE_LEFT, (20, game_state['paddles']['0'], 20, 100))
        draw.rect(screen, COLOR_PADDLE_RIGHT, (WIDTH - 40, game_state['paddles']['1'], 20, 100))
        
        # Малюємо м'яч
        draw.circle(screen, COLOR_BALL, (game_state['ball']['x'], game_state['ball']['y']), 10)
        
        # Рахунок
        score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, COLOR_BALL)
        screen.blit(score_text, (WIDTH // 2 - 25, 20))

        # Обробка звуків (якщо додасте файли)
        if game_state.get('sound_event'):
            pass

    else:
        screen.fill(COLOR_BG_MAIN)
        waiting_text = font_main.render(f"Очікування гравців...", True, COLOR_BALL)
        screen.blit(waiting_text, (WIDTH // 2 - 100, HEIGHT // 2))

    display.update()
    clock.tick(60)

    # Керування
    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP\n")
    elif keys[K_s]:
        client.send(b"DOWN\n")