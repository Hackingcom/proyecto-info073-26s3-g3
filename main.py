# Importamos módulos requeridos
import os
import random

import pygame

# Estados del juego
ESTADO_INICIO = "inicio"
ESTADO_INSTRUCCIONES = "instrucciones"
ESTADO_JUGANDO = "jugando"
ESTADO_DERROTA = "derrota"
ESTADO_VICTORIA = "victoria"

# Rutas a la carpeta de imágenes de pantallas
DIR_PANTALLAS = os.path.join(os.path.dirname(__file__), "data", "pantallas")


DIR_SONIDOS = os.path.join(os.path.dirname(__file__), "data", "sonidos")


# Se específica el nombre del archivo para cada imagen de pantalla.
# El formato de imagen utilizado puede ser PNG, JPG/JPEG, BMP, o GIF.
PANTALLA_INICIO = "pantalla_inicio.bmp"
PANTALLA_INSTRUCCIONES = "pantalla_instrucciones.bmp"
PANTALLA_VICTORIA = "pantalla_victoria.bmp"
PANTALLA_DERROTA = "pantalla_derrota.bmp"

# Para evitar que el jugador se mueva demasiado rápido
RETRASO = 200

# Códigos de cada elemento del tablero
VACIO = 0
JUGADOR = 1
MANZANA = 2



# Obstaculos NUEVOS
VOLCANO = 3
LAVA = 4
HOYO = 5
BURBUJA = 6

# Objetos 
PROTEINA = 7
ESCUDO = 8

# Tamaño del tablero
# Si se cambian estas constantes, se debe modificar la definición
# del tablero que se encuentra en función reiniciar().
FILAS = 15
COLUMNAS = 15

VIDAS_MAXIMAS = 3

# Configuración de obstaculos

CANT_VOLCANO = 10
CANT_HOYO = 15
CANT_BURBUJA = 15
CANT_PROTEINA = 2

# Tamaño min/max de lago de lava
LAVA_MIN = 10
LAVA_MAX = 20

# Cantidad min/max de lago de lava
LAGOS_MIN = 1
LAGOS_MAX = 3

# Cuantas manzanas se deben comer para ganar
MANZANAS_PARA_GANAR = 3

# Celdas que conforman el borde del tablero
BORDE = (
    [(c, 0) for c in range(COLUMNAS)]
    + [(c,FILAS - 1) for c in range(COLUMNAS)]
    + [(0, f) for f in range(1, FILAS - 1)]
    + [(COLUMNAS - 1, f) for f in range(1, FILAS - 1)]
)

def aparecer_aleatorio(tablero, id_elem, incluir_borde=True):
    """
    Coloca un elemento en una casilla vacía aleatoria del tablero.
    """

    vacios = []

    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            elem_pos = tablero[fila][columna]

            if elem_pos == VACIO:

                if id_elem in (VOLCANO, HOYO, BURBUJA, JUGADOR):
                    
                    if al_lado_de_lava(tablero, columna, fila):
                        continue

                    if al_lado_del_mismo(tablero, columna, fila, id_elem):
                        continue

                vacios.append((columna, fila))

    if not incluir_borde:
        vacios = [pos for pos in vacios if pos not in BORDE]

    if len(vacios) == 0:
        return -1, -1

    columna, fila = random.choice(vacios)
    tablero[fila][columna] = id_elem

    return columna, fila



def generar_lago_lava(tablero, cantidad):
    
    """
    Genera un lago de lava con forma irregular
    """

    columna, fila = aparecer_aleatorio(tablero, LAVA, incluir_borde=False)

    if columna == -1:
        return
    
    posiciones = [(columna,fila)]

    while len(posiciones) < cantidad:

        col, fil = random.choice(posiciones)

        vecinos = [
            (col + 1, fil),
            (col - 1, fil),
            (col, fil + 1),
            (col, fil - 1)
        ]

        random.shuffle(vecinos)

        for nueva_col, nueva_fil in vecinos:

            if 0 <= nueva_col < COLUMNAS and 0 <= nueva_fil < FILAS:

                if tablero[nueva_fil][nueva_col] == VACIO:

                    tablero[nueva_fil][nueva_col] = LAVA
                    posiciones.append((nueva_col, nueva_fil))
                    break



def dibujar_bordes_lava(screen, tablero, imagenes, ancho_elem, alto_elem):

    for fila in range(FILAS):

        for columna in range(COLUMNAS):

            if tablero[fila][columna] == LAVA:
                continue
            if tablero[fila][columna] == VOLCANO:
                continue
            if tablero[fila][columna] == HOYO:
                continue

            x = columna * ancho_elem
            y = fila * alto_elem

            arriba = fila > 0 and tablero[fila - 1][columna] == LAVA
            abajo = fila < FILAS - 1 and tablero[fila + 1][columna] == LAVA
            izquierda = columna > 0 and tablero[fila][columna - 1] == LAVA
            derecha = columna < COLUMNAS - 1 and tablero[fila][columna + 1] == LAVA

            if not (arriba or abajo or izquierda or derecha):
                continue

            if arriba and abajo and izquierda and derecha:
                screen.blit(imagenes["lava_all_sides"], (x, y))
            elif arriba and izquierda and derecha:
                screen.blit(imagenes["lava_top_both"], (x, y))
            elif abajo and izquierda and derecha:
                screen.blit(imagenes["lava_bottom_both"], (x, y))
            elif izquierda and arriba and abajo:
                screen.blit(imagenes["lava_left_both"], (x, y))
            elif derecha and arriba and abajo:
                screen.blit(imagenes["lava_right_both"], (x, y))
            elif arriba and izquierda:
                screen.blit(imagenes["lava_top_left"], (x, y))
            elif arriba and derecha:
                screen.blit(imagenes["lava_top_right"], (x, y))
            elif abajo and izquierda:
                screen.blit(imagenes["lava_bottom_left"], (x, y))
            elif abajo and derecha:
                screen.blit(imagenes["lava_bottom_right"], (x, y))
            elif arriba and abajo:
                screen.blit(imagenes["lava_top_bottom"], (x, y))
            elif izquierda and derecha:
                screen.blit(imagenes["lava_left_right"], (x, y))
            elif arriba:
                screen.blit(imagenes["lava_top"], (x, y))
            elif abajo:
                screen.blit(imagenes["lava_bottom"], (x, y))
            elif izquierda:
                screen.blit(imagenes["lava_left"], (x, y))
            elif derecha:
                screen.blit(imagenes["lava_right"], (x, y))



def al_lado_de_lava(tablero, columna, fila):

    vecinos = [
        (columna + 1, fila),
        (columna - 1, fila),
        (columna, fila + 1),
        (columna, fila - 1)
    ]

    for col, fil in vecinos:

        if 0 <= col < COLUMNAS and 0 <= fil < FILAS:
            if tablero[fil][col] == LAVA:
                return True
    
    return False


def al_lado_del_mismo(tablero, columna, fila, id_elem):

    vecinos = [
        (columna + 1, fila),
        (columna - 1, fila),
        (columna, fila + 1),
        (columna, fila - 1),

        (columna + 1, fila + 1),
        (columna + 1, fila - 1),
        (columna - 1, fila + 1),
        (columna - 1, fila - 1)
    ]

    for col, fil in vecinos:

        if 0 <= col < COLUMNAS and 0 <= fil < FILAS:
            if tablero[fil][col] == id_elem:
                return True
    
    return False

def poblar_tablero(tablero):
    """
    Coloca un obstáculo y la manzana en el tablero.
    """

    cantidad_lagos = random.randint(LAGOS_MIN, LAGOS_MAX)

    for i in range(cantidad_lagos):

        tamaño = random.randint(LAVA_MIN, LAVA_MAX)

        generar_lago_lava(tablero, tamaño)

    for i in range(CANT_VOLCANO):
        aparecer_aleatorio(tablero, VOLCANO, incluir_borde=False)
    
    for i in range(CANT_HOYO):
        aparecer_aleatorio(tablero, HOYO, incluir_borde=False)
    
    for i in range(CANT_BURBUJA):
        aparecer_aleatorio(tablero, BURBUJA, incluir_borde=False)

    aparecer_aleatorio(tablero, MANZANA)


# CAMBIO PARA MOV: Se añaden px_juno_x e px_juno_y como parámetros
def refrescar_tablero(screen, tablero, vidas, imagenes, tiene_escudo, direccion_juno, px_juno_x, px_juno_y):
    """
    Dibuja el estado actual del tablero en la pantalla.
    """

    screen.fill("gray30")

    floor = imagenes["floor"]
    apple = imagenes["apple"]
    volcano = imagenes["volcano"]
    hole = imagenes["hole"]
    bubble = imagenes["bubble"]

    heart_full = imagenes["heart_full"]
    heart_empty = imagenes["heart_empty"]

    alto_elem = screen.get_height() / FILAS
    ancho_elem = screen.get_width() / COLUMNAS

    #-------------------------------
    # JUGADOR (se escala UNA vez)
    #-------------------------------
    multiplicador = 1.5  
    nuevo_ancho = int(ancho_elem * multiplicador)
    nuevo_alto = int(alto_elem * multiplicador)

    textura_jugador = pygame.transform.scale(
        imagenes["juno_" + direccion_juno],
        (nuevo_ancho, nuevo_alto)
    )
    
    #-------------------------------
    # CAPA 1 Y 2 DEL TABLERO    
    #-------------------------------

    pos_y = 0

    for i in range(FILAS):
        pos_x = 0
        for j in range(COLUMNAS):
            if tablero[i][j] == VOLCANO:
                screen.blit(floor, [pos_x, pos_y])
                screen.blit(imagenes["volcano"], [pos_x, pos_y])

            elif tablero[i][j] == LAVA:
                screen.blit(floor, [pos_x, pos_y])
                screen.blit(imagenes["lava"], [pos_x, pos_y])

            elif tablero[i][j] == HOYO:
                screen.blit(hole, [pos_x, pos_y])

            elif tablero[i][j] == BURBUJA:
                screen.blit(floor, [pos_x, pos_y]) 
                screen.blit(bubble, [pos_x, pos_y])

            elif tablero[i][j] == MANZANA:
                screen.blit(floor, [pos_x, pos_y])
                screen.blit(apple, [pos_x, pos_y])
              
            elif tablero[i][j] == PROTEINA:
                screen.blit(floor, [pos_x, pos_y]) 
                screen.blit(imagenes["protein"], (pos_x, pos_y))

            elif tablero[i][j] == ESCUDO:
                screen.blit(floor, [pos_x, pos_y])
                screen.blit(imagenes["shield"], (pos_x, pos_y)) 

            elif tablero[i][j] == JUGADOR:
                # 1. Pintamos el suelo base
                screen.blit(floor, [pos_x, pos_y])
                
                # CAMBIO PARA MOV: Se eliminó el cálculo centrado acoplado a la matriz aquí. 
                # El renderizado del jugador se movió a la Capa 3.5

            else:
                screen.blit(floor, [pos_x, pos_y])

            pos_x += ancho_elem
        pos_y += alto_elem


    #-------------------------------
    # CAPA 3 DEL TABLERO (bordes de lava)  
    #-------------------------------   
   
    dibujar_bordes_lava(
        screen,
        tablero,
        imagenes,
        ancho_elem,
        alto_elem
    )


    #-------------------------------
    # CAPA 3.5 DEL TABLERO (JUGADOR FLUIDO)  # CAMBIO PARA MOV: Dibujado desacoplado
    #------------------------------- 
    centro_x = px_juno_x + ancho_elem / 2    # CAMBIO PARA MOV: Usa las coordenadas fluidas en pixeles
    centro_y = px_juno_y + alto_elem / 2     # CAMBIO PARA MOV: Usa las coordenadas fluidas en pixeles
    
    rect_jugador = textura_jugador.get_rect(center=(centro_x, centro_y))  # CAMBIO PARA MOV: Define rectángulo centrado
    screen.blit(textura_jugador, rect_jugador)                            # CAMBIO PARA MOV: Pinta a Juno

    #-------------------------------
    # CAPA 4 DEL TABLERO (vidas y escudo) 
    #------------------------------- 

    for i in range(VIDAS_MAXIMAS):

        if i < vidas:
            screen.blit(heart_full, (10 + i * 45 - 10, 1))
        else:
            screen.blit(heart_empty, (10 + i * 45 - 10, 1))

    if tiene_escudo:

        escudo_pequeño = pygame.transform.scale(
            imagenes["shield"],
            (35, 35)
        )

        screen.blit(escudo_pequeño, (10 + VIDAS_MAXIMAS * 45 + 5, 18))

    #-------------------------------
    # FINAL 
    #------------------------------- 

    pygame.display.flip()



def cambiar_direccion(keys, direccion_actual, direccion_juno):
    """
    Cambia la dirección del jugador.
    """

    if keys[pygame.K_w]:
        return (0, -1), "up"

    if keys[pygame.K_s]:
        return (0, 1), "down"

    if keys[pygame.K_a]:
        return (-1, 0), "left"

    if keys[pygame.K_d]:
        return (1, 0), "right"

    return direccion_actual, direccion_juno


def avanzar(tablero, pos_jugador, direccion, manzanas_comidas, vidas, tiene_escudo):
    """
    Avanza el jugador un paso en la dirección dada.
    """

    dir_col, dir_fila = direccion
    ind_actual_col, ind_actual_fila = (
        pos_jugador  
    )

    ind_nueva_col = ind_actual_col + dir_col
    ind_nueva_fila = ind_actual_fila + dir_fila

    if not (0 <= ind_nueva_col < COLUMNAS and 0 <= ind_nueva_fila < FILAS):
        return "derrota", pos_jugador, manzanas_comidas, vidas, tiene_escudo

    pos_elem = tablero[ind_nueva_fila][ind_nueva_col]

    if pos_elem == VOLCANO:
        if tiene_escudo:
            tiene_escudo = False
            tablero[ind_actual_fila][ind_actual_col] = VACIO
            tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR
            return "ok", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo
        
        return "derrota", pos_jugador, manzanas_comidas, vidas, tiene_escudo

    if pos_elem == LAVA:
        if tiene_escudo:
            tiene_escudo = False
            tablero[ind_actual_fila][ind_actual_col] = VACIO
            tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR
            return "ok", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo
        
        return "derrota", pos_jugador, manzanas_comidas, vidas, tiene_escudo

    if pos_elem == HOYO:
        if tiene_escudo:
            tiene_escudo = False
            tablero[ind_actual_fila][ind_actual_col] = VACIO
            tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR
            return "ok", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo
        
        return "derrota", pos_jugador, manzanas_comidas, vidas, tiene_escudo
    
    if pos_elem == BURBUJA:
        if tiene_escudo:
            tiene_escudo = False
            # --- ASE AGREGAN ESTAS TRES LINEAS PARA EVITAR B U G DEL SONIDO ---
            tablero[ind_actual_fila][ind_actual_col] = VACIO
            tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR
            return "ok", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo
            # ----------------------------------------------------------
        else:
            vidas -= 1

        tablero[ind_actual_fila][ind_actual_col] = VACIO
        tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

        if vidas <= 0:
            return "derrota", pos_jugador, manzanas_comidas, vidas, tiene_escudo

        return "burbuja", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo      

    if pos_elem == MANZANA:
        manzanas_comidas += 1
        tablero[ind_actual_fila][ind_actual_col] = VACIO
        tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

        if manzanas_comidas >= MANZANAS_PARA_GANAR:
            return "victoria", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo

        aparecer_aleatorio(tablero, MANZANA)
        return "manzana", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo

    elif pos_elem == PROTEINA:
        if vidas < VIDAS_MAXIMAS:
            vidas += 1
    
        tablero[ind_actual_fila][ind_actual_col] = VACIO
        tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

        return "proteina", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo

    elif pos_elem == ESCUDO:
        tiene_escudo = True
    
        tablero[ind_actual_fila][ind_actual_col] = VACIO
        tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

        return "escudo", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo


    tablero[ind_actual_fila][ind_actual_col] = VACIO
    tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

    return "ok", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo


def reiniciar():
    """
    Crea un nuevo tablero y estado para una nueva partida.
    """

    tablero = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    poblar_tablero(tablero)

    pos_jugador = aparecer_aleatorio(tablero, JUGADOR)

    return tablero, pos_jugador


def mostrar_pantalla(screen, nombre_archivo):
    """
    Carga una imagen y la muestra escalada a la ventana.
    """

    ruta = os.path.join(DIR_PANTALLAS, nombre_archivo)

    try:
        imagen = pygame.image.load(ruta)
        imagen = pygame.transform.scale(imagen, screen.get_size())

        screen.blit(imagen, (0, 0))

        pygame.display.flip()
    except FileNotFoundError:
        screen.fill("black")
        pygame.display.flip()
        print(f"Advertencia: No se encontró la imagen {ruta}")


def main():
    pygame.init()

## === SONIDO ===
    pygame.mixer.init() 
    
    sonido_derrota = pygame.mixer.Sound(os.path.join(DIR_SONIDOS, "perdedor.mp3"))
    sonido_victoria = pygame.mixer.Sound(os.path.join(DIR_SONIDOS, "ganador.mp3"))
    sonido_manzana = pygame.mixer.Sound(os.path.join(DIR_SONIDOS, "ganarunavida.mp3"))
    sonido_burbuja = pygame.mixer.Sound(os.path.join(DIR_SONIDOS, "perderunavida.mp3"))
    sonido_gana_escudo = pygame.mixer.Sound(os.path.join(DIR_SONIDOS, "ganarescudo.mp3"))
    sonido_pierde_escudo = pygame.mixer.Sound(os.path.join(DIR_SONIDOS, "perderescudo.mp3"))
    sonido_proteina = pygame.mixer.Sound(os.path.join(DIR_SONIDOS, "ganarproteina.mp3"))
    pygame.mixer.music.load(os.path.join(DIR_SONIDOS, "background.mp3"))
    # =============================

    screen = pygame.display.set_mode((700, 700))

    pygame.display.set_caption("Juego Básico")

    imagenes = {}

    imagenes["floor"] = pygame.image.load(
        "data/assets/blocks/floor.jpg"
    ).convert()


    imagenes["apple"] = pygame.image.load(
        "data/assets/elements/apple.png"
    ).convert_alpha()
    
    imagenes["apple"] = pygame.transform.smoothscale(
        imagenes["apple"],
        (40, 40)
    )

    imagenes["volcano"] = pygame.image.load(
        "data/assets/blocks/volcano.png"
    ).convert()
    imagenes["volcano"] = pygame.transform.scale(
        imagenes["volcano"],
        (49,49)
    )


    imagenes["lava"] = pygame.image.load(
        "data/assets/blocks/lava.png"
    ).convert_alpha()
    imagenes["lava"] = pygame.transform.scale(
        imagenes["lava"],
        (49,49)
    )

    imagenes["hole"] = pygame.image.load(
        "data/assets/blocks/hole.jpg"
    ).convert()
    imagenes["hole"] = pygame.transform.scale(
        imagenes["hole"],
        (49,49)
    )

    imagenes["bubble"] = pygame.image.load(
        "data/assets/elements/bubble.png" 
    ).convert_alpha()

    imagenes["heart_full"] = pygame.image.load(
        "data/assets/ui/heart_full.png"
    ).convert_alpha()
    imagenes["heart_full"] = pygame.transform.scale(
        imagenes["heart_full"],
        (60,60)
    )

    imagenes["heart_empty"] = pygame.image.load(
        "data/assets/ui/heart_empty.png"
    ).convert_alpha()
    imagenes["heart_empty"] = pygame.transform.scale(
        imagenes["heart_empty"],
        (60,60)
    )

    imagenes["protein"] = pygame.image.load(
        "data/assets/elements/protein.png"
    ).convert_alpha()
    imagenes["protein"] = pygame.transform.scale(
        imagenes["protein"],
        (49,49)
    )

    imagenes["shield"] = pygame.image.load(
        "data/assets/elements/shield.png"
    ).convert_alpha()
    imagenes["shield"] = pygame.transform.scale(
        imagenes["shield"],
        (49,49)
    )

    #----------------------------------------------
    # JUNO
    imagenes["juno_up"] = pygame.image.load(
        "data/assets/elements/juno_up.png"
    ).convert_alpha()

    imagenes["juno_down"] = pygame.image.load(
        "data/assets/elements/juno_down.png"
    ).convert_alpha()

    imagenes["juno_left"] = pygame.image.load(
        "data/assets/elements/juno_left.png"
    ).convert_alpha()

    imagenes["juno_right"] = pygame.image.load(
        "data/assets/elements/juno_right.png"
    ).convert_alpha() 
    #----------------------------------------------


    # Suelos con LAVA
    #----------------------------------------------
    imagenes["lava_top"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_top.jpeg"
    ).convert_alpha()
    imagenes["lava_top"] = pygame.transform.scale(
        imagenes["lava_top"],
        (49,49)
    )

    imagenes["lava_bottom"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_bottom.jpeg"
    ).convert_alpha()
    imagenes["lava_bottom"] = pygame.transform.scale(
        imagenes["lava_bottom"],
        (49,49)
    )

    imagenes["lava_left"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_left.jpeg"
    ).convert_alpha()
    imagenes["lava_left"] = pygame.transform.scale(
        imagenes["lava_left"],
        (49,49)
    )

    imagenes["lava_right"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_right.jpeg"
    ).convert_alpha() 
    imagenes["lava_right"] = pygame.transform.scale(
        imagenes["lava_right"],
        (49,49)
    )

    imagenes["lava_top_left"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_top_left.jpeg"
    ).convert_alpha()
    imagenes["lava_top_left"] = pygame.transform.scale(
        imagenes["lava_top_left"],
        (49,49)
    )

    imagenes["lava_top_right"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_top_right.jpeg"
    ).convert_alpha()
    imagenes["lava_top_right"] = pygame.transform.scale(
        imagenes["lava_top_right"],
        (49,49)
    )

    imagenes["lava_bottom_left"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_bottom_left.jpeg"
    ).convert_alpha()
    imagenes["lava_bottom_left"] = pygame.transform.scale(
        imagenes["lava_bottom_left"],
        (49,49)
    )

    imagenes["lava_bottom_right"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_bottom_right.jpeg"
    ).convert_alpha()
    imagenes["lava_bottom_right"] = pygame.transform.scale(
        imagenes["lava_bottom_right"],
        (49,49)
    )

    imagenes["lava_top_both"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_top_both.jpeg"
    ).convert_alpha()
    imagenes["lava_top_both"] = pygame.transform.scale(
        imagenes["lava_top_both"],
        (49,49)
    )

    imagenes["lava_bottom_both"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_bottom_both.jpeg"
    ).convert_alpha()
    imagenes["lava_bottom_both"] = pygame.transform.scale(
        imagenes["lava_bottom_both"],
        (49,49)
    )

    imagenes["lava_left_both"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_left_both.jpeg"
    ).convert_alpha()
    imagenes["lava_left_both"] = pygame.transform.scale(
        imagenes["lava_left_both"],
        (49,49)
    )
    
    imagenes["lava_right_both"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_right_both.jpeg"
    ).convert_alpha()
    imagenes["lava_right_both"] = pygame.transform.scale(
        imagenes["lava_right_both"],
        (49,49)
    )

    imagenes["lava_all_sides"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_all_sides.png"
    ).convert_alpha()
    imagenes["lava_all_sides"] = pygame.transform.scale(
        imagenes["lava_all_sides"],
        (49,49)
    )

    imagenes["lava_top_bottom"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_top_bottom.png"
    ).convert_alpha()
    imagenes["lava_top_bottom"] = pygame.transform.scale(
        imagenes["lava_top_bottom"],
        (49,49)
    )

    imagenes["lava_left_right"] = pygame.image.load(
        "data/assets/blocks/lava_floor/lava_left_right.png"
    ).convert_alpha()
    imagenes["lava_left_right"] = pygame.transform.scale(
        imagenes["lava_left_right"],
        (49,49)
    )
    #----------------------------------------------


    running = True

    estado = ESTADO_INICIO
    tablero = []
    pos_jugador = (0, 0)
    direccion = (0, 0)

    direccion_juno = "down"

    tiempo_ultimo_mov = 0
    
    manzanas_comidas = 0
    vidas = VIDAS_MAXIMAS

    proteina_activa = False
    tiempo_ultima_proteina = pygame.time.get_ticks()

    escudo_activo = False
    tiempo_ultimo_escudo = pygame.time.get_ticks()
    tiene_escudo = False

    # --- CAMBIO PARA MOV: SETUP DE FPS Y COORDENADAS FLUIDAS ---
    clock = pygame.time.Clock()                 # Inicializar reloj
    ancho_elem = 700 / COLUMNAS                 # Definimos el tamaño antes
    alto_elem = 700 / FILAS                     # Definimos el tamaño antes
    
    px_juno_x = pos_jugador[0] * ancho_elem     # Inicializar X visual
    px_juno_y = pos_jugador[1] * alto_elem      # Inicializar Y visual
    # -----------------------------------------------------------

    mostrar_pantalla(screen, PANTALLA_INICIO)

    while running:


        if estado == ESTADO_JUGANDO:
                
                if not proteina_activa:

                    if pygame.time.get_ticks() - tiempo_ultima_proteina >= 5000:

                        aparecer_aleatorio(tablero, PROTEINA)
                        proteina_activa = True
                        tiempo_ultima_proteina = pygame.time.get_ticks()



        if estado == ESTADO_JUGANDO:
                
                if not escudo_activo:

                    if pygame.time.get_ticks() - tiempo_ultimo_escudo >= 5000:

                        aparecer_aleatorio(tablero, ESCUDO)
                        escudo_activo = True
                        tiempo_ultimo_escudo = pygame.time.get_ticks()


        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False

            if evento.type == pygame.KEYDOWN:
                if estado == ESTADO_INICIO:
                    if evento.key == pygame.K_SPACE:
                        tablero, pos_jugador = reiniciar()

                        manzanas_comidas = 0
                        vidas = VIDAS_MAXIMAS

                        proteina_activa = False
                        tiempo_ultima_proteina = pygame.time.get_ticks()

                        escudo_activo = False
                        tiempo_ultimo_escudo = pygame.time.get_ticks()
                        tiene_escudo = False

                        direccion = (0, 0)
                        direccion_juno = "down"

                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        estado = ESTADO_JUGANDO

                        # --- CAMBIO PARA MOV: REINICIO POSICIÓN FLUIDA ---
                        px_juno_x = pos_jugador[0] * ancho_elem
                        px_juno_y = pos_jugador[1] * alto_elem
                        # -------------------------------------------------

                        pygame.mixer.music.play(-1) 

                        # CAMBIO PARA MOV: Se eliminó el llamado a refrescar_tablero() aquí, ahora lo hace el bucle continuo abajo

                    elif evento.key == pygame.K_i:
                        estado = ESTADO_INSTRUCCIONES
                        mostrar_pantalla(screen, PANTALLA_INSTRUCCIONES)

                elif estado == ESTADO_INSTRUCCIONES:
                    estado = ESTADO_INICIO
                    mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado in (ESTADO_DERROTA, ESTADO_VICTORIA):
                    if evento.key == pygame.K_r:
                        tablero, pos_jugador = reiniciar()

                        manzanas_comidas = 0
                        vidas = VIDAS_MAXIMAS

                        proteina_activa = False
                        tiempo_ultima_proteina = pygame.time.get_ticks()

                        escudo_activo = False
                        tiempo_ultimo_escudo = pygame.time.get_ticks()
                        tiene_escudo = False

                        direccion = (0, 0)
                        direccion_juno = "down"

                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        estado = ESTADO_JUGANDO

                        # --- CAMBIO PARA MOV: REINICIO POSICIÓN FLUIDA ---
                        px_juno_x = pos_jugador[0] * ancho_elem
                        px_juno_y = pos_jugador[1] * alto_elem
                        # -------------------------------------------------

                        pygame.mixer.stop()
                        pygame.mixer.music.play(-1) 
                        
                        # CAMBIO PARA MOV: Se eliminó el llamado a refrescar_tablero() aquí

                    if evento.key == pygame.K_ESCAPE:
                        estado = ESTADO_INICIO
                        mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado == ESTADO_JUGANDO:
                    direccion, direccion_juno = cambiar_direccion(
                        pygame.key.get_pressed(), 
                        direccion,
                        direccion_juno)

        if estado == ESTADO_JUGANDO:
            tiempo_actual = pygame.time.get_ticks() 

            if direccion != (0, 0) and tiempo_actual - tiempo_ultimo_mov >= RETRASO:
                escudo_previo = tiene_escudo # <-- SE AGREGAA: Guarda el estado antes de mover
                resultado, pos_jugador, manzanas_comidas, vidas, tiene_escudo = avanzar(
                    tablero, 
                    pos_jugador, 
                    direccion, 
                    manzanas_comidas, 
                    vidas,
                    tiene_escudo)
                # --- AGREGAR: Evalúa si el escudo se rompió en este turno ---
                if escudo_previo and not tiene_escudo:
                    sonido_pierde_escudo.play()
                # ------------------------------------------------------------
                if resultado == "derrota":
                    estado = ESTADO_DERROTA

                    pygame.mixer.music.stop() 
                    sonido_derrota.play()

                    mostrar_pantalla(screen, PANTALLA_DERROTA)
                elif resultado == "victoria":
                    estado = ESTADO_VICTORIA
                    pygame.mixer.music.stop() 
                    sonido_victoria.play()
                    mostrar_pantalla(screen, PANTALLA_VICTORIA)
                
                elif resultado == "manzana":
                    sonido_manzana.play() 
                    tiempo_ultimo_mov = tiempo_actual
                    # CAMBIO PARA MOV: Se eliminó el llamado a refrescar_tablero() aquí

                elif resultado == "proteina":
                    sonido_proteina.play()
                    proteina_activa = False
                    tiempo_ultima_proteina = pygame.time.get_ticks()
                    tiempo_ultimo_mov = tiempo_actual
                    # CAMBIO PARA MOV: Se eliminó el llamado a refrescar_tablero() aquí

                elif resultado == "escudo":
                    sonido_gana_escudo.play()
                    tiene_escudo = True
                    escudo_activo = False
                    tiempo_ultimo_escudo = pygame.time.get_ticks()
                    tiempo_ultimo_mov = tiempo_actual
                    # CAMBIO PARA MOV: Se eliminó el llamado a refrescar_tablero() aquí

                elif resultado == "burbuja":
                    sonido_burbuja.play()
                    tiempo_ultimo_mov = tiempo_actual
                    # CAMBIO PARA MOV: Se eliminó el llamado a refrescar_tablero() aquí

                else:
                    tiempo_ultimo_mov = tiempo_actual
                    # CAMBIO PARA MOV: Se eliminó el llamado a refrescar_tablero() aquí

        # --- CAMBIO PARA MOV: GESTIÓN CONTINUA DE RENDERIZADO Y LERsP (60 FPS) ---
        if estado == ESTADO_JUGANDO:
            # 1. Dónde DEBERÍA estar lógicamente en la grilla
            target_x = pos_jugador[0] * ancho_elem
            target_y = pos_jugador[1] * alto_elem
            
            # 2. Suavizado Matemático (Lerp). Velocidad de deslizamiento = 0.2
            px_juno_x += (target_x - px_juno_x) * 0.2
            px_juno_y += (target_y - px_juno_y) * 0.2

            # 3. Único llamado de renderizado constante
            refrescar_tablero(screen, tablero, vidas, imagenes, tiene_escudo, direccion_juno, px_juno_x, px_juno_y)
            
        clock.tick(60) # Limita el proceso a 60 cuadros por segundo
        # ------------------------------------------------------------------------

    pygame.quit()

if __name__ == "__main__":
    main()