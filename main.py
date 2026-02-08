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
SPAWN_Y = 730
# OBJETOS
btn_start = Actor('btn_start', (500, 250))
btn_exit = Actor('btn_exit', (500, 400))
player = Actor('character_green_idle',(SPAWN_X, SPAWN_Y))
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
inimigos = []
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
        screen.draw.text("GLOOP'S GALAXY", center=(WIDTH // 2, 120 + titulo_y_offset),
                         fontsize=100, color="green", shadow=(2, 2), scolor="darkgreen")

    elif game_state == JOGANDO:
        try:
            screen.blit('fase_bg', (0, 0))
        except:
            screen.fill((50, 150, 200))

        # Desenha Plataformas
        for p in plataformas:
            draw_actor_scroll(p, scroll_x)

        # Desenha Lavas
        for lava in lavas:
            draw_actor_scroll(lava, scroll_x)

        # Desenha inimigos
        for slime in inimigos:
            draw_actor_scroll(slime, scroll_x)

        # Desenha Chave com animação vertical
        draw_actor_scroll(Actor(key.image, (key.x, key.y + key_y_offset)), scroll_x)

        # Desenha Porta
        draw_actor_scroll(Actor(porta_base.image, (porta_pos_x, porta_pos_y)), scroll_x)
        draw_actor_scroll(Actor(porta_topo.image, (porta_pos_x, porta_pos_y - 64)), scroll_x)

        # Desenha Player
        draw_actor_scroll(player, scroll_x)

        # HUD (não sofre scroll)
        hud_helmet.draw()
        hud_character3.draw()
        hud_character0.draw()
        hud_key.draw()
def update():
    global invencivel, velocidade_y
    
    if game_state == MENU:
        animar_titulo_menu()
        return

    # 1. Vida e Dano
    if invencivel > 0: invencivel -= 1    
    verificar_lava()
    
    # 2. Input de pulo (SÓ o pulo)
    if keyboard.space and not esta_pulando:
        velocidade_y = -18
        # esta_pulando vira True automaticamente na função de colisão

    # 3. Movimento Horizontal
    movimento_horizontal()
    
    # 4. Física Vertical (Gravidade)
    velocidade_y += gravidade
    player.y += velocidade_y
    
    # 5. RESOLUÇÃO DE COLISÃO (Corrige a posição antes de desenhar)
    colisao_vertical()
    
    # 6. Itens e Vitórias
    if player.colliderect(key):
        key.x = -1000
    if player.colliderect(porta_base) and key.x < 0:
        print("VOCÊ VENCEU!")

    # 7. Finalização visual
    atualizar_camera()
    animar_player()
    animar_objetos()
def draw_actor_scroll(actor, scroll_x):
    # Desenha o ator na posição relativa à câmera sem alterar o X real dele
    screen.blit(actor.image, (actor.left - scroll_x, actor.top))
    
    # DEBUG: Remova as aspas abaixo para ver as caixas de colisão
    screen.draw.rect(Rect((actor.left - scroll_x, actor.top), (actor.width, actor.height)), "red")
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
    inimigos.clear() # Limpa inimigos ao reiniciar
    largura = 64
    pos_chao_y = 800 # Nível principal do chão

    zonas_lava = [(12, 18), (30, 36), (50, 60)] 

    for i in range(150): 
        x = i * largura
        if eh_lava(i, zonas_lava):
            lava = Actor('lava_top', (x, pos_chao_y))
            lava.anchor = ('left', 'top')
            lavas.append(lava)
        else:
            bloco = Actor('chao', (x, pos_chao_y))
            bloco.anchor = ('left', 'top')
            plataformas.append(bloco)

    # Inimigos EXATAMENTE no nível do chão (pos_chao_y)
    criar_slime_fire(x=500, y=740, x_min=450, x_max=650)
    criar_slime_fire(x=1000, y=740, x_min=950, x_max=1150)
    criar_slime_fire(x=2800, y=740, x_min=2750, x_max=2950)
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
    
    # Define o sufixo da direção para o nome da imagem
    lado = "right" if direcao == 1 else "left"
    
    # ESTADO: PULO
    if esta_pulando:
        estado = "jump"
        player.image = f"character_green_jump_{lado}" # Ex: character_green_jump_left
    
    # ESTADO: ANDANDO
    elif andando:
        estado = "walk"
        if timer_anim >= 10: # Velocidade da animação (menor = mais rápido)
            frame = (frame + 1) % 2
            timer_anim = 0
        
        # Alterna entre frame a e b
        letra_frame = 'a' if frame == 0 else 'b'
        player.image = f"character_green_walk_{lado}_{letra_frame}"
    
    # ESTADO: PARADO (IDLE)
    else:
        estado = "idle"
        player.image = f"character_green_idle"
def movimento_horizontal():
    global direcao, andando
    andando = False
    if keyboard.left:
        player.x -= speed
        direcao = -1  # Esquerda
        andando = True
    elif keyboard.right:
        player.x += speed
        direcao = 1   # Direita
        andando = True
def animar_objetos():
    global key_y_offset, key_y_direcao
    # Animação da Chave
    key_y_offset += key_y_direcao * 0.5 
    if key_y_offset > 10 or key_y_offset < -5:
        key_y_direcao *= -1
    # Movimento dos Inimigos
    for slime in inimigos:
        atualizar_slime(slime)
        andando = True
def colisao_vertical():
    global velocidade_y, esta_pulando
    
    # Se ele está subindo (velocidade negativa), não checamos colisão com o chão
    if velocidade_y < 0:
        esta_pulando = True
        return

    for p in plataformas:
        # Verifica se o Player está alinhado horizontalmente com a plataforma
        if player.x + 15 > p.left and player.x - 15 < p.right:
            # Verifica se o pé do player passou do topo da plataforma, 
            # mas não atravessou a plataforma inteira ainda
            if player.y <= p.top + (velocidade_y + 2) and player.y >= p.top - 5:
                player.y = p.top  # Trava o player no topo
                velocidade_y = 0  # Zera a queda
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
def criar_slime_fire(x, y, x_min, x_max):
    try:
        slime = Actor('slime_fire_walk_right_a', (x, y))
    except:
        slime = Actor('chao', (x, y))  

    slime.anchor = ('center', 'bottom')
    slime.x_min = x_min
    slime.x_max = x_max
    slime.velocidade = 1.2
    slime.direcao = 1
    slime.anim_timer = 0
    slime.anim_frame = 0

    inimigos.append(slime)

def atualizar_slime(slime):
    slime.x += slime.velocidade * slime.direcao

    if slime.x >= slime.x_max:
        slime.direcao = -1
    elif slime.x <= slime.x_min:
        slime.direcao = 1

    # Animação
    slime.anim_timer += 1
    if slime.anim_timer >= 10:
        slime.anim_timer = 0
        slime.anim_frame = 1 - slime.anim_frame
        # Use o nome correto da sua imagem (ajustado para inverter se necessário)
        img_nome = 'slime_fire_walk_right_a' if slime.anim_frame == 0 else 'slime_fire_walk_right_b'
        slime.image = img_nome

titulo_y_offset = 0
titulo_y_direcao = 1
pgzrun.go()