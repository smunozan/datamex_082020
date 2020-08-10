import sys #para usar exit()
import time #para usar sleep()
import pygame #libreria de juegos con python
import random #para posición de los virus

#definir tamaño de interfaz
ANCHO = 640
ALTO = 300
color_negro = (0,0,0) #Color para letras
color_blanco = (247,247,247) #Color de fondo

#inicializamos el uso de fuentes (texto) para el mensaje cuando pierde
pygame.init()

#Creación de objetos (los objetos visibles en pygame son sprites)
#Creación de imagen de fondo
class Fondo(pygame.sprite.Sprite):
    def __init__(self): 
        pygame.sprite.Sprite.__init__(self)
        #cargar imagen
        self.image = pygame.image.load("imagenes/fondo.png")
        #obtener rectangulo de la imagen
        self.rect = self.image.get_rect()
        #posición inicial, provista externamente
        self.rect.midbottom = (ANCHO/2, ALTO+5)
        #Establecer velocidad inicial (cuantos pixeles en x y cuantos en y)
        self.speed = [-3,0]
    
    #movimiento del fondo
    def update(self):
        self.speed = [-3,0]
        #mover el elemento en base a posición actual y velocidad
        self.rect.move_ip(self.speed)

#Crear objeto ironhack
class Ironhack(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #cargar imagen
        self.image = pygame.image.load("imagenes/ironhack.png")
        #obtener rectangulo de la imagen
        self.rect = self.image.get_rect()
        #Posición inicial de la paleta (centrada en eje X)
        self.rect.midbottom = (ANCHO*.10, ALTO*.80)
        #Establecer velocidad inicial (cuantos pixeles en x y cuantos en y)
        self.speed = [0,0]
    
    #movimientos del jugador
    def update(self):
        #Acción si presiona el space
        if self.rect.bottom >= ALTO*.80:
            self.speed = [0,-5]
        elif self.rect.bottom <= ALTO*.45:
            self.speed = [0,5]
        #mover el elemento en base a posición actual y velocidad
        self.rect.move_ip(self.speed)

#Crear objeto virus (el que tenemos que esquivar)
class Virus(pygame.sprite.Sprite):
    def __init__(self,posicion):
        pygame.sprite.Sprite.__init__(self)
        #cargar imagen
        self.image = pygame.image.load("imagenes/virus.png")
        #obtener rectangulo de la imagen
        self.rect = self.image.get_rect()
        #posición inicial, provista externamente
        self.rect.midbottom = posicion
        #Establecer velocidad inicial (cuantos pixeles en x y cuantos en y)
        self.speed = [-6.5,0]
    
    #movimiento del virus
    def update(self):
        self.speed = [-6.5,0]
        #mover el elemento en base a posición actual y velocidad
        self.rect.move_ip(self.speed)


#Crear objeto colección de virus        
class Enemigos(pygame.sprite.Group):
    def __init__(self,  cantidadVirus):
        pygame.sprite.Group.__init__(self)
        #llamamos a clase Ladrillo para crear los ladrillos del muro en la posición x, y
        pos_x = ANCHO+20 
        pos_y = ALTO*.80
        #Nivel 1 (más espacio entre virus)
        for i in range(round(cantidadVirus/5)):
            virus = Virus((pos_x,pos_y))
            #agregamos el virus creado a la colección de virus
            self.add(virus)
            #modificamos la posición en x con una posición random
            pos_x += random.randint(250,800)
        for i in range(round(cantidadVirus/5)):
            virus = Virus((pos_x,pos_y))
            #agregamos el virus creado a la colección de virus
            self.add(virus)
            #modificamos la posición en x con una posición random
            pos_x += random.randint(250,700)
        for i in range(round(cantidadVirus/5)):
            virus = Virus((pos_x,pos_y))
            #agregamos el virus creado a la colección de virus
            self.add(virus)
            #modificamos la posición en x con una posición random
            pos_x += random.randint(200,600)
        for i in range(round(cantidadVirus/5)):
            virus = Virus((pos_x,pos_y))
            #agregamos el virus creado a la colección de virus
            self.add(virus)
            #modificamos la posición en x con una posición random
            pos_x += random.randint(200,500)
        for i in range(round(cantidadVirus/5)):
            virus = Virus((pos_x,pos_y))
            #agregamos el virus creado a la colección de virus
            self.add(virus)
            #modificamos la posición en x con una posición random
            pos_x += random.randint(150,400)

#función que se ejecuta cuando pierdes (muestra textos)
def juego_terminado():
    #determinamos el texto que se va a ver
    fuente = pygame.font.SysFont("Consolas",60)
    if nueva_puntuacion == True:
        texto = fuente.render("NEW RECORD: "+str(round(puntuacion_mas_alta)), True, color_negro)
    else:
        texto = fuente.render("GAME OVER", True, color_negro)
    texto_rect = texto.get_rect()
    texto_rect.center = [ANCHO/2,ALTO*.4]
    #llamamos el texto a mostrarse en pantalla
    pantalla.blit(texto,texto_rect)
    pygame.display.flip()

def juego_terminado_TA():
    #determinamos el texto que se va a ver
    fuente = pygame.font.SysFont("Consolas",30)
    texto = fuente.render("Try Again", True, color_negro)
    texto_rect = texto.get_rect()
    texto_rect.center = [ANCHO/2,ALTO*.55]
    #llamamos el texto a mostrarse en pantalla
    pantalla.blit(texto,texto_rect)
    pygame.display.flip()

#función que muestra la puntuación
def mostrar_puntuacion():
    #determinamos el texto que se va a ver
    fuente = pygame.font.SysFont("Consolas",20)
    cadena = str(round(puntuacion)).zfill(5)
    texto = fuente.render(cadena, True, color_negro)
    texto_rect = texto.get_rect()
    texto_rect.center = [ANCHO*.90,15]
    #llamamos el texto a mostrarse en pantalla
    pantalla.blit(texto,texto_rect)

#función que muestra la puntuación más alta
def mostrar_puntuacion_mas_alta():
    #determinamos el texto que se va a ver
    fuente = pygame.font.SysFont("Consolas",20)
    cadena = "HI "+str(round(puntuacion_mas_alta)).zfill(5)
    texto = fuente.render(cadena, True, color_negro)
    texto_rect = texto.get_rect()
    texto_rect.center = [ANCHO*.75,15]
    #llamamos el texto a mostrarse en pantalla
    pantalla.blit(texto,texto_rect)

#definir interfaz
pantalla = pygame.display.set_mode((ANCHO,ALTO))

#Configurar titulo de la pantalla
pygame.display.set_caption("Ironhack vs Virus")

#crear reloj para definir tiempos de procesamiento
reloj = pygame.time.Clock()

#Ajustar que se pueda repetir la acción de una tecla si se mantiene presionada (se pone el retraso en milisegundos)
pygame.key.set_repeat(20)

#Crear los objetos con las clases que definimos arriba
jugador = Ironhack()
jugador_jugo = False
enemigos = Enemigos(100)
puntuacion = 0
puntuacion_mas_alta = 0
inicio_juego = False
game_over = False
fondo = Fondo()
fondo2 = Fondo()
#la posición de fondo2 va a ser despues de fondo (le va siguiendo)
fondo2.rect.midbottom = (fondo.rect.midbottom[0]+fondo.rect.width, ALTO+5)

#mantener abierta la interfaz hasta que ocurra un evento
while True:
    #Establecer FPS (frames por segundo) (el juego correra como máximo X veces por segundo )
    reloj.tick(60)

    #revisar los eventos
    for evento in pygame.event.get():
        #si se presiona la X de cerrar, se cierra el juego
        if evento.type == pygame.QUIT:
            sys.exit()
        #Jugador quiere saltar
        elif evento.type == pygame.KEYDOWN and jugador.rect.bottom <= ALTO*.80:
            jugador_jugo = True
            game_over = False

    #print("posición inicial",jugador.rect.bottom)
    #Actualizar posición del jugador
    if jugador_jugo == True:
        #print("no quiero parar",jugador.rect.bottom)
        jugador.update()
        if jugador.rect.bottom == ALTO*.80:
            #print("falso otra vez")
            jugador_jugo = False
            inicio_juego = True

    #Choque entre los objetos
    if pygame.sprite.spritecollide(jugador,enemigos,False):
        nueva_puntuacion = False
        inicio_juego = False
        game_over = True
        jugador_jugo = False
        jugador.rect.midbottom = (ANCHO*.10, ALTO*.80)
        enemigos = Enemigos(100)
        if puntuacion_mas_alta < puntuacion:
            puntuacion_mas_alta = puntuacion
            nueva_puntuacion = True
        puntuacion = 0

    #Empezo el juego cuando usuario da tecla SPACE
    if inicio_juego == True:
        #Hacemos que los virus se muevan
        enemigos.update()
        #Movimiento del fondo (cuando el fondo sale de la pantalla, se regresa atras del otro)
        fondo.update()
        fondo2.update()
        puntuacion += 0.1
        #print(fondo.rect.midbottom)
        if fondo.rect.midbottom[0] < -500:
            fondo.rect.midbottom = (fondo2.rect.midbottom[0]+fondo2.rect.width, ALTO+5)
        elif fondo2.rect.midbottom[0] < -500:
            fondo2.rect.midbottom = (fondo.rect.midbottom[0]+fondo.rect.width, ALTO+5)

    #mostar texto de game over cuando pierde
    if game_over == True:
        juego_terminado()
        juego_terminado_TA()

    #Rellenamos la pantalla con el color de fondo
    pantalla.fill(color_blanco)

    #Mostramos texto de puntuación
    mostrar_puntuacion()

    #Mostramos texto de puntuación
    mostrar_puntuacion_mas_alta()

    #Dibujar objeto fondo en pantalla
    pantalla.blit(fondo2.image, fondo2.rect)
    pantalla.blit(fondo.image, fondo.rect)

    #Dibujar objeto ironhack del jugador en pantalla
    pantalla.blit(jugador.image, jugador.rect)

    #Dibujar colección de virus en pantalla
    enemigos.draw(pantalla)

    #Actualizar los elementos en pantalla
    pygame.display.flip()