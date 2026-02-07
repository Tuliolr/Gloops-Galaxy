import pgzrun

# 1. Configuracoes da Janela
WIDTH = 1000 
HEIGHT = 900
MENU = 0
JOGANDO = 1
game_state = MENU

# Fisica e Camera
gravidade = 0.8
velocidade_y = 0
esta_pulando = False
scroll_x = 0  

# Variaveis de Animacao
speed = 5
gravidade = 0.8
velocidade_y = 0

estado = "idle"     # idle | walk | jump
direcao = 1         # 1 = direita | -1 = esquerda
frame = 0
timer_anim = 0
esta_pulando = False
andando = False
titulo_y_offset = 0
titulo_y_direcao = 1
# 2. Objetos
btn_start = Actor('btn_start', (500, 250))
btn_exit = Actor('btn_exit', (500, 400))
player = Actor('character_green_idle', (250, 300))
# Ajuste da ancora para evitar tremores nas trocas de sprites
player.anchor = ('center', 'bottom')
titulo_y_offset = 0
titulo_y_direcao = 1 # 1 para descer, -1 para subir
plataformas = []  

def criar_plataforma_longa(x_inicial, y, blocos_do_meio):
    largura_sprite = 64 
    try:
        p_esq = Actor('plat_esq', (x_inicial, y))
        p_esq.anchor = ('left', 'top')
        plataformas.append(p_esq)
        for i in range(1, blocos_do_meio + 1):
            p_meio = Actor('plat_meio', (x_inicial + (i * largura_sprite), y))
            p_meio.anchor = ('left', 'top')
            plataformas.append(p_meio)
        p_dir = Actor('plat_dir', (x_inicial + ((blocos_do_meio + 1) * largura_sprite), y))
        p_dir.anchor = ('left', 'top')
        plataformas.append(p_dir)
    except:
        print("Erro ao carregar pecas da plataforma modular")

# --- MONTANDO O CENARIO ---
largura_chao = 64 
for i in range(50): # Chao bem longo
    try:
        bloco = Actor('chao', (i * largura_chao, 750))
        bloco.anchor = ('left', 'top')
        plataformas.append(bloco)
    except:
        pass

# Plataformas flutuantes usando o sistema modular
criar_plataforma_longa(300, 600, 2)
criar_plataforma_longa(700, 500, 3)
criar_plataforma_longa(1200, 400, 2)

# Musiquinha
try:
    music.play('tema_fundo')
    music.set_volume(0.4)
except:
    pass

def draw():
    # Limpa a tela completamente a cada frame para evitar rastros/quadrados
    screen.clear()
    
    if game_state == MENU:
        try: screen.blit('background', (0, 0))
        except: screen.fill((30, 30, 50))
        btn_start.draw()
        btn_exit.draw()
        screen.draw.text("START", center=btn_start.pos, fontsize=45, color="white")
        screen.draw.text("EXIT", center=btn_exit.pos, fontsize=45, color="white")

        # O NOME DO JOGO - ASTROHOP (Com Animacao Flutuante)
        screen.draw.text(
            "GLOOP'S GALAXY", 
            center=(WIDTH // 2, 120 + titulo_y_offset), # Posicao X central, Y flutuante
            fontsize=100, 
            color="green", # Cor de energia alienigena
            shadow=(2, 2), 
            scolor="darkgreen" # Sombra escura para contraste
        )
        
    elif game_state == JOGANDO:
        try: screen.blit('fase_bg', (0, 0))
        except: screen.fill((50, 150, 200))
        
        # Desenha plataformas com a camera (scroll)
        for p in plataformas:
            pos_x_original = p.x
            p.x -= scroll_x 
            p.draw()
            p.x = pos_x_original 
            
        # Desenha player com a camera
        pos_player_original = player.x
        player.x -= scroll_x
        player.draw()
        player.x = pos_player_original
        
def animar_walk():
    global frame

    frames = ["character_green_walk_right_a", "character_green_walk_right_b"]

    if direcao == 'left':
        frames = ["character_green_walk_left_a", "character_green_walk_left_b"]

    player.image = frames[frame // 6 % len(frames)]
    frame += 1

def update():
    global velocidade_y, esta_pulando, game_state, scroll_x, timer_anim, direcao, titulo_y_offset, titulo_y_direcao, estado, frame

    andando = False

    if game_state == MENU:
        titulo_y_offset += titulo_y_direcao * 0.5 # A velocidade de flutuacao
        if titulo_y_offset > 10 or titulo_y_offset < -10: # Limite de flutuacao
            titulo_y_direcao *= -1 # Inverte a direc

    # === MOVIMENTO HORIZONTAL ===
    if keyboard.left:
        player.x -= speed
        direcao = -1
        andando = True

    elif keyboard.right:
        player.x += speed
        direcao = 1
        andando = True

    # === PULO ===
    if keyboard.space and not esta_pulando:
        velocidade_y = -18
        esta_pulando = True

    # === GRAVIDADE ===
    player.y += velocidade_y
    velocidade_y += gravidade

    # === COLISÃO COM PLATAFORMAS (VERTICAL) ===
    chao_detectado = False

    for p in plataformas:
        # Posição real da plataforma
        px = p.x
        py = p.y
        pw = p.width
        ph = p.height

        # Caixa do player
        player_left = player.x - player.width // 2
        player_right = player.x + player.width // 2

        # Verifica se o player está caindo
        if velocidade_y >= 0:
            # Colisão horizontal
            if player_right > px and player_left < px + pw:
                # Pé do player encostando no topo da plataforma
                if player.y <= py and player.y + velocidade_y >= py:
                    player.y = py
                    velocidade_y = 0
                    esta_pulando = False
                    chao_detectado = True
    # === ANIMAÇÃO ===
    timer_anim += 1

    if estado != "walk":
        frame = 0

    if estado == "idle":
        player.image = "character_green_idle"

    elif estado == "jump":
        player.image = "character_green_jump"

    elif estado == "walk":
        if timer_anim >= 18:   # mais lento e suave
            frame = (frame + 1) % 2
            timer_anim = 0

    if direcao == 1:
        player.image = (
            "character_green_walk_right_a"
            if frame == 0
            else "character_green_walk_right_b"
        )
    else:
        player.image = (
            "character_green_walk_left_a"
            if frame == 0
            else "character_green_walk_left_b"
        )
    
    # === ESTADO DO PLAYER ===
    if esta_pulando:
        estado = "jump"
    elif andando:
        estado = "walk"
    else:
        estado = "idle"


def on_mouse_down(pos):
    global game_state, scroll_x, velocidade_y, esta_pulando, estado

    if game_state == MENU:
        if btn_start.collidepoint(pos):
            game_state = JOGANDO

            # RESET IMPORTANTE
            scroll_x = 0
            player.pos = (250, 300)
            velocidade_y = 0
            esta_pulando = False
            estado = "idle"

        elif btn_exit.collidepoint(pos):
            exit()

pgzrun.go()
