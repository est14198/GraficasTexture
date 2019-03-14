# Universidad del Valle de Guatemala
# Graficas por Computadora - Seccion 10
# Maria Fernanda Estrada 14198
# Cargar un archivo obj y leer/mostrar lo que lleva dentro
# Codigo base en ejemplo visto en clase





import struct
import Funciones2 as imagen
from random import randint
from collections import namedtuple

# Vectores
V2 = namedtuple('Vertex2', ['x', 'y'])
V3 = namedtuple('Vertex3', ['x', 'y', 'z'])


# Clase que carga el obj, lee el obj y dibuja el modelo
class Obj(object):

    # Constructor
    def __init__(self, filename, filenameMaterial = None):
        # Para leer el archivo
        with open(filename) as f:
            self.lines = f.read().splitlines()
        # Para leer el archivo de materiales
        with open(filenameMaterial) as f:
            self.linesMtl = f.read().splitlines()
        # Inicializar todo en cero y leer
        self.vertices = []
        self.tvertices = []
        self.caras = []
        self.materialesDic = {} # Diccionario de colores
        self.read()
        self.readMtl()
    
    # Leer e interpretar el archivo obj
    def read(self):
        materialActual = ''
        # Para cada linea leida en el documento
        for line in self.lines:
            # Si no esta vacia hacer lo siguiente
            if line:
                # Separar la primera letra del resto. Lo primero es el prefix v (vertice) o f (cara).
                prefix, value = line.split(' ', 1) # Se coloca 1 para que tome 1 linea a la vez
                # Si es un vertice, colocar en el array de vertices
                if prefix == 'v':
                    # Separa los valores despues de la v por espacios, los mapea a un float (cast) y los vuelve una lista despues a los tres
                    listaV = list(map(float, value.split(' ')))
                    self.vertices.append(listaV)
                # Si es un vertice de textura, colocar en el array de vertices de textura
                elif prefix == 'vt':
                    # Separa los valores despues de la vt por espacios, los mapea a un float (cast) y los vuelve una lista despues a los tres
                    listaVt = list(map(float, value.split(' ')))
                    self.tvertices.append(listaVt)
                # Si es una cara, colocar en el array de caras. Este sera un array de arrays
                elif prefix == 'f':
                    # Separar por espacio
                    listaF1 = value.split(' ')
                    listaX = []
                    # Ahora separar por guiones y castear a int
                    for cara in listaF1:
                        listaF2 = cara.split('/')
                        listaF = []
                        for l2 in listaF2:
                            if l2:
                                listaF.append(int(l2))
                            else:
                                listaF.append(0)
                        # Se guarda el material antes de las caras a las que se aplicaran
                        listaF.append(materialActual)
                        listaX.append(listaF)
                    self.caras.append(listaX)
                # Para ver que material es el que toca a ciertas caras
                elif prefix == 'usemtl':
                    materialActual = value

    # Leer e interpretar el archivo mtl
    def readMtl(self):
        # Guardar el nombre del material
        nombreMaterial = ''
        for line in self.linesMtl:
             # Si no esta vacia hacer lo siguiente
            if line:
                prefix, value = line.split(' ', 1) # Se coloca 1 para que tome 1 linea a la vez
                # Guardar el nombre de material
                if prefix == 'newmtl':
                    nombreMaterial = value
                # Guardar los valores rgb de ese material en un diccionario
                elif prefix == 'Kd':
                    coloresStr = value.split(' ')
                    listaColores = list(map(float, coloresStr))
                    self.materialesDic[nombreMaterial] = listaColores

    # Mandar los vertices y caras a la funcion glLine (en valores de -1 a 1 para traslacion y escala) (valores de 0 a 1 para textura)
    def load(self, traslacion, escala, textura = None):

        luz = V3(0, 0, 1) # La luz solo vendra hacia la pantalla, eje z

        for cara in self.caras:
            # Como nuestros valores solo van de 0 a 1, se debe hacer la conversion
            # Se agrega el valor en z que nos interesa para el zbuffer
            x1 = int(imagen.bm.vp_width * ((self.vertices[cara[0][0] - 1][0] + 1) / 2))
            y1 = int(imagen.bm.vp_width * ((self.vertices[cara[0][0] - 1][1] + 1) / 2))
            z1 = int(imagen.bm.vp_width * ((self.vertices[cara[0][0] - 1][2] + 1) / 2))
            x2 = int(imagen.bm.vp_width * ((self.vertices[cara[1][0] - 1][0] + 1) / 2))
            y2 = int(imagen.bm.vp_width * ((self.vertices[cara[1][0] - 1][1] + 1) / 2))
            z2 = int(imagen.bm.vp_width * ((self.vertices[cara[1][0] - 1][2] + 1) / 2))
            x3 = int(imagen.bm.vp_width * ((self.vertices[cara[2][0] - 1][0] + 1) / 2))
            y3 = int(imagen.bm.vp_width * ((self.vertices[cara[2][0] - 1][1] + 1) / 2))
            z3 = int(imagen.bm.vp_width * ((self.vertices[cara[2][0] - 1][2] + 1) / 2))

            # Ya con los valores convertidos, se crean los vectores v1, v2 y v3
            v1 = V3(x1, y1, z1)
            v2 = V3(x2, y2, z2)
            v3 = V3(x3, y3, z3)

            # Se calcula la normal de los vectores
            normal = imagen.norm(imagen.cruz(imagen.resta(v2, v1), imagen.resta(v3, v1)))
            # Calcular la intensidad de la luz 
            intens = imagen.punto(normal, luz)

            # Si no hay textura, colocar el color de los materiales
            if not textura:
                # Si se encuentra muy al fondo, no ponerle intensidad de luz
                if intens < 0:
                    continue
                # Pintar el color del material guardado por la intensidad para darle luz
                imagen.glColor(self.materialesDic[cara[0][3]][0]*intens, self.materialesDic[cara[0][3]][1]*intens, self.materialesDic[cara[0][3]][2]*intens)
                #imagen.triangle(v1, v2, v3)
            else:
                # Como los valores en la textura van de 0 a 1, ya no se necesitan convertir. Solo se resta 1 porque comienza en 1
                eq1 = int(textura.width * ((self.tvertices[cara[0][1] - 1][0]))) - 1
                ye1 = int(textura.height * ((self.tvertices[cara[0][1] - 1][1]))) - 1
                eq2 = int(textura.width * ((self.tvertices[cara[1][1] - 1][0]))) - 1
                ye2 = int(textura.height * ((self.tvertices[cara[1][1] - 1][1]))) - 1
                eq3 = int(textura.width * ((self.tvertices[cara[2][1] - 1][0]))) - 1
                ye3 = int(textura.height * ((self.tvertices[cara[2][1] - 1][1]))) - 1

                # Se crean los nuevos vectores de texturas
                t1 = V3(eq1, ye1, 0)
                t2 = V3(eq2, ye2, 0)
                t3 = V3(eq3, ye3, 0)

                # Hacer el triangulo
                imagen.triangle(v1, v2, v3, t1, t2, t3, textura, intens)


# Clase para colocar una textura sobre el modelo
class Texture(object):

    # Inicializar
    def __init__(self, path):
        self.path = path
        self.read()
    
    # Leer archivo de textura (visto en clase)
    def read(self):
        # Se debe seguir el formato de bmp
        image = open(self.path, "rb")
        image.seek(10)
        header_size = struct.unpack("=l", image.read(4))[0]
        image.seek(18)
        self.width = struct.unpack("=l", image.read(4))[0]
        self.height = struct.unpack("=l", image.read(4))[0]
        self.pixels = []
        image.seek(header_size)
        # Se lee el color de cada pixel y se guarda en un array
        for y in range(self.height):
            self.pixels.append([])
            for x in range(self.width):
                b = ord(image.read(1))
                g = ord(image.read(1))
                r = ord(image.read(1))
                self.pixels[y].append(imagen.color(b, g, r))
        image.close()

    
    # Obtener el color del pixel
    def get_Color(self, tx, ty, intensity = 1):
        x = int(tx)
        y = int(ty)
        return bytes(
            map(
                lambda b: round(b * intensity)
                    if (b * intensity) > 0 else 0,
                self.pixels[y][x]
            )
        )







# El porygon esta de lado porque de frente no se distingue mucho que es
imagen.glInit() # Inicializar SR1
imagen.glCreateWindow(1000,1000) # Cambia el tamano del window a 1000x1000
imagen.glClearColor(0, 0, 0) # Cambia el color de la ventana a negro
imagen.glClear() # Clear a ventana
imagen.glViewPort(0, 0, 1000, 1000) # Especificar en donde se dibujara
obj = Obj('Porygon22.obj', 'Porygon22.mtl') # Cargar el contenido del obj
text = Texture('camo.bmp') # Textura cao de 24 bits
obj.load((0,0), (1,1), text) # Dibujar el contenido del obj sin escala y con la textura cargada
imagen.glFinish() # Generar la imagen