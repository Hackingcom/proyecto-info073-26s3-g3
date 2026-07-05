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

CANT_VOLCANO = 15
CANT_HOYO = 8
CANT_BURBUJA = 10
CANT_PROTEINA = 2

# Bloques del lago de lava
LAVA_MIN = 20
LAVA_MAX = 30
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

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
        - id_elem: El número identificador del elemento que queremos colocar.

    Retorna:
        - (columna, fila): Tupla que indica posición en la que se colocó el elemento.
    """

    # Debemos detectar los espacios vacíos, para ello recorremos
    # el tablero y almacenamos tuplas de (columna, fila) las posiciones
    # en las que un elemento "VACIO" (el número 0 en este caso) se encuentre.
    vacios = []

    # Forma vista en clases de recorrer el arreglo multidimensional.
    # Tanto fila como columna son números.
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            # Obtenemos el elemento que se encuentra en esa fila y columna.
            elem_pos = tablero[fila][columna]

            if elem_pos == VACIO:
                # Al utilizar los paréntesis () dentro de la función, lo estaremos
                # añadiendo como una tupla con la estructura (columna, fila).
                vacios.append((columna, fila))

    # También se puede utilizar comprensión de listas para rellenar el arreglo
    # a la vez que lo recorremos:
    #
    # vacios = [
    #     (columna, fila)
    #     for fila in range(FILAS)
    #     for columna in range(COLUMNAS)
    #     if tablero[fila][columna] == VACIO
    # 

    if not incluir_borde:
        vacios = [pos for pos in vacios if pos not in BORDE]


    # Si no hay casillas vacías, retornamos un valor especial.
    if len(vacios) == 0:
        return -1, -1

    # Usando la función random.choice(lista) podremos obtener una tupla
    # aleatoria desde el arreglo "vacios" que definimos anteriormente.
    columna, fila = random.choice(vacios)

    # Finalmente, colocamos el elemento al poner su número en la casilla
    # del tablero correspondiente.
    tablero[fila][columna] = id_elem

    return columna, fila



def generar_lago_lava(tablero):
    
    """
    Genera un lago de lava con forma irregular
    """

    # Punto inicial
    columna, fila = aparecer_aleatorio(tablero, LAVA, incluir_borde=False)

    if columna == -1:
        return
    
    # Bloques del lago

    posiciones = [(columna,fila)]

    cantidad = random.randint(LAVA_MIN,LAVA_MAX)

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


def poblar_tablero(tablero):
    """
    Coloca un obstáculo y la manzana en el tablero.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
    """


    generar_lago_lava(tablero)


    for i in range(CANT_VOLCANO):
        aparecer_aleatorio(tablero, VOLCANO, incluir_borde=False)
    
    for i in range(CANT_HOYO):
        aparecer_aleatorio(tablero, HOYO, incluir_borde=False)
    
    for i in range(CANT_BURBUJA):
        aparecer_aleatorio(tablero, BURBUJA, incluir_borde=False)


    aparecer_aleatorio(tablero, MANZANA)


def refrescar_tablero(screen, tablero, vidas, imagenes, tiene_escudo, direccion_juno):
    """
    Dibuja el estado actual del tablero en la pantalla.

    Parámetros:
        - screen: La pantalla sobre la cual estamos dibujando.
        - tablero: El tablero con sus posiciones actuales.
    """

    # Rellena la pantalla con el color gris, básicamente pintando
    # por encima de lo que estaba anteriormente.
    screen.fill("gray30")


    floor = imagenes["floor"]
    apple = imagenes["apple"]
    volcano = imagenes["volcano"]
    hole = imagenes["hole"]
    bubble = imagenes["bubble"]

    heart_full = imagenes["heart_full"]
    heart_empty = imagenes["heart_empty"]


    # Podemos calcular el tamaño en pixeles que tendrá cada
    # casilla al dividir tanto la altura de la pantalla (screen.get_height())
    # como el ancho (screen.get_width()) por la cantidad de filas y columnas respectivamente.
    # Por ejemplo en este caso alto_elem sería 800 / 15 = 53.3, lo que nos indica que la
    # altura de cada elemento es de 53.3 píxeles.
    alto_elem = screen.get_height() / FILAS
    ancho_elem = screen.get_width() / COLUMNAS
    # Como el jugador es un círculo, se necesita el radio.
    radio = ancho_elem / 2

# --- NUEVO: CARGA Y ESCALA AL PJ---
    multiplicador = 1.5  # AUMETNAR PARA HACERLO MAS GRANDE
    nuevo_ancho = int(ancho_elem * multiplicador)
    nuevo_alto = int(alto_elem * multiplicador)

    textura_jugador = pygame.transform.scale(
        imagenes["juno_" + direccion_juno],
        (nuevo_ancho, nuevo_alto)
    )

    # -------------------------------------------------
    
    pos_y = 0

    for i in range(FILAS):
        # Posición en eje "x" en unidad de píxeles.
        pos_x = 0
        for j in range(COLUMNAS):
            if tablero[i][j] == VOLCANO:
                # Dibuja un rectángulo en la posición (pos_x, pos_y) y que sea
                # de tamaño (ancho_elem, alto_elem) y color negro.
                screen.blit(floor, [pos_x, pos_y])
                screen.blit(volcano, [pos_x, pos_y])


            elif tablero[i][j] == LAVA:


                screen.blit(floor, [pos_x, pos_y])
                screen.blit(imagenes["lava"], [pos_x, pos_y])


            elif tablero[i][j] == HOYO:

                screen.blit(hole, [pos_x, pos_y])


            elif tablero[i][j] == BURBUJA:
                screen.blit(floor, [pos_x, pos_y]) # <-- PARA RENDERIZAR EL SUELO, CAMBIAR EL PNG
                screen.blit(bubble, [pos_x, pos_y])


            elif tablero[i][j] == JUGADOR:
                # 1. Pintamos el suelo base
                screen.blit(floor, [pos_x, pos_y])
                
                # 2. CALCULAR CENTRO
                centro_x = pos_x + ancho_elem / 2
                centro_y = pos_y + alto_elem / 2
                
                # 3. CENTRAR
                rect_jugador = textura_jugador.get_rect(center=(centro_x, centro_y))
                
                # 4. SE DIBUJA USANDO LA TEXTURA EN EL CENTRO
                screen.blit(textura_jugador, rect_jugador)
            

            
            elif tablero[i][j] == MANZANA:

                screen.blit(floor, [pos_x, pos_y])
                screen.blit(apple, [pos_x, pos_y])
              



            elif tablero[i][j] == PROTEINA:
                screen.blit(floor, [pos_x, pos_y]) # <-- AGREGUE SUELO Y RENDERIZA EL SUELO DEBAJO
                screen.blit(imagenes["protein"], (pos_x, pos_y))




            elif tablero[i][j] == ESCUDO:
                screen.blit(floor, [pos_x, pos_y])
                screen.blit(imagenes["shield"], (pos_x, pos_y))    

            else:
                screen.blit(floor, [pos_x, pos_y])

            # Estamos recorriendo los píxeles de la pantalla, por lo que
            # debemos sumar el ancho y altura en pixeles de cada elemento que
            # ya hayamos recorrido para avanzar al siguiente.
            pos_x += ancho_elem
        pos_y += alto_elem


    for i in range(VIDAS_MAXIMAS):

        if i < vidas:
            screen.blit(heart_full, (10 + i * 45, 10))
        else:
            screen.blit(heart_empty, (10 + i * 45, 10))

    if tiene_escudo:

        screen.blit(imagenes["shield"], (10 + VIDAS_MAXIMAS * 45 + 20, 5))


    # Refresca el contenido que se ve en pantalla.
    pygame.display.flip()


def cambiar_direccion(keys, direccion_actual, direccion_juno):
    """
    Cambia la dirección del jugador.

    Parámetros:
        - keys: Arreglo de teclas presionadas.
        - direccion_actual: La dirección en la que estaba avanzando justo antes de analizar
            si hubo un cambio de dirección.

    Retorna:
        - direccion_actual: La nueva dirección del jugador.
    """

    # Tecla W
    if keys[pygame.K_w]:
        # La tupla nos indica que horizontalmente (columnas) no hará nada (0) y
        # que verticalmente (filas) disminuirá el índice en el tablero (-1).
        return (0, -1), "up"

    # Tecla S
    if keys[pygame.K_s]:
        # En este caso avanzará a través de las filas del tablero.
        return (0, 1), "down"

    # Tecla A
    if keys[pygame.K_a]:
        # Retrocede por las columnas del tablero.
        return (-1, 0), "left"

    # Tecla D
    if keys[pygame.K_d]:
        # Avanza por las columnas del tablero.
        return (1, 0), "right"

    # Si no se presiona ninguna de las teclas anteriores, la dirección
    # será la misma que la anterior.
    return direccion_actual, direccion_juno


def avanzar(tablero, pos_jugador, direccion, manzanas_comidas, vidas, tiene_escudo):
    """
    Avanza el jugador un paso en la dirección dada.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
        - pos_jugador: Tupla con la posición actual (índice con
            estructura (columna, fila)) del jugador en el tablero.
        - direccion: Tupla con la dirección en la que está avanzando actualmente el jugador.

    Retorna:
        - (resultado, nueva_pos_jugador): Retorna el resultado que se obtiene
            al avanzar (derrota, victoria o "ok" (no cambia de pantalla)) y la nueva posición del jugador.
    """

    # Obtenemos los componentes "x" e "y" de cada tupla recibida
    # con información de la dirección y posición del jugador.
    dir_col, dir_fila = direccion
    ind_actual_col, ind_actual_fila = (
        pos_jugador  # Tupla (columna, fila) que representa los índices en el tablero.
    )

    # Aplicamos la dirección a la posición del jugador.
    ind_nueva_col = ind_actual_col + dir_col
    ind_nueva_fila = ind_actual_fila + dir_fila

    # Verificamos que no haya choque con el borde del tablero.
    if not (0 <= ind_nueva_col < COLUMNAS and 0 <= ind_nueva_fila < FILAS):
        return "derrota", pos_jugador, manzanas_comidas, vidas, tiene_escudo

    # Obtenemos el elemento que se encuentre en el tablero en la nueva posición del jugador.
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
        
        else:

            vidas -= 1

        tablero[ind_actual_fila][ind_actual_col] = VACIO
        tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

        if vidas <= 0:
            return "derrota", pos_jugador, manzanas_comidas, vidas, tiene_escudo

        return "burbuja", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo      

    if pos_elem == MANZANA:
        ### return "victoria", (ind_nueva_col, ind_nueva_fila)
        manzanas_comidas += 1
        # Mover al jugador a la nueva casilla
        tablero[ind_actual_fila][ind_actual_col] = VACIO
        tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

        # Si llegamos al objetivo, victoria
        if manzanas_comidas >= MANZANAS_PARA_GANAR:
            return "victoria", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo

        # Si no, generar otra manzana y continuar
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



    # Movimiento normal, si es que no encontramos manzana ni obstáculo.
    tablero[ind_actual_fila][ind_actual_col] = VACIO
    tablero[ind_nueva_fila][ind_nueva_col] = JUGADOR

    return "ok", (ind_nueva_col, ind_nueva_fila), manzanas_comidas, vidas, tiene_escudo


def reiniciar():
    """
    Crea un nuevo tablero y estado para una nueva partida.

    Retorna:
        - (tablero, pos_jugador): Tablero nuevo y la nueva posición aleatoria del jugador.
            pos_jugador corresponda a una tupla (columna, fila) donde columna y fila son índices
            de matriz tablero.
    """

    # Si se modifica constante FILAS o COLUMNAS al inicio, también
    # se debe modificar este arreglo de tablero con los valores correspondientes.
    # Esto puede ser mejorado usando dos bucles "for" anidados o comprensión de listas.
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

    # Usando dos bucles "for" anidados se haría de la siguiente manera:
    # tablero = []
    # for _ in range(FILAS):
    #     fila_tablero = []
    #
    #     for _ in range(COLUMNAS):
    #         fila_tablero.append(VACIO)
    #
    #     tablero.append(fila_tablero)
    # Otra manera usando comprensión de listas:
    # tablero = [[VACIO] * COLUMNAS for _ in range(FILAS)]
    # El _ en el "for" indica que no usamos la variable con la que iteramos.

    poblar_tablero(tablero)

    # Colocamos al jugador en una posición aleatoria.
    pos_jugador = aparecer_aleatorio(tablero, JUGADOR)

    return tablero, pos_jugador


def mostrar_pantalla(screen, nombre_archivo):
    """
    Carga una imagen y la muestra escalada a la ventana.

    Parámetros:
        - screen: La pantalla donde colocaremos la imagen.
        - nombre_archivo: El nombre del archivo de la imagen.
    """

    ruta = os.path.join(DIR_PANTALLAS, nombre_archivo)

    try:
        imagen = pygame.image.load(ruta)
        imagen = pygame.transform.scale(imagen, screen.get_size())

        # Dibujamos la imagen en la pantalla en la coordenada (0, 0).
        screen.blit(imagen, (0, 0))

        # Refrescamos pantalla.
        pygame.display.flip()
    except FileNotFoundError:
        # Fallback de seguridad en caso de que las imágenes no existan aún
        screen.fill("black")
        pygame.display.flip()
        print(f"Advertencia: No se encontró la imagen {ruta}")


def main():
    pygame.init()

## === SONIDO ===
    pygame.mixer.init() # Esto enciende el motor de audio de pygame
    
    # Se cargan los efectos
    sonido_derrota = pygame.mixer.Sound(os.path.join(DIR_SONIDOS, "perdedor.mp3"))
    sonido_victoria = pygame.mixer.Sound(os.path.join(DIR_SONIDOS, "ganador.mp3"))
    sonido_manzana = pygame.mixer.Sound(os.path.join(DIR_SONIDOS, "ganarunavida.mp3"))
    sonido_burbuja = pygame.mixer.Sound(os.path.join(DIR_SONIDOS, "perderunavida.mp3"))
    pygame.mixer.music.load(os.path.join(DIR_SONIDOS, "background.mp3 "))
    # =============================

    # Establecemos la resolución de la pantalla.
    screen = pygame.display.set_mode((700, 700))

    # Establecemos el título de la ventana.
    pygame.display.set_caption("Juego Básico")




    imagenes = {}

    imagenes["floor"] = pygame.image.load(
        "data/assets/blocks/floor.jpg"
    ).convert()


    imagenes["apple"] = pygame.image.load(
        "data/assets/elements/apple.png"
    ).convert_alpha()
    
    # Se redimensiona la manzana usando smoothscale para mantener mejor la textura
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
        "data/assets/elements/bubble.png" # Cambio a .png
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





    mostrar_pantalla(screen, PANTALLA_INICIO)

    # Este es el bucle principal del juego, todo lo que sucede en el juego
    # está aquí.
    while running:


        if estado == ESTADO_JUGANDO:
                
                if not proteina_activa:

                    if pygame.time.get_ticks() - tiempo_ultima_proteina >= 10000:

                        aparecer_aleatorio(tablero, PROTEINA)
                        proteina_activa = True
                        tiempo_ultima_proteina = pygame.time.get_ticks()



        if estado == ESTADO_JUGANDO:
                
                if not escudo_activo:

                    if pygame.time.get_ticks() - tiempo_ultimo_escudo >= 1000:

                        aparecer_aleatorio(tablero, ESCUDO)
                        escudo_activo = True
                        tiempo_ultimo_escudo = pygame.time.get_ticks()


        # Se analizan los eventos del bucle actual.
        for evento in pygame.event.get():
            # Si es que se quiere cerrar la ventana.
            if evento.type == pygame.QUIT:
                running = False

            # Si es que se presiona alguna tecla.
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

                        # Obtiene tiempo en milisegundos
                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        estado = ESTADO_JUGANDO

                        # MUSICA ---
                        pygame.mixer.music.play(-1) # El -1 hace que se repita sola todo el rato
                        # MUSICA ----

                        refrescar_tablero(screen, tablero, vidas, imagenes, tiene_escudo, direccion_juno)
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

                        # === AUDIO: ARREGLAR REINICIO ===
                        pygame.mixer.stop()
                        pygame.mixer.music.play(-1) 
                        # ================================

                        refrescar_tablero(screen, tablero, vidas, imagenes, tiene_escudo, direccion_juno)

                    if evento.key == pygame.K_ESCAPE:
                        estado = ESTADO_INICIO
                        mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado == ESTADO_JUGANDO:
                    direccion, direccion_juno = cambiar_direccion(
                        pygame.key.get_pressed(), 
                        direccion,
                        direccion_juno)

        if estado == ESTADO_JUGANDO:
            tiempo_actual = pygame.time.get_ticks()  # En milisegundos

            # La variable RETRASO hace que si no han pasado esa cantidad de ticks,
            # entonces no se avanzará en el tablero.
            if direccion != (0, 0) and tiempo_actual - tiempo_ultimo_mov >= RETRASO:
                ### resultado, pos_jugador = avanzar(tablero, pos_jugador, direccion)
                resultado, pos_jugador, manzanas_comidas, vidas, tiene_escudo = avanzar(
                    tablero, 
                    pos_jugador, 
                    direccion, 
                    manzanas_comidas, 
                    vidas,
                    tiene_escudo)
                if resultado == "derrota":
                    estado = ESTADO_DERROTA

                    pygame.mixer.music.stop() # Detiene la música de fondo primero
                    sonido_derrota.play()

                    mostrar_pantalla(screen, PANTALLA_DERROTA)
                elif resultado == "victoria":
                    estado = ESTADO_VICTORIA
                    pygame.mixer.music.stop() 
                    sonido_victoria.play()
                    mostrar_pantalla(screen, PANTALLA_VICTORIA)
                
                # NUEVO: Bloque de la manzana
                elif resultado == "manzana":
                    sonido_manzana.play() # Hará el sonido "ganarunavida.mp3"
                    
                    tiempo_ultimo_mov = tiempo_actual
                    refrescar_tablero(screen, tablero, vidas, imagenes, tiene_escudo, direccion_juno)

                elif resultado == "proteina":
                    # ELIMINADO: sonido_proteina.play() para que no suene
                    proteina_activa = False
                    tiempo_ultima_proteina = pygame.time.get_ticks()

                    tiempo_ultimo_mov = tiempo_actual
                    refrescar_tablero(screen, tablero, vidas, imagenes, tiene_escudo, direccion_juno)
                


                elif resultado == "escudo":

                    tiene_escudo = True
                    escudo_activo = False
                    tiempo_ultimo_escudo = pygame.time.get_ticks()
                    
                    tiempo_ultimo_mov = tiempo_actual
                    refrescar_tablero(screen, tablero, vidas, imagenes, tiene_escudo, direccion_juno)



                # --- NUEVO: Bloque para q funcione lo del sonido ---
                elif resultado == "burbuja":
                    sonido_burbuja.play()
                    
                    tiempo_ultimo_mov = tiempo_actual
                    refrescar_tablero(screen, tablero, vidas, imagenes, tiene_escudo, direccion_juno)
                # ----------------------------------------------

                
                else:
                    tiempo_ultimo_mov = tiempo_actual
                    refrescar_tablero(screen, tablero, vidas, imagenes, tiene_escudo, direccion_juno)

    pygame.quit()

if __name__ == "__main__":
    main()
