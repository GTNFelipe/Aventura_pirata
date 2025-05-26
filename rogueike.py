# Jogo: Aventura pirata - Plataforma
# Desenvolvido por: Felipe Santana da Silva 
# Data: 24/05/2025
import pgzrun
import random
from pygame import Rect

# Configurações da janela do jogo
WIDTH = 1200  # Largura da tela
HEIGHT = 720  # Altura da tela
TITLE = "Aventura pirata"  # Título do jogo

# Estados do jogo
MENU = 0  # Estado do menu principal
PLAYING = 1  # Estado durante o jogo
GAME_OVER = 2  # Estado de game over (não utilizado atualmente)
VICTORY = 3  # Estado de vitória
game_state = MENU  # Estado inicial do jogo
sound_on = True  # Controle de som ligado/desligado
score = 0  # Pontuação do jogador

class Button:
    """Classe para criar botões interativos no menu"""
    def __init__(self, x, y, width, height, text, color=(200, 200, 200), hover_color=(255, 255, 255)):
        """Inicializa um botão com posição, tamanho, texto e cores"""
        self.rect = Rect(x, y, width, height)  # Área retangular do botão
        self.text = text  # Texto exibido no botão
        self.color = color  # Cor normal do botão
        self.hover_color = hover_color  # Cor quando o mouse está sobre o botão
        self.is_hovered = False  # Estado de hover
    
    def draw(self):
        """Desenha o botão na tela"""
        color = self.hover_color if self.is_hovered else self.color
        screen.draw.filled_rect(self.rect, color)
        screen.draw.text(self.text, center=self.rect.center, color=(0, 0, 0), fontsize=32)
    
    def check_hover(self, pos):
        """Verifica se o mouse está sobre o botão"""
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, click):
        """Verifica se o botão foi clicado"""
        return self.rect.collidepoint(pos) and click

# Criação dos botões do menu
start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 80, 200, 50, "Começar")
sound_button = Button(WIDTH//2 - 100, HEIGHT//2, 200, 50, "Som: ligado")
exit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50, "Sair")

class Pirate:
    """Classe que representa o personagem principal do jogo"""
    def __init__(self, x, y):
        """Inicializa o pirata com posição e propriedades de movimento"""
        self.x = x  # Posição X inicial
        self.y = y  # Posição Y inicial
        self.speed = 5  # Velocidade de movimento horizontal
        self.jump_power = 15  # Força do pulo
        self.velocity_y = 0  # Velocidade vertical
        self.is_jumping = False  # Estado de pulo
        self.direction = 1  # Direção atual (1 = direita, -1 = esquerda)
        self.last_direction = 1  # Última direção olhada
        
        # Dicionário de animações para cada estado
        self.animations = {
            'idle_right': ['pirate_idle_right_0', 'pirate_idle_right_1'],
            'idle_left': ['pirate_idle_left_0', 'pirate_idle_left_1'],
            'run_right': ['pirate_run_right_0', 'pirate_run_right_1'],
            'run_left': ['pirate_run_left_0', 'pirate_run_left_1'],
            'jump_right': ['pirate_jump_right'],
            'jump_left': ['pirate_jump_left']
        }
        self.current_animation = 'idle_right'  # Animação atual
        self.animation_index = 0  # Índice do frame atual
        self.animation_timer = 0  # Contador para troca de frames
    
    def update(self, platforms):
        """Atualiza a posição e estado do pirata"""
        moving = False  # Flag para verificar se está se movendo
        
        # Controles de movimento
        if keyboard.left:
            self.direction = -1
            self.last_direction = -1
            self.x -= self.speed
            moving = True
        elif keyboard.right:
            self.direction = 1
            self.last_direction = 1
            self.x += self.speed
            moving = True
        
        # Determina o estado atual (pulando, correndo ou parado)
        if self.is_jumping:
            state = 'jump'
        elif moving:
            state = 'run'
        else:
            state = 'idle'
            self.direction = self.last_direction
        
        # Define a animação baseada no estado e direção
        direction = 'left' if self.direction == -1 else 'right'
        new_animation = f"{state}_{direction}"
        
        # Muda a animação se necessário
        if new_animation != self.current_animation:
            self.current_animation = new_animation
            self.animation_index = 0
            self.animation_timer = 0
        
        # Lógica de pulo
        if keyboard.up and not self.is_jumping:
            self.velocity_y = -self.jump_power
            self.is_jumping = True
            self.current_animation = f"jump_{direction}"
            self.animation_index = 0
        
        # Aplica gravidade
        self.velocity_y += 0.8
        self.y += self.velocity_y
        
        # Verifica colisões com plataformas
        for platform in platforms:
            if (self.y + 50 > platform.rect.y and 
                self.y < platform.rect.y and 
                self.x + 40 > platform.rect.x and 
                self.x < platform.rect.x + platform.rect.width):
                self.y = platform.rect.y - 50
                self.velocity_y = 0
                self.is_jumping = False
                if 'jump' in self.current_animation:
                    self.current_animation = f"idle_{direction}"
        
        # Verifica se o pirata caiu da tela
        if self.y > HEIGHT or self.x < -50 or self.x > WIDTH + 50:
            return True  # Indica que precisa respawnar
        
        # Atualiza animação
        self.animation_timer += 1
        if self.animation_timer > 10:
            self.animation_timer = 0
            frames = self.animations[self.current_animation]
            self.animation_index = (self.animation_index + 1) % len(frames)
        
        return False
    
    def draw(self):
        """Desenha o pirata na tela com a animação atual"""
        try:
            frame = self.animations[self.current_animation][self.animation_index]
            img = getattr(images, frame)
            screen.blit(img, (self.x, self.y))
        except:
            pass

class Enemy:
    """Classe que representa os inimigos do jogo"""
    def __init__(self, x, y, patrol_range):
        """Inicializa o inimigo com posição e alcance de patrulha"""
        self.x = x  # Posição X inicial
        self.y = y  # Posição Y inicial
        self.start_x = x  # Posição X de início da patrulha
        self.patrol_range = patrol_range  # Alcance da patrulha
        self.speed = random.uniform(1.0, 2.5)  # Velocidade aleatória
        self.direction = 1  # Direção inicial (1 = direita, -1 = esquerda)
        
        # Animações do inimigo
        self.animations = {
            'walk_right': ['enemy_walk_right_0', 'enemy_walk_right_1', 'enemy_walk_right_2', 'enemy_walk_right_3'],
            'walk_left': ['enemy_walk_left_0', 'enemy_walk_left_1', 'enemy_walk_left_2', 'enemy_walk_left_3']
        }
        self.current_animation = 'walk_right'  # Animação atual
        self.animation_index = 0  # Índice do frame atual
        self.animation_timer = 0  # Contador para troca de frames
    
    def update(self):
        """Atualiza a posição e animação do inimigo"""
        self.x += self.speed * self.direction
        
        # Inverte a direção quando atinge o limite da patrulha
        if abs(self.x - self.start_x) > self.patrol_range:
            self.direction *= -1
            self.current_animation = 'walk_left' if self.direction == -1 else 'walk_right'
        
        # Atualiza animação
        self.animation_timer += 1
        if self.animation_timer > 10:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.animations[self.current_animation])
    
    def draw(self):
        """Desenha o inimigo na tela com a animação atual"""
        try:
            frame = self.animations[self.current_animation][self.animation_index]
            img = getattr(images, frame)
            screen.blit(img, (self.x, self.y))
        except:
            pass

class Platform:
    """Classe que representa as plataformas do jogo"""
    def __init__(self, x, y, width, height, color=(34, 139, 34)):
        """Inicializa a plataforma com posição, tamanho e cor"""
        self.rect = Rect(x, y, width, height)  # Retângulo de colisão
        self.color = color  # Cor da plataforma
    
    def draw(self):
        """Desenha a plataforma na tela"""
        screen.draw.filled_rect(self.rect, self.color)

class Treasure:
    """Classe que representa os tesouros coletáveis"""
    def __init__(self, x, y):
        """Inicializa o tesouro com posição e estado"""
        self.x = x  # Posição X
        self.y = y  # Posição Y
        self.collected = False  # Se foi coletado ou não
        self.animation_frames = ['treasure_0', 'treasure_1']  # Frames de animação
        self.animation_index = 0  # Índice do frame atual
        self.animation_timer = 0  # Contador para troca de frames
    
    def update(self):
        """Atualiza a animação do tesouro se não foi coletado"""
        if not self.collected:
            self.animation_timer += 1
            if self.animation_timer > 15:
                self.animation_timer = 0
                self.animation_index = 1 - self.animation_index
    
    def draw(self):
        """Desenha o tesouro na tela se não foi coletado"""
        if not self.collected:
            try:
                frame = self.animation_frames[self.animation_index]
                screen.blit(frame, (self.x, self.y))
            except:
                pass

def init_game():
    """Inicializa ou reinicia o jogo com todos os objetos"""
    global pirate, platforms, enemies, treasures, score
    pirate = Pirate(100, 300)  # Cria o pirata
    platforms = [  # Cria todas as plataformas
        Platform(0, 550, 200, 50),
        Platform(250, 500, 200, 50),
        Platform(500, 450, 200, 50),
        Platform(150, 350, 200, 50),
        Platform(400, 300, 200, 50),
        Platform(650, 250, 150, 50)
    ]
    enemies = [  # Cria todos os inimigos
        Enemy(300, 450, 100),
        Enemy(600, 400, 80),
        Enemy(200, 300, 120)
    ]
    treasures = [  # Cria todos os tesouros
        Treasure(350, 450),
        Treasure(600, 400),
        Treasure(250, 250)
    ]
    score = 0  # Reseta a pontuação

# Inicializa o jogo pela primeira vez
init_game()

def update():
    """Função principal de atualização do jogo chamada a cada frame"""
    global game_state, score
    
    if game_state == PLAYING:
        # Atualiza o pirata e verifica se precisa respawnar
        needs_respawn = pirate.update(platforms)
        if needs_respawn:
            init_game()
        
        # Atualiza inimigos e verifica colisões
        for enemy in enemies:
            enemy.update()
            if (abs(pirate.x - enemy.x) < 40 and abs(pirate.y - enemy.y) < 50):
                init_game()  # Reseta o jogo se colidir com inimigo
        
        # Verifica se todos os tesouros foram coletados
        all_collected = all(t.collected for t in treasures)
        if all_collected:
            game_state = VICTORY
            if sound_on:
                sounds.victory.play()
        
        # Atualiza tesouros e verifica coleta
        for treasure in treasures:
            treasure.update()
            if (not treasure.collected and 
                abs(pirate.x - treasure.x) < 30 and 
                abs(pirate.y - treasure.y) < 30):
                treasure.collected = True
                score += 100
                if sound_on:
                    sounds.coin.play()

def draw():
    """Função principal de renderização do jogo chamada a cada frame"""
    screen.fill((135, 206, 235))  # Fundo azul claro
    
    # Chama a função de desenho apropriada para o estado atual
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        draw_game()
    elif game_state == VICTORY:
        draw_victory()

def draw_menu():
    """Desenha a tela de menu com título e botões"""
    screen.draw.text("Aventura pirata", center=(WIDTH//2, HEIGHT//2 - 150), fontsize=64, color=(0, 0, 0))
    start_button.draw()
    sound_button.draw()
    exit_button.draw()

def draw_game():
    """Desenha todos os elementos do jogo durante a gameplay"""
    # Desenha plataformas
    for platform in platforms:
        platform.draw()
    
    # Desenha tesouros
    for treasure in treasures:
        treasure.draw()
    
    # Desenha inimigos
    for enemy in enemies:
        enemy.draw()
    
    # Desenha pirata
    pirate.draw()
    
    # Desenha HUD com pontuação e tesouros restantes
    screen.draw.text(f"Score: {score}", (10, 10), fontsize=36, color=(0, 0, 0))
    remaining = sum(1 for t in treasures if not t.collected)
    screen.draw.text(f"Tesouros: {remaining}/{len(treasures)}", (WIDTH - 200, 10), fontsize=36, color=(0, 0, 0))

def draw_victory():
    """Desenha a tela de vitória"""
    screen.draw.text("VOCÊ VENCEU!", center=(WIDTH//2, HEIGHT//2 - 100), fontsize=100, color=(0, 0, 0))
    screen.draw.text(f"Pontuação final: {score}", center=(WIDTH//2, HEIGHT//2), fontsize=50, color=(255, 255, 255))
    screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, HEIGHT//2 + 100), fontsize=30, color=(28, 28, 28))

def on_mouse_move(pos):
    """Verifica quando o mouse se move sobre os botões do menu"""
    if game_state == MENU:
        start_button.check_hover(pos)
        sound_button.check_hover(pos)
        exit_button.check_hover(pos)

def on_mouse_down(pos):
    """Lida com cliques do mouse nos botões do menu"""
    global game_state, sound_on
    if game_state == MENU:
        if start_button.is_clicked(pos, True):
            game_state = PLAYING
            if sound_on:
                sounds.start.play()
        elif sound_button.is_clicked(pos, True):
            sound_on = not sound_on
            sound_button.text = "Som: ligado" if sound_on else "Som: desligado"
            if sound_on:
                sounds.music.play(-1)
            else:
                sounds.music.stop()
        elif exit_button.is_clicked(pos, True):
            exit()

def on_key_down(key):
    """Lida com pressionamento de teclas"""
    global game_state
    if key == keys.ESCAPE:
        if game_state == VICTORY:
            game_state = MENU
            init_game()

# Inicia a música se o som estiver ligado
if sound_on:
    sounds.music.play(-1)

# Inicia o jogo
pgzrun.go()