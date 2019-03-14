# Universidad del Valle de Guatemala
# Graficas por Computadora - Seccion 10
# Maria Fernanda Estrada 14198
# Funciones para crear un escritor de imagenes BMP
# Codigo base en ejemplo visto en clase
# Se usan coordenadas barometricas para rellenar triangulos





import struct
from collections import namedtuple
from random import randint


def char(c): # Funcion vista en clase
    return struct.pack("=c", c.encode('ascii'))


def word(c): # Funcion vista en clase
    return struct.pack("=h", c)


def dword(c): # Funcion vista en clase
    return struct.pack("=l", c)


def color(r, g, b): # Funcion vista en clase, para tener en bytes el color ingresado
    return bytes([b, g, r])


# Vectores
V2 = namedtuple('Vertex2', ['x', 'y'])
V3 = namedtuple('Vertex3', ['x', 'y', 'z'])


# Operaciones de vector (Visto en clase)

# Suma
def suma(v0, v1):
    return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

# Resta
def resta(v0, v1):
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

# Multiplicar por escalar
def mul(v0, k):
    return V3(v0.x * k, v0.y * k, v0.z * k)

# Producto punto
def punto(v0, v1):
    return (v0.x * v1.x) + (v0.y * v1.y) + (v0.z * v1.z)

# Producto cruz
def cruz(v0, v1):
    return V3(
        v0.y * v1.z - v0.z * v1.y,
        v0.z * v1.x - v0.x * v1.z,
        v0.x * v1.y - v0.y * v1.x
    )

# Largo de vector
def largov(v0):
    return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

# Normalizar vector
def norm(v0):
    l = largov(v0)
    if not l:
        return V3(0, 0, 0)
    return V3(v0.x/l, v0.y/l, v0.z/l)



# Clase Bitmap, para generar la imagen
class Bitmap(object):

    # Constructor del bitmap
    def __init__(self, width, height):
        # Valores iniciales
        self.width = width
        self.height = height
        self.color_clear = color (0, 0, 0)
        self.color_point = color (0, 0, 0)
        self.vp_x = 0 # Para viewport => vp
        self.vp_y = 0
        self.vp_width = 0
        self.vp_height = 0
        self.framebuffer = []
        self.clear()
    
    # Funcion dentro de Bitmap para modificar alto y ancho, solo cambia los valores actuales
    def cambioWidthHeight(self, width, height):
        self.width = width
        self.height = height

    # Funcion para colorear de un color toda la pantalla
    def clear(self):
        self.framebuffer = [
            [self.color_clear for x in range(self.width)]
            for y in range(self.height)
        ]

        self.zbuffer = [
            [-float('inf') for x in range(self.width)]
            for y in range(self.height)
        ]
    
    # Funcion para modificar color del clear
    def clearcolor(self, r, g, b):
        self.color_clear = color(r, g, b)

    # Funcion para generar Viewport, area de imagen sobre la cual se dibujara
    def viewport(self, x, y, width, height):
        self.vp_x = x
        self.vp_y = y
        self.vp_width = width-1 # Se le resta 1 porque se sale por uno del index si no se coloca
        self.vp_height = height-1

    # Funcion para generar el archivo de imagen, vista en clase
    def write(self, filename):
        f = open(filename, 'bw')
        # File Header 14
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + (self.width*self.height*3)))
        f.write(dword(0))
        f.write(dword(14 + 40))
        # Image Header 40
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width*self.height*3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        for x in range(self.height):
            for y in range(self.width):
                f.write(self.framebuffer[x][y])
        
        f.close()
    
    # Funcion para cambiar el color del punto a dibujar en el viewport
    def colorPoint(self, r, g, b):
        self.color_point = color(r, g, b)

    # Funcion para crear un punto dentro del viewport
    def point(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        else:
            self.framebuffer[y][x] = self.color_point



# Funciones "globales"
bm = Bitmap(0,0)


# Inicializar Bitmap con valores default
def glInit():
    global bm 
    bm = Bitmap(600,400)


# Crear ventana con width y height como parametros
def glCreateWindow(width, height):
    bm.cambioWidthHeight(width, height) # Usando funcion Bitmap para cambiar el ancho y alto


# Crear area sobre la cual se dibujara
def glViewPort(x, y, width, height):
    bm.viewport(x, y, width, height)


# Limpiar ventana, usando funcion en Bitmap
def glClear():
    bm.clear()


# Cambiar color de clear
def glClearColor(r, g, b):
    bm.clearcolor(int(r*255), int(g*255), int(b*255))


# Generar un punto en el viewport
def glVertex(x, y):
    equis = (((x+1)/2)*(bm.vp_width)) + (bm.vp_x)
    ye = (((y+1)/2)*(bm.vp_height)) + (bm.vp_y)
    bm.point(equis, ye)


# Cambiar el color de un punto
def glColor(r, g, b):
    bm.colorPoint(int(r*255), int(g*255), int(b*255))


# Generar la imagen en un archivo
def glFinish():
    bm.write("out.bmp")


# Dibujar una linea recta de (x0, y0) a (x1, y1). Recibe parametros de -1 a 1
# Codigo base visto en clase
def glLine(x1, y1, x2, y2):

    # Hay que transformar las x1, y1, x2, y2 a posiciones absolutas en pixeles para que funcione
    x1 = int(bm.vp_width * ((x1+1)/2))
    y1 = int(bm.vp_height * ((y1+1)/2))
    x2 = int(bm.vp_width * ((x2+1)/2))
    y2 = int(bm.vp_height * ((y2+1)/2))
    
    # Diferencia en distancias
    dy = abs(y2 - y1)
    dx = abs(x2 - x1)

    # True si la division daria mayor a 0
    fraccion = dy > dx

    # Si la division da mayor a 0, intercambiar valores
    if fraccion:
        eq1 = x1
        ye1 = y1
        eq2 = x2
        ye2 = y2
        x1 = ye1
        y1 = eq1
        x2 = ye2
        y2 = eq2

    # True si la pendiente es negativa
    negativa = x1 > x2

    # Si es negativa la pendiente, voltear
    if negativa:
        equis1 = x1
        yee1 = y1
        equis2 = x2
        yee2 = y2
        x1 = equis2
        y1 = yee2
        x2 = equis1
        y2 = yee1

    # Diferencia en distancias
    dy = abs(y2 - y1)
    dx = abs(x2 - x1)
    
    offset = 0 * 2 * dx
    threshold = 0.5 * 2 * dx

    # Para graficar
    y = y1
    for x in range (x1, x2 + 1):
        if fraccion:
            bm.point(y, x)
        else:
            bm.point(x, y)
        offset += dy * 2 # Hay que multiplicarlo por 2, sino queda en un menor angulo
        if offset >= threshold:
            if y1 < y2:
                y = y + 1 
            else:
                y = y - 1
            threshold += 1 * 2 * dx


# Dibujar una linea recta de (x0, y0) a (x1, y1). Recibe parametros en coordenadas absolutas (para la tarea 3)
# Codigo base visto en clase
def glLineABS(x1, y1, x2, y2):
    
    # Diferencia en distancias
    dy = abs(y2 - y1)
    dx = abs(x2 - x1)

    # True si la division daria mayor a 0
    fraccion = dy > dx

    # Si la division da mayor a 0, intercambiar valores
    if fraccion:
        eq1 = x1
        ye1 = y1
        eq2 = x2
        ye2 = y2
        x1 = ye1
        y1 = eq1
        x2 = ye2
        y2 = eq2

    # True si la pendiente es negativa
    negativa = x1 > x2

    # Si es negativa la pendiente, voltear
    if negativa:
        equis1 = x1
        yee1 = y1
        equis2 = x2
        yee2 = y2
        x1 = equis2
        y1 = yee2
        x2 = equis1
        y2 = yee1

    # Diferencia en distancias
    dy = abs(y2 - y1)
    dx = abs(x2 - x1)
    
    offset = 0 * 2 * dx
    threshold = 0.5 * 2 * dx

    # Para graficar
    y = y1
    for x in range (x1, x2 + 1):
        if fraccion:
            bm.point(y, x)
        else:
            bm.point(x, y)
        offset += dy * 2 # Hay que multiplicarlo por 2, sino queda en un menor angulo
        if offset >= threshold:
            if y1 < y2:
                y = y + 1 
            else:
                y = y - 1
            threshold += 1 * 2 * dx


# Funcion bbox (visto en clase)
def bbox(A, B, C):
    xs = sorted([A.x, B.x, C.x])
    ys = sorted([A.y, B.y, C.y])
    return V2(xs[0], ys[0]), V2(xs[2], ys[2])


# Funcion barycentric (visto en clase)
def barycentric(A, B, C, P):
    cx, cy, cz = cruz(
        V3(B.x - A.x, C.x - A.x, A.x - P.x),
        V3(B.y - A.y, C.y - A.y, A.y - P.y)
    )

    if cz == 0:
        return -1, -1, -1
    
    # Coordenadas baricentricas
    u = cx/cz
    v = cy/cz
    w = 1 - (u + v)

    return w, v, u


# Rellenar triangulos (visto en clase)
def triangle(A, B, C, TAcord, TBcord, TCcord, texture = None, intensity = 1):
    bbox_min, bbox_max = bbox(A, B, C)

    for x in range(bbox_min.x, bbox_max.x + 1):
        for y in range(bbox_min.y, bbox_max.y + 1):
            w, v, u = barycentric(A, B, C, V2(x, y))

            # Si estan fuera del triangulo, no pintar
            if w < 0 or v < 0 or u < 0:
                continue
            
            # Ver el color del pixel de textura
            if texture:
                tA, tB, tC = TAcord, TBcord, TCcord
                tx = tA.x * w + tB.x * v + tC.x * u
                ty = tA.y * w + tB.y * v + tC.y * u
                color = texture.get_Color(tx, ty, intensity)

            z = A.z * w + B.z * v + C.z * u

            # Si z es mayor que el z buffer, pintar y cambiar valor zbuffer
            # Esto sirve para saber que z esta mas arriba y cual mas atras
            if z > bm.zbuffer[x][y]:
                bm.colorPoint(*color)
                bm.point(x, y)
                bm.zbuffer[x][y] = z