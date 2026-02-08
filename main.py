import pgzrun
import random
from pygame import Rect
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
porta_base = Actor('door_closed',(3000, 200))
porta_topo = Actor('door_closed_top',(3000, 200))
porta_base.anchor = ('left', 'bottom')
porta_topo.anchor = ('left', 'bottom')
porta_pos_x = 3250
porta_pos_y = 540
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

        for p in plataformas:
            draw_actor_scroll(p, scroll_x)

        for lava in lavas:
            draw_actor_scroll(lava, scroll_x)
            

        for slime in inimigos:
            draw_actor_scroll(slime, scroll_x)
            screen.draw.rect(Rect(slime.x - 20 - scroll_x, slime.y - 30, 40, 30), "red")

        draw_actor_scroll(Actor(key.image, (key.x, key.y + key_y_offset)), scroll_x)
        draw_actor_scroll(Actor(porta_base.image, (porta_pos_x, porta_pos_y)), scroll_x)
        draw_actor_scroll(Actor(porta_topo.image, (porta_pos_x, porta_pos_y - 64)), scroll_x)
        draw_actor_scroll(player, scroll_x)
        hud_helmet.draw()
        hud_character3.draw()
        hud_character0.draw()
        hud_key.draw()
def update():
    global invencivel, velocidade_y
    if game_state == MENU:
        animar_titulo_menu()
        return
    if invencivel > 0: invencivel -= 1    
    verificar_lava()
    
    if keyboard.space and not esta_pulando:
        velocidade_y = -18
        sounds.sfx_jump_high.play() 
        
       
    movimento_horizontal()
    velocidade_y += gravidade
    player.y += velocidade_y
    colisao_vertical()
    verificar_inimigos()
    if player.colliderect(key):
        key.x = -1000
    if player.colliderect(porta_base) and key.x < 0:
        print("VOCÊ VENCEU!")

    atualizar_camera()
    animar_player()
    animar_objetos()
def draw_actor_scroll(actor, scroll_x):
    screen.blit(actor.image, (actor.left - scroll_x, actor.top))
    
   # screen.draw.rect(Rect((actor.left - scroll_x, actor.top), (actor.width, actor.height)), "red")
# AUXILIARES DE CENARIO
def eh_lava(indice, zonas_lava):
    for inicio, fim in zonas_lava:
        if inicio <= indice <= fim:
            return True
    return False
def criar_plataforma_longa(x_inicial, y, blocos_do_meio):
    largura = 64
    total_blocos = blocos_do_meio + 2
    
    # Criamos um ID único para cada plataforma para que os blocos saibam que são do mesmo grupo
    grupo_id = random.random() 
    vel_y = random.uniform(0.5, 1.5) * random.choice([-1, 1])
    
    for i in range(total_blocos):
        if i == 0: img = 'plat_esq'
        elif i == total_blocos - 1: img = 'plat_dir'
        else: img = 'plat_meio'
        
        p = Actor(img, (x_inicial + i * largura, y))
        p.anchor = ('left', 'top')
        
        # Atributos para movimento sincronizado
        p.vel_y = vel_y
        p.limite_sup = y - 150
        p.limite_inf = y + 150
        p.movel = True # Marcamos como móvel
        
        plataformas.append(p)

def atualizar_plataformas_moveis():
    for p in plataformas:
        # Move a plataforma
        p.y += p.vel_y
        
        # Inverte a direção se passar dos limites
        if p.y < p.limite_sup or p.y > p.limite_inf:
            p.vel_y *= -1
def montar_cenario():
    global plataformas, lavas
    plataformas.clear()
    lavas.clear()
    inimigos.clear() 
    largura = 64
    pos_chao_y = 800 

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

    # Inimigos EXATAMENTE no nível do chão 
    criar_slime_fire(x=500, y=740, x_min=150, x_max=650)
    criar_slime_fire(x=1500, y=740, x_min=1300, x_max=1700)
    criar_slime_fire(x=2800, y=740, x_min=2400, x_max=2950)
    criar_plataforma_longa(500, 650, 2)
    criar_plataforma_longa(850, 500, 3)
    criar_plataforma_longa(1250, 550, 2)
    criar_plataforma_longa(1650, 550, 2) 
    criar_plataforma_longa(2100, 500, 3) 
    criar_plataforma_longa(2550, 500, 2) 
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
    # --- SLIMES DE SPIKE NAS PLATAFORMAS INFERIORES ---
    # criar_slime_spike(x=600, y=400, x_min=550, x_max=750)
    criar_slime_spike(x=950, y=450, x_min=950, x_max=1100) #ok
    criar_slime_spike(x=1700, y=500, x_min=1650, x_max=1800) #ok
    criar_slime_spike(x=2600, y=450, x_min=2560, x_max=2740)#ok
    # --- SLIMES DE SPIKE NAS PLATAFORMAS SUPERIORES ---
    
    # Plataforma (150, 210, 1) -> Largura total 192px (3 blocos)
    criar_slime_spike(x=200, y=160, x_min=160, x_max=330)
    
    # Plataforma (950, 250, 2) -> Largura total 256px (4 blocos)
    #criar_slime_spike(x=1000, y=200, x_min=970, x_max=1100)
    
    # Plataforma (1850, 250, 1)
    criar_slime_spike(x=1900, y=200, x_min=1860, x_max=1950)
    
    # Plataforma (2300, 200, 2)
   # criar_slime_spike(x=2500, y=150, x_min=2310, x_max=2540)
    
    # --- PLATAFORMAS EXTREMAS (LA NO TOPO) ---
    
    # criar_slime_spike(x=1300, y=80, x_min=1260, x_max=1490)
    
    # Plataforma (2600, 130, 2)
    criar_slime_spike(x=2700, y=130, x_min=2610, x_max=2840)
   

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
            sounds.sfx_die.play()
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
    lado = "right" if direcao == 1 else "left"
    # ESTADO: PULO
    if esta_pulando:
        estado = "jump"
        player.image = f"character_green_jump_{lado}" 
    # ESTADO: ANDANDO
    elif andando:
        estado = "walk"
        if timer_anim >= 10: 
            frame = (frame + 1) % 2
            timer_anim = 0
        
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
        direcao = -1 
        andando = True
    elif keyboard.right:
        player.x += speed
        direcao = 1  
        andando = True
def animar_objetos():
    global key_y_offset, key_y_direcao
    key_y_offset += key_y_direcao * 0.5 
    if key_y_offset > 10 or key_y_offset < -5:
        key_y_direcao *= -1
    for slime in inimigos:
        atualizar_slime(slime)
        andando = True
        
def colisao_vertical():
    global velocidade_y, esta_pulando
    if velocidade_y < 0:
        esta_pulando = True
        return
    for p in plataformas:
        if player.x + 15 > p.left and player.x - 15 < p.right:
            if player.y <= p.top + (velocidade_y + 2) and player.y >= p.top - 5:
                player.y = p.top 
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
            sounds.sfx_bump.play()
        # O correto para sons curtos é usar sounds, não music
    
        
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
def tem_chao_firme(x_verificar):
    for p in plataformas:
        if x_verificar >= p.left and x_verificar <= p.right:
            return True
    return False
def atualizar_slime(slime):
    # --- 1. MOVIMENTO HORIZONTAL (PATRULHA) ---
    # O slime se move na direção atual com sua velocidade específica
    slime.x += slime.velocidade * slime.direcao

    # Verifica se atingiu os limites de patrulha para inverter a direção
    if slime.x >= slime.x_max:
        slime.direcao = -1
    elif slime.x <= slime.x_min:
        slime.direcao = 1

    # --- 2. MOVIMENTO VERTICAL (ACOMPANHAR PLATAFORMA) ---
    # Percorremos todas as plataformas para ver se o slime está pisando em uma móvel
    for p in plataformas:
        # Verifica se o slime está dentro da largura desta plataforma (X)
        if p.left <= slime.x <= p.right:
            # Verifica se o slime está encostado no topo da plataforma (Y)
            # Usamos uma margem de 10 pixels para garantir a detecção
            if abs(slime.y - p.top) < 10:
                # O "Pulo do Gato": O Slime assume o Y exato do topo da plataforma
                # Se a plataforma sobe, o slime sobe. Se desce, ele desce.
                slime.y = p.top
                break # Encontrou o chão, não precisa checar as outras plataformas

    # --- 3. ANIMAÇÃO ---
    # Controla a troca de frames (a/b) e a direção da imagem (left/right)
    slime.anim_timer += 1
    if slime.anim_timer >= 10:
        slime.anim_timer = 0
        slime.anim_frame = 1 - slime.anim_frame
        
        # Define se o nome terá "right" ou "left"
        lado = "right" if slime.direcao == 1 else "left"
        # Define se será o frame "a" ou "b"
        frame_img = "a" if slime.anim_frame == 0 else "b"
        
        # Define o prefixo (spike ou fire) baseado no atributo que criamos
        prefixo = "slime_spike" if hasattr(slime, 'tipo') and slime.tipo == "spike" else "slime_fire"
        
        # Monta o nome final: ex: slime_spike_walk_left_a
        slime.image = f"{prefixo}_walk_{lado}_{frame_img}"
def criar_slime_spike(x, y, x_min, x_max):
    try:
        slime = Actor('slime_spike_walk_right_a', (x, y))
    except:
        slime = Actor('chao', (x, y))

    slime.anchor = ('center', 'bottom')
    slime.x_min = x_min
    slime.x_max = x_max
    slime.velocidade = 1.0
    slime.direcao = 1
    slime.anim_timer = 0
    slime.anim_frame = 0
    slime.tipo = "spike" 

    inimigos.append(slime)
def verificar_inimigos():
    global invencivel
    if invencivel > 0: return 
    
    # Criamos uma hitbox para o player um pouco mais estreita que a imagem
    player_hb = Rect(player.x - 12, player.y - 40, 24, 40)

    for slime in inimigos:
        # Criamos a hitbox do slime baseada no centro dele
        # Ajustamos para ser um quadrado pequeno na base do slime
        # (x_centro - 15, y_chao - 25, largura 30, altura 25)
        slime_hb = Rect(slime.x - 15, slime.y - 25, 30, 25)

        if player_hb.colliderect(slime_hb):
            try: sounds.sfx_die.play()
            except: pass
            # resetar_player()
            break
titulo_y_offset = 0
titulo_y_direcao = 1
pgzrun.go()