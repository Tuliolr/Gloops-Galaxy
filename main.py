import pgzrun
import random
from pygame import Rect
# CONFIGURACOES
WIDTH = 1000
HEIGHT = 900
MENU = 0
JOGANDO = 1
VENCEU = 2
PERDEU = 3
tela_alpha = 0
game_state = MENU
timer_vitoria = 0
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
hud_key = Actor('hud_key_blue', (180, 50))
key = Actor('key_blue')
key.pos = (210, 165)
porta_base = Actor('door_closed',(3000, 200))
porta_topo = Actor('door_closed_top',(3000, 200))
porta_base.anchor = ('left', 'bottom')
porta_topo.anchor = ('left', 'bottom')
porta_pos_x = 3250
porta_pos_y = 580
vidas = 3
chaves = 0
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
    screen.draw.text(f"Plataformas: {len(plataformas)}", (10, 10))
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
    elif game_state in [JOGANDO, VENCEU, PERDEU]:
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
        hud_key.draw()
        try:
            Actor(f"hud_{vidas}", (125, 50)).draw()
            Actor(f"hud_{chaves}", (220, 50)).draw()
        except:
            screen.draw.text(str(vidas), (125, 50), fontsize=50, color="white")
        if key.x < 0: 
            hud_key.draw()
        if game_state == VENCEU or game_state == PERDEU:
            overlay = Rect(0, 0, WIDTH, HEIGHT)
            screen.draw.filled_rect(overlay, (0, 0, 0)) 
            texto = "VOCE VENCEU!" if game_state == VENCEU else "GAME OVER"
            cor = "gold" if game_state == VENCEU else "red"
            valor_alpha = min(1.0, tela_alpha / 150)
            screen.draw.text(texto, center=(WIDTH//2, HEIGHT//2), 
                             fontsize=100, color=cor, alpha=valor_alpha, shadow=(2,2))
            screen.draw.text("Pressione ESC para Voltar ao Menu", 
                             center=(WIDTH//2, HEIGHT//2 + 100), 
                             fontsize=30, color="white", alpha=valor_alpha)
def update():
    global game_state, tela_alpha, invencivel, velocidade_y, chaves, timer_vitoria
    
    if game_state == MENU:
        animar_titulo_menu()
        return
    if game_state == JOGANDO:
        if invencivel > 0: invencivel -= 1    
        verificar_lava()
        if keyboard.space and not esta_pulando:
            velocidade_y = -18
            try: sounds.sfx_jump_high.play() 
            except: pass  
        movimento_horizontal()
        velocidade_y += gravidade
        player.y += velocidade_y
        colisao_vertical()
        verificar_inimigos()
        if player.colliderect(key):
            if key.x != -1000:
                key.x = -1000
                chaves = 1
                print("Chave coletada!") # DEBUG
                try: sounds.sfx_gem.play() 
                except: pass
        if player.colliderect(porta_base) and chaves >= 1:
            print("Entrou na porta! Mudando para VENCEU") # DEBUG
            game_state = VENCEU
            tela_alpha = 0 
            timer_vitoria = 0
        atualizar_camera()
        animar_player()
        animar_objetos()
        atualizar_plataformas_moveis()
    elif game_state in [VENCEU, PERDEU]:
        timer_vitoria += 1
        
        if tela_alpha < 150:
            tela_alpha += 5
        if keyboard.escape and timer_vitoria > 60:
            print("Voltando ao menu pelo ESC") # DEBUG
            resetar_jogo_completo()
            game_state = MENU
            tela_alpha = 0
            timer_vitoria = 0
def draw_actor_scroll(actor, scroll_x):
    if actor == player and invencivel > 0:
        if (invencivel // 5) % 2 == 0: return 
    pos_original = actor.pos
    actor.x -= scroll_x
    actor.draw()
    actor.pos = pos_original
def eh_lava(indice, zonas_lava):
    for inicio, fim in zonas_lava:
        if inicio <= indice <= fim:
            return True
    return False
def criar_plataforma_longa(x_inicial, y, blocos_do_meio):
    largura = 64
    total_blocos = blocos_do_meio + 2
    grupo_id = random.random() 
    vel_y = random.uniform(0.5, 1.5) * random.choice([-1, 1])
    for i in range(total_blocos):
        if i == 0: img = 'plat_esq'
        elif i == total_blocos - 1: img = 'plat_dir'
        else: img = 'plat_meio'
        p = Actor(img, (x_inicial + i * largura, y))
        p.anchor = ('left', 'top')
        p.vel_y = vel_y
        p.limite_sup = y - 150
        p.limite_inf = y + 150
        p.movel = True 
        plataformas.append(p)
def atualizar_plataformas_moveis():
    for p in plataformas:
        if hasattr(p, 'movel') and p.movel:
            p.y += p.vel_y
            if p.y < p.limite_sup or p.y > p.limite_inf:
                p.vel_y *= -1
def montar_cenario():
    global plataformas, lavas, inimigos
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
    # Inimigos EXATAMENTE no nivel do chao
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
    # SLIMES DE SPIKE NAS PLATAFORMAS INFERIORES
    criar_slime_spike(x=950, y=450, x_min=950, x_max=1100) 
    criar_slime_spike(x=1700, y=500, x_min=1650, x_max=1800)
    criar_slime_spike(x=2600, y=450, x_min=2560, x_max=2740)
    # SLIMES DE SPIKE NAS PLATAFORMAS SUPERIORES 
    criar_slime_spike(x=1900, y=200, x_min=1860, x_max=1950)
    criar_slime_spike(x=2500, y=150, x_min=2310, x_max=2540)
    # PLATAFORMAS EXTREMAS (LA NO TOPO)
    criar_slime_spike(x=1300, y=80, x_min=1260, x_max=1490)
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
            perder_vida()
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
        if player.x > 20: 
            player.x -= speed
            direcao = -1 
            andando = True
    elif keyboard.right:
        player.x += speed
        direcao = 1  
        andando = True
def animar_objetos():
    global key_y_offset, key_y_direcao, porta_pos_y 
    key_y_offset += key_y_direcao * 0.5 
    if key_y_offset > 10 or key_y_offset < -5:
        key_y_direcao *= -1
    if key.x > 0: 
        for p in plataformas:
            if p.left <= key.x <= p.right:
                if abs(key.y - p.top) < 20:
                    key.y = p.top
                    break
    for p in plataformas:
        if p.left <= porta_pos_x <= p.right:
            if abs(porta_pos_y - p.top) < 20:
                porta_pos_y = p.top
                break
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
    global game_state, vidas
    if game_state == MENU:
        if btn_start.collidepoint(pos):
            vidas = 3 
            montar_cenario() 
            game_state = JOGANDO
            resetar_player()
            try: sounds.sfx_bump.play()
            except: pass
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
    slime.x += slime.velocidade * slime.direcao
    if slime.x >= slime.x_max:
        slime.direcao = -1
    elif slime.x <= slime.x_min:
        slime.direcao = 1
    for p in plataformas:
        if p.left <= slime.x <= p.right:
            if abs(slime.y - p.top) < 10:
                slime.y = p.top
                break 
    slime.anim_timer += 1
    if slime.anim_timer >= 10:
        slime.anim_timer = 0
        slime.anim_frame = 1 - slime.anim_frame
        lado = "right" if slime.direcao == 1 else "left"
        frame_img = "a" if slime.anim_frame == 0 else "b"
        prefixo = "slime_spike" if hasattr(slime, 'tipo') and slime.tipo == "spike" else "slime_fire"
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
    if invencivel > 0: return 
    player_hb = Rect(player.x - 12, player.y - 40, 24, 40)
    for slime in inimigos:
        slime_hb = Rect(slime.x - 15, slime.y - 25, 30, 25)
        if player_hb.colliderect(slime_hb):
            perder_vida()
            break
def perder_vida():
    global vidas, game_state, invencivel,tela_alpha
    if invencivel > 0: return 
    vidas -= 1
    if vidas == 0:
        game_state = PERDEU
        tela_alpha = 255
    else:
        try: sounds.sfx_die.play()
        except: pass
        invencivel = 100 
        resetar_player()
def resetar_jogo_completo():
    global vidas, game_state, scroll_x, chaves
    vidas = 3
    chaves = 0
    key.x = 210  
    key.y = 150
    resetar_player()
    montar_cenario()
titulo_y_offset = 0
titulo_y_direcao = 1
pgzrun.go()