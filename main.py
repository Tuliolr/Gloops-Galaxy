# -*- coding: utf-8 -*-
import pgzrun
# CONFIGURACOES
WIDTH = 1000
HEIGHT = 900
MENU = 0
JOGANDO = 1
game_state = MENU
# FISICA / CAMERA
gravidade = 0.8
velocidade_y = 0
esta_pulando = False
scroll_x = 0
CAMERA_CENTER_X = WIDTH // 2
# PLAYER / ANIMACAO
speed = 5
direcao = 1
estado = "idle"
frame = 0
timer_anim = 0
andando = False
invencivel = 0
SPAWN_X = 100
SPAWN_Y = 650
# MENU
titulo_y_offset = 0
titulo_y_direcao = 1
# OBJETOS
btn_start = Actor('btn_start', (500, 250))
btn_exit = Actor('btn_exit', (500, 400))
player = Actor('character_green_idle')
hud_helmet = Actor('hud_player_helmet_green', (80, 80))
hud_character3 = Actor('hud_character_3', (125, 80))
hud_character0 = Actor('hud_character_0', (220, 80))
player.anchor = ('center', 'bottom')
hud_helmet.anchor = ('center', 'center')
hud_character3.anchor = ('center', 'center')
hud_character0.anchor = ('center', 'center')
hud_key = Actor('hud_key_blue', (180, 80))
hud_key.anchor = ('center', 'center')
plataformas = []
lavas = []
# CENARIO
def criar_plataforma_longa(x_inicial, y, blocos_do_meio):
    largura = 64

    p_esq = Actor('plat_esq', (x_inicial, y))
    p_esq.anchor = ('left', 'top')
    plataformas.append(p_esq)

    for i in range(1, blocos_do_meio + 1):
        p_meio = Actor('plat_meio', (x_inicial + i * largura, y))
        p_meio.anchor = ('left', 'top')
        plataformas.append(p_meio)

    p_dir = Actor(
        'plat_dir',
        (x_inicial + (blocos_do_meio + 1) * largura, y)
    )
    p_dir.anchor = ('left', 'top')
    plataformas.append(p_dir)

def criar_lava_chao(x_inicial, y, blocos_do_meio):
    largura = 64

    # LAVA ESQUERDA
    lava_esq = Actor('lava_top', (x_inicial, y))
    lava_esq.anchor = ('left', 'top')
    lavas.append(lava_esq)

    # LAVA MEIO
    for i in range(1, blocos_do_meio + 1):
        lava_meio = Actor(
            'lava_top',
            (x_inicial + i * largura, y)
        )
        lava_meio.anchor = ('left', 'top')
        lavas.append(lava_meio)

    # LAVA DIREITA
    lava_dir = Actor(
        'lava_top',
        (x_inicial + (blocos_do_meio + 1) * largura, y)
    )
    lava_dir.anchor = ('left', 'top')
    lavas.append(lava_dir)

def criar_lava_em_tres_partes(x_inicial, y, total_blocos):
    largura = 64
    parte = total_blocos // 3
    esquerda = parte
    meio = parte + (total_blocos % 3)
    direita = parte
    x = x_inicial
    # LAVA ESQUERDA
    criar_lava_chao(x, y, esquerda - 1)
    x += esquerda * largura
    # LAVA MEIO
    criar_lava_chao(x, y, meio - 1)
    x += meio * largura
    # LAVA DIREITA
    criar_lava_chao(x, y, direita - 1)

def eh_lava(indice, zonas_lava):
    for inicio, fim in zonas_lava:
        if inicio <= indice <= fim:
            return True
    return False
def resetar_player():
    global player, vy, no_chao, scroll_x, invencivel
    player.x = SPAWN_X
    player.y = SPAWN_Y
    vy = 0
    no_chao = False
    invencivel = 60
    scroll_x = player.x - CAMERA_CENTER_X

def verificar_lava():
    if invencivel > 0:
        return

    for lava in lavas:
        if player.colliderect(lava):
            resetar_player()
            break
def montar_cenario():
    plataformas.clear()
    lavas.clear()
    largura = 64
    zonas_lava = [
        (8, 14),
        (20, 25),
        (35, 42)
    ]

    for i in range(60):
        x = i * largura
        if eh_lava(i, zonas_lava):
            lava = Actor('lava_top', (x, 750))
            lava.anchor = ('left', 'top')
            lavas.append(lava)

        else:
            bloco = Actor('chao', (x, 750))
            bloco.anchor = ('left', 'top')
            plataformas.append(bloco)

    criar_plataforma_longa(300, 600, 2)
    criar_plataforma_longa(700, 500, 3)
    criar_plataforma_longa(1200, 400, 2)

    try:
        music.play('tema_fundo')
        music.set_volume(0.4)
    except:
        pass

def draw():
    screen.clear()

    if game_state == MENU:
        try:
            screen.blit('background', (0, 0))
        except:
            screen.fill((30, 30, 50))

        btn_start.draw()
        btn_exit.draw()

        screen.draw.text("START", center=btn_start.pos, fontsize=45, color="white")
        screen.draw.text("EXIT", center=btn_exit.pos, fontsize=45, color="white")
        screen.draw.text(
            "GLOOP'S GALAXY",
            center=(WIDTH // 2, 120 + titulo_y_offset),
            fontsize=100,
            color="green",
            shadow=(2, 2),
            scolor="darkgreen"
        )
    elif game_state == JOGANDO:
        try:
            screen.blit('fase_bg', (0, 0))
        except:
            screen.fill((50, 150, 200))

        # PLATAFORMAS COM CAMERA
        for p in plataformas:
            ox = p.x
            p.x -= scroll_x
            p.draw()
            p.x = ox

        # PLAYER COM CAMERA
        ox = player.x
        player.x -= scroll_x
        player.draw()
        player.x = ox

        hud_helmet.draw()
        hud_character3.draw()
        hud_character0.draw()
        hud_key.draw()

        for lava in lavas:
            pos_original = lava.x
            lava.x -= scroll_x
            lava.draw()
            lava.x = pos_original
def movimento_e_fisica_player():
    global velocidade_y, esta_pulando, direcao, andando
    andando = False
    # HORIZONTAL
    if keyboard.left:
        player.x -= speed
        direcao = -1
        andando = True
    elif keyboard.right:
        player.x += speed
        direcao = 1
        andando = True
    # PULO
    if keyboard.space and not esta_pulando:
        velocidade_y = -18
        esta_pulando = True
    # GRAVIDADE
    velocidade_y += gravidade
    player.y += velocidade_y
def colisao_vertical():
    global velocidade_y, esta_pulando
    pe_anterior = player.y - velocidade_y
    for p in plataformas:
        px = p.x
        py = p.y
        pw = p.width
        player_left = player.x - player.width / 2
        player_right = player.x + player.width / 2
        if velocidade_y >= 0:
            if player_right > px and player_left < px + pw:
                if pe_anterior <= py <= player.y:
                    player.y = py
                    velocidade_y = 0
                    esta_pulando = False
                    return

    esta_pulando = True

def animar_player():
    global frame, timer_anim, estado
    timer_anim += 1
    if esta_pulando:
        estado = "jump"
    elif andando:
        estado = "walk"
    else:
        estado = "idle"

    if estado == "idle":
        player.image = "character_green_idle"

    elif estado == "jump":
        player.image = "character_green_jump"

    elif estado == "walk":
        if timer_anim >= 18:
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
def update():
    global invencivel
    if invencivel > 0:
        invencivel -= 1

    verificar_lava()
    if game_state == MENU:
        animar_titulo_menu()
        return
    movimento_e_fisica_player()
    colisao_vertical()
    atualizar_camera()
    animar_player()
def animar_titulo_menu():
    global titulo_y_offset, titulo_y_direcao
    titulo_y_offset += titulo_y_direcao * 0.5
    if titulo_y_offset > 10 or titulo_y_offset < -10:
        titulo_y_direcao *= -1
def atualizar_camera():
    global scroll_x
    alvo = player.x - CAMERA_CENTER_X
    scroll_x += (alvo - scroll_x) * 0.1
def on_mouse_move(pos):
    if game_state == MENU:
        btn_start.image = 'btn_start_hover' if btn_start.collidepoint(pos) else 'btn_start'
        btn_exit.image = 'btn_exit_hover' if btn_exit.collidepoint(pos) else 'btn_exit'
def on_mouse_down(pos):
    global game_state, scroll_x, velocidade_y, esta_pulando, estado
    if game_state == MENU:
        if btn_start.collidepoint(pos):
            game_state = JOGANDO
            scroll_x = 0
            player.pos = (250, 300)
            velocidade_y = 0
            esta_pulando = False
            estado = "idle"
            montar_cenario()
        elif btn_exit.collidepoint(pos):
            exit()
pgzrun.go()
