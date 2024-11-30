import math
import random

import pygame

# Inicialização do pygame e configuração da janela de simulação
# Configura a resolução da tela, inicializa o relógio e a fonte para renderização de texto
pygame.init()
imagemBrocolis = pygame.image.load("Image/brocolis.png")
pygame.display.set_caption("Simulação de sistema solar")
pygame.display.set_icon(imagemBrocolis)
x, y = 1920, 1080
tela = pygame.display.set_mode((x, y))
clock = pygame.time.Clock()
pygame.font.init()
fonte = pygame.font.SysFont("Arial", 16)


# Constantes físicas utilizadas na simulação
G = 6.67430e-11
massaSol = 1.989e10
tamanhoSol = 1392.700
distanciaPlanetas = [57.9, 108.2, 149.6, 227.9, 778.5, 1432.0, 2867.0, 4515.0]
massaPlanetas = [3.28e3, 4.83e4, 5.98e4, 6.40e3, 1.90e7, 5.68e6, 8.67e5, 1.05e6]
tamanhoPlanetas = [4.879, 12.104, 12.756, 6.798, 142.964, 120.536, 51.118, 49.572]
coresPlanetas = [
    (169, 169, 169),
    (255, 215, 0),
    (0, 191, 255),
    (188, 39, 50),
    (255, 140, 0),
    (210, 180, 140),
    (0, 255, 255),
    (25, 25, 112),
]
nomesPlanetas = [
    "Mercúrio",
    "Vênus",
    "Terra",
    "Marte",
    "Júpiter",
    "Saturno",
    "Urano",
    "Netuno",
]


# Parâmetros de simulação
timeStep = 1e1  # Intervalo de tempo para cada iteração da simulação
movimento_speed = 10  # Velocidade de movimento da câmera com teclas WASD


# Configurações da área do cinturão de asteroides
ASTEROID_BELT_INNER_RADIUS = 300 + (tamanhoSol / 2)  # Milhões de km
ASTEROID_BELT_OUTER_RADIUS = 600 + (tamanhoSol / 2)  # Milhões de km
NUM_ASTEROIDS = 250


# Variáveis para controle de zoom e pan
zoom = 0.1
pan_x = 0  # Deslocamento horizontal da câmera
pan_y = 0  # Deslocamento vertical da câmera


# Posição inicial do Sol
posSol = pygame.Vector2(x // 2, y // 2)


# Inicialização dos planetas
# Cria uma lista de planetas com as devidas características necessárias (posição, velocidade etc.) para o desenvolvimento das funções
planetas = []
for i in range(len(massaPlanetas)):
    angulo = i * (math.pi / 4)
    distancia = distanciaPlanetas[i] + (tamanhoSol / 2)
    pos = posSol + pygame.Vector2(
        math.cos(angulo) * distancia, math.sin(angulo) * distancia
    )
    velOrb = math.sqrt(G * massaSol / distancia)
    vel = pygame.Vector2(-math.sin(angulo), math.cos(angulo)) * velOrb
    planetas.append(
        {
            "nome": nomesPlanetas[i],
            "massa": massaPlanetas[i],
            "tam": tamanhoPlanetas[i],
            "pos": pos,
            "antPos": pos - vel * timeStep,
            "raioOrbital": distancia,
            "vel": vel,
        }
    )


# Inicialização dos asteroides
# Gera uma população de asteroides no cinturão de asteroides com posições e velocidades aleatórias
asteroides = []
for _ in range(NUM_ASTEROIDS):
    raio_aleatorio = random.uniform(
        ASTEROID_BELT_INNER_RADIUS, ASTEROID_BELT_OUTER_RADIUS
    )
    angulo = random.uniform(0, 2 * math.pi)
    massa_asteroide = random.uniform(1e-6, 1e-4)
    tamanho_asteroide = random.uniform(0.1, 2)
    pos = posSol + pygame.Vector2(
        math.cos(angulo) * raio_aleatorio, math.sin(angulo) * raio_aleatorio
    )
    velOrb = math.sqrt(G * massaSol / raio_aleatorio)
    vel = pygame.Vector2(-math.sin(angulo), math.cos(angulo)) * velOrb
    asteroides.append(
        {
            "massa": massa_asteroide,
            "tam": tamanho_asteroide,
            "pos": pos,
            "antPos": pos - vel * timeStep,
            "vel": vel,
        }
    )


def fGrav(m1, p1, m2, p2):
    """
    Cálculo da força gravitacional

    1. Cria o vetor que parte da posição do planeta 1 (p1) para o planeta 2 (p2)
    2. Guarda a distância entre eles
    3. Calcula o módulo da força gravitacional resultante entre os planetas (guarda em 'magnitude')
    4. Normaliza o vetor (guarda em 'dir')
    5. Calcula e retorna     o vetor força gravitacional (aplica o módulo da força na direção do vetor entre os planetas com 'magnitude * dir')

    Parâmetros:
        m1, m2 (float): massa dos planetas a serem analisados na função
        p1, p2 (tupla): coordenadas da posição dos planetas a serem analisados na função

    Retorna:
        pygame.Vector2: vetor com magnitude da força gravitacional calculada entre dois planetas, apontando da posição de p1 para p2
    """

    vecDist = p1 - p2
    dist = vecDist.length()
    if dist == 0:
        return pygame.Vector2(0, 0)
    magnitude = G * (m1 * m2) / dist**2
    dir = vecDist.normalize()
    return magnitude * dir


def world_to_screen(pos):
    """
    Converte as coordenadas do planeta para as coordenadas da tela levando em consideração zoom e pan

    Parâmetro:
        pos (pygame.Vector2): coordenadas da posição original em espaço de simulação

    Retorna:
        pygame.Vector2: coordenadas da posição ajustada na tela de renderização
    """
    screen_x = (pos.x - x // 2) * zoom + x // 2 + pan_x
    screen_y = (pos.y - y // 2) * zoom + y // 2 + pan_y
    return pygame.Vector2(screen_x, screen_y)


def calc_velocidade(objeto):
    """
    Calcula a velocidade atual do objeto em km/s

    1. Armazena a posição atual e posição anterior
    2. Faz a diferença entre as duas e divide pelo tempo em que essa posição variou, chegando na nova velocidade
    3. Multiplica a velocidade por 1000 para manter a escala

    Parâmetro:
        objeto (dict): dicionário contendo a posição atual e anterior do objeto

    Retorna:
        float: velocidade do objeto em km/s
    """

    pos_atual = pygame.Vector2(objeto["pos"])
    pos_anterior = pygame.Vector2(objeto["antPos"])
    velocidade = (pos_atual - pos_anterior).length() / timeStep
    return velocidade * 1000


def update_antPos(objetos):
    """
    Atualiza a posição anterior dos objetos

    Usado para corrigir a posição anterior quando a velocidade é modificada

    Parâmetros:
        objetos (list): Lista de objetos (planetas ou asteroides) a serem atualizados
    """

    for objeto in objetos:
        objeto["antPos"] = objeto["pos"] - objeto["vel"] * timeStep


# Loop principal da simulação
running = True
while running:

    # Tratamento de eventos do Pygame
    for event in pygame.event.get():

        # Fechamento da janela
        if event.type == pygame.QUIT:
            running = False

        # Tratamento de zoom com a roda do mouse
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                zoom *= 1.1
            else:
                zoom /= 1.1

        # Reset do movimento relativo com botão do meio do mouse
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:
                pygame.mouse.get_rel()

        # Movimentação da câmera (pan) com botão do meio do mouse
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[1]:
                rel_x, rel_y = pygame.mouse.get_rel()
                pan_x += rel_x
                pan_y += rel_y

        # Controle de velocidade da simulação com teclas para cima/para baixo
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and timeStep < 1e2:
                timeStep *= 1.2
                update_antPos(planetas)
                update_antPos(asteroides)
            elif event.key == pygame.K_DOWN and timeStep > 0.1:
                timeStep /= 1.2
                update_antPos(planetas)
                update_antPos(asteroides)

    # Controle de movimento da câmera com teclas WASD
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        pan_y += movimento_speed
    if keys[pygame.K_s]:
        pan_y -= movimento_speed
    if keys[pygame.K_a]:
        pan_x += movimento_speed
    if keys[pygame.K_d]:
        pan_x -= movimento_speed

    # Simulação de física para planetas e asteroides
    all_objects = planetas + asteroides

    # Cálculo das forças gravitacionais e atualização de posições
    for i, objeto in enumerate(all_objects):

        # Força gravitacional do Sol
        fTotal = fGrav(massaSol, posSol, objeto["massa"], objeto["pos"])

        # Forças gravitacionais entre todos os objetos
        for j, objeto2 in enumerate(all_objects):
            if i != j:
                fTotal += fGrav(
                    objeto2["massa"],
                    objeto2["pos"],
                    objeto["massa"],
                    objeto["pos"],
                    # Isso faz com que alguns asteróides sejam estilingados por júpiter
                )

        # Cálculo de aceleração e atualização de posição
        accel = fTotal / objeto["massa"]
        nPos = 2 * objeto["pos"] - objeto["antPos"] + accel * (timeStep**2)
        objeto["antPos"] = objeto["pos"]
        objeto["pos"] = nPos
        objeto["vel"] = (nPos - objeto["antPos"]) / timeStep

    # Renderização
    tela.fill((0, 0, 0))

    # Variável para armazenar informações a serem exibidas
    info_to_display = None

    # Desenha o Sol
    sol_pos = world_to_screen(posSol)
    raio_sol = max(2, int((tamanhoSol / 2) * zoom))
    pygame.draw.circle(tela, (255, 255, 0), (int(sol_pos.x), int(sol_pos.y)), raio_sol)

    # Verifica se o mouse está sobre o Sol para exibir informações
    mouse_pos = pygame.mouse.get_pos()
    if (sol_pos - pygame.Vector2(mouse_pos)).length() < raio_sol:
        info_to_display = {
            "pos": (int(sol_pos.x) + raio_sol + 5, int(sol_pos.y) - 30),
            "text": [
                "Sol",
                f"Massa: {massaSol*1e20:.2e} kg",
                f"Diâmetro: {tamanhoSol:.1f} mil km",
            ],
        }

    # Desenha as órbitas dos planetas
    for planeta in planetas:
        raio_orbital = planeta["raioOrbital"] * zoom
        pygame.draw.circle(
            tela, (30, 30, 30), (int(sol_pos.x), int(sol_pos.y)), int(raio_orbital), 1
        )

    # Desenha os planetas
    for i, planeta in enumerate(planetas):
        cor = coresPlanetas[i]
        planeta_pos = world_to_screen(planeta["pos"])
        raio = max(2, int((planeta["tam"] / 2) * zoom))
        pygame.draw.circle(tela, cor, (int(planeta_pos.x), int(planeta_pos.y)), raio)

        # Verifica se o mouse está sobre o planeta para exibir informações
        if (planeta_pos - pygame.Vector2(mouse_pos)).length() < raio:
            vel_atual = calc_velocidade(planeta)
            info_to_display = {
                "pos": (int(planeta_pos.x) + raio + 5, int(planeta_pos.y) - 50),
                "text": [
                    f"Nome: {planeta['nome']}",
                    f"Massa: {planeta['massa']*1e20:.2e} kg",
                    f"Distância do Sol: {planeta['raioOrbital']:.1f} milhões km",
                    f"Velocidade: {vel_atual:.2f} km/s",
                    f"Diâmetro: {planeta['tam']:.3f} mil km",
                ],
            }

    # Desenha os asteroides
    for asteroide in asteroides:
        asteroide_pos = world_to_screen(asteroide["pos"])
        raio = max(1, int(asteroide["tam"] * zoom * 0.5))
        pygame.draw.circle(
            tela, (150, 150, 150), (int(asteroide_pos.x), int(asteroide_pos.y)), raio
        )

    # Desenha as informações
    if info_to_display:
        max_width = max(fonte.size(texto)[0] for texto in info_to_display["text"])
        info_height = len(info_to_display["text"]) * 20
        info_surface = pygame.Surface((max_width + 10, info_height + 10))
        info_surface.fill((50, 50, 50))

        for i, texto in enumerate(info_to_display["text"]):
            texto_surface = fonte.render(texto, True, (255, 255, 255))
            info_surface.blit(texto_surface, (5, 5 + i * 20))

        tela.blit(info_surface, info_to_display["pos"])

    # Desenha informações de controle na tela
    controles = [
        "Controles:",
        "WASD - Mover câmera",
        "Roda do mouse - Zoom",
        "Botão do meio do mouse - Pan",
        "Setas cima/baixo - Ajustar velocidade da simulação",
        f"TimeStep atual: {timeStep:.2e}",
        f"Asteroides: {len(asteroides)}",
    ]

    for i, texto in enumerate(controles):
        texto_surface = fonte.render(texto, True, (255, 255, 255))
        tela.blit(texto_surface, (10, 10 + i * 20))

    pygame.display.flip()
    clock.tick(240)

pygame.quit()
