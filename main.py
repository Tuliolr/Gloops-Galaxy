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
key_y_offset = 0
key_y_direcao = 1
SPAWN_X = 32   
SPAWN_Y = 600
# OBJETOS
btn_start = Actor('btn_start', (500, 250))
btn_exit = Actor('btn_exit', (500, 400))
player = Actor('character_green_idle')
player.anchor = ('center', 'bottom')
hud_helmet = Actor('hud_player_helmet_green', (80, 50))
hud_character3 = Actor('hud_character_3', (125, 50))
hud_character0 = Actor('hud_character_0', (220, 50))
hud_key = Actor('hud_key_blue', (180, 50))
key = Actor('key_blue')
key.pos = (210, 150)
porta_base = Actor('door_closed')
porta_topo = Actor('door_closed_top')
porta_base.anchor = ('left', 'bottom')
porta_topo.anchor = ('left', 'bottom')
porta_pos_x = 3240
porta_pos_y = 572
plataformas = []
lavas = []
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
        screen.draw.text("GLOOP'S GALAXY", center=(WIDTH // 2, 120 + titulo_y_offset), fontsize=100, color="green", shadow=(2, 2), scolor="darkgreen")
    
    elif game_state == JOGANDO:
        try:
            screen.blit('fase_bg', (0, 0))
        except:
            screen.fill((50, 150, 200))
        # Desenha Plataformas
        for p in plataformas:
            ox = p.x
            p.x -= scroll_x
            p.draw()
            p.x = ox
        # Desenha Lavas
        for lava in lavas:
            ox = lava.x
            lava.x -= scroll_x
            lava.draw()
            lava.x = ox  
        # Desenha Chave
        ox_key, oy_key = key.x, key.y
        key.x -= scroll_x
        key.y += key_y_offset
        key.draw()
        key.x, key.y = ox_key, oy_key
        ox_p, oy_p = porta_pos_x, porta_pos_y
        # Porta Base
        porta_base.x = ox_p - scroll_x
        porta_base.y = oy_p
        porta_base.draw()
        porta_topo.x = ox_p - scroll_x
        porta_topo.y = oy_p - 64 
        porta_topo.draw()
        porta_base.x, porta_topo.x = ox_p, ox_p
        # Desenha Player
        ox = player.x
        player.x -= scroll_x
        player.draw()
        player.x = ox
        # HUD
        hud_helmet.draw()
        hud_character3.draw()
        hud_character0.draw()
        hud_key.draw()
def update():
    global invencivel, key_y_offset, key_y_direcao
    
    if game_state == MENU:
        animar_titulo_menu()
        return
    if invencivel > 0:
        invencivel -= 1    
    verificar_lava()
    # Animação da Chave
    key_y_offset += key_y_direcao * 0.5 
    if key_y_offset > 10 or key_y_offset < -5:
        key_y_direcao *= -1   
    if player.colliderect(key):
        key.x = -1000    
    movimento_e_fisica_player()
    colisao_vertical()
    atualizar_camera()
    animar_player()
    if player.colliderect(porta_base) and key.x < 0:
        print("VOCÊ VENCEU!")       
# AUXILIARES DE CENARIO
def eh_lava(indice, zonas_lava):
    for inicio, fim in zonas_lava:
        if inicio <= indice <= fim:
            return True
    return False
def criar_plataforma_longa(x_inicial, y, blocos_do_meio):
    largura = 64
    p_esq = Actor('plat_esq', (x_inicial, y))
    p_esq.anchor = ('left', 'top')
    plataformas.append(p_esq)
    for i in range(1, blocos_do_meio + 1):
        p_meio = Actor('plat_meio', (x_inicial + i * largura, y))
        p_meio.anchor = ('left', 'top')
        plataformas.append(p_meio)
    p_dir = Actor('plat_dir', (x_inicial + (blocos_do_meio + 1) * largura, y))
    p_dir.anchor = ('left', 'top')
    plataformas.append(p_dir)
def montar_cenario():
    global plataformas, lavas
    plataformas.clear()
    lavas.clear()
    largura = 64
    zonas_lava = [(12, 18), (30, 36), (50, 60)] 
    # CHAO E LAVA INICIAL
    for i in range(150): 
        x = i * largura
        if eh_lava(i, zonas_lava):
            lava = Actor('lava_top', (x, 750))
            lava.anchor = ('left', 'top')
            lavas.append(lava)
        else:
            bloco = Actor('chao', (x, 750))
            bloco.anchor = ('left', 'top')
            plataformas.append(bloco)
    # PLATAFORMAS AEREAS
    criar_plataforma_longa(300, 600, 2)
    criar_plataforma_longa(750, 500, 3)
    criar_plataforma_longa(1200, 450, 2)
    criar_plataforma_longa(1650, 550, 2) 
    criar_plataforma_longa(2100, 500, 3) 
    criar_plataforma_longa(2550, 450, 2) 
    criar_plataforma_longa(3000, 600, 4) 
    # CAMINHO SUPERIOR (CONECTADO AO PRINCIPAL)
    criar_plataforma_longa(150, 210, 1) 
    criar_plataforma_longa(500, 300, 1)   
    criar_plataforma_longa(950, 250, 2)  
    criar_plataforma_longa(1400, 200, 1)  
    criar_plataforma_longa(1850, 250, 1)  
    criar_plataforma_longa(2300, 200, 2)  
    criar_plataforma_longa(2750, 300, 1)
    # PLATAFORMAS EXTREMAS (OPCIONAIS/TROLL) 
    criar_plataforma_longa(800, 100, 1)   
    criar_plataforma_longa(1250, 80, 2)  
    criar_plataforma_longa(1700, 120, 1)  
    criar_plataforma_longa(2150, 90, 1)  
    criar_plataforma_longa(2600, 130, 2)
def resetar_player():
    global velocidade_y, esta_pulando, scroll_x, invencivel
    player.x = SPAWN_X
    player.y = SPAWN_Y
    velocidade_y = 0
    esta_pulando = False
    invencivel = 60
    scroll_x = 0
def verificar_lava():
    if invencivel > 0: return
    for lava in lavas:
        if player.colliderect(lava):
            resetar_player()
            break
def animar_titulo_menu():
    global titulo_y_offset, titulo_y_direcao
    titulo_y_offset += titulo_y_direcao * 0.5
    if titulo_y_offset > 10 or titulo_y_offset < -10:
        titulo_y_direcao *= -1
def animar_player():
    global frame, timer_anim, estado
    timer_anim += 1
    if esta_pulando: estado = "jump"
    elif andando: estado = "walk"
    else: estado = "idle"
    if estado == "idle": player.image = "character_green_idle"
    elif estado == "jump": player.image = "character_green_jump"
    elif estado == "walk":
        if timer_anim >= 18:
            frame = (frame + 1) % 2
            timer_anim = 0
        img = "right" if direcao == 1 else "left"
        player.image = f"character_green_walk_{img}_{'a' if frame == 0 else 'b'}"
def movimento_e_fisica_player():
    global velocidade_y, esta_pulando, direcao, andando
    andando = False
    if keyboard.left:
        player.x -= speed
        direcao = -1
        andando = True
    elif keyboard.right:
        player.x += speed
        direcao = 1
        andando = True
    if keyboard.space and not esta_pulando:
        velocidade_y = -18
        esta_pulando = True
    velocidade_y += gravidade
    player.y += velocidade_y
def colisao_vertical():
    global velocidade_y, esta_pulando
    pe_anterior = player.y - velocidade_y
    for p in plataformas:
        if velocidade_y >= 0:
            if player.x + 20 > p.x and player.x - 20 < p.x + p.width:
                if pe_anterior <= p.y and player.y >= p.y:
                    player.y = p.y
                    velocidade_y = 0
                    esta_pulando = False
                    return
    esta_pulando = True
def atualizar_camera():
    global scroll_x
    alvo = player.x - CAMERA_CENTER_X
    if alvo < 0: alvo = 0 
    scroll_x += (alvo - scroll_x) * 0.1
def on_mouse_move(pos):
    if game_state == MENU:
        btn_start.image = 'btn_start_hover' if btn_start.collidepoint(pos) else 'btn_start'
        btn_exit.image = 'btn_exit_hover' if btn_exit.collidepoint(pos) else 'btn_exit'
def on_mouse_down(pos):
    global game_state, scroll_x, velocidade_y, esta_pulando, estado
    if game_state == MENU:
        if btn_start.collidepoint(pos):
            montar_cenario()
            game_state = JOGANDO
            player.x = SPAWN_X
            player.y = SPAWN_Y
            scroll_x = 0 
            velocidade_y = 0
            esta_pulando = False
            estado = "idle"
        elif btn_exit.collidepoint(pos):
            exit()
titulo_y_offset = 0
titulo_y_direcao = 1
pgzrun.go()