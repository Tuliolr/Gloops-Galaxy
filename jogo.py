import pgzrun

# 1. Configurações da Janela
WIDTH = 800
HEIGHT = 600

# 2. Actors e Variáveis de Animação
# O background deve ser do tamanho da tela (800x600)
background = 'fase_bg' 

# O player começa com a imagem 'player_idle'
player = Actor('character_green_idle', (100, 500))

# Variáveis para controlar a animação
frames_andando = ['character_green_walk_a', 'character_green_walk_b']
timer_animacao = 0
indice_frame = 0

def draw():
    # Desenha o fundo cobrindo toda a tela
    screen.blit(background, (0, 0))
    # Desenha o jogador
    player.draw()

def update():
    global timer_animacao, indice_frame
    
    andando = False

    # 3. Lógica de Movimentação
    if keyboard.left and player.left > 0:
        player.x -= 4
        andando = True
    if keyboard.right and player.right < WIDTH:
        player.x += 4
        andando = True

    # 4. Lógica de Animação
    if andando:
        timer_animacao += 1
        # A cada 10 frames, trocamos a imagem para criar o efeito de movimento
        if timer_animacao > 10:
            indice_frame = (indice_frame + 1) % len(frames_andando)
            player.image = frames_andando[indice_frame]
            timer_animacao = 0
    else:
        # Se parado, volta para a imagem inicial
        player.image = 'character_green_idle'

pgzrun.go()