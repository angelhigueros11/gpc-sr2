# Graficas por computador
# Angel Higueros - 20460
# SR2

import struct
from cube import Obj
import main

# Métodos de escritura
def char(c): 
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    return struct.pack('=h', w)

def dword(d):
    return struct.pack('=l', d)

def color(r, g, b):
    return bytes([b, g, r])



class Render(object):

    def glInit(self, filename = 'sr2.bmp'):
        self.filename = filename 
        self.width = 100 
        self.height = 100
        self.viewport_x = 0 
        self.viewport_y = 0 
        self.viewport_width = 100 
        self.viewport_height = 100
        self.current_color = color(255, 255, 255) # por defecto blanco
        self.vertex_color = color(200, 0, 0) # por defecto rojo
        self.framebuffer = []
        self.glClear()

    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height

    def glViewPort(self, x, y, width, height):

        if self.width < x + width or self.height < y + height:
            print("[!] El viewport debe estar dentro de las medidas de la pantalla")
            self.viewport_x = 0
            self.viewport_y = 0
            self.viewport_width = self.width
            self.viewport_height = self.height
            self.glClear()
        else:
            self.viewport_x = x
            self.viewport_y = y
            self.viewport_width = width
            self.viewport_height = height
            self.glClear()

    def glClear(self):
        self.framebuffer= [
            [color(0, 0, 0) for x in range(self.width)]
            for y in range(self.height)
        ]

        for x in range(self.width):
            for y in range(self.height):
                if x >= self.viewport_x and x <= self.viewport_width and y >= self.viewport_y and y <= self.viewport_height:
                    self.framebuffer[x][y] = self.current_color 

    def glClearColor(self, r, g, b):
        self.current_color = color(r, g, b)

    def glVertex(self, x, y):

        # convertir coordenadas normalizadas a cordenadas del dispositivo
        half_size_width = self.viewport_width / 2
        half_size_height = self.viewport_height / 2

        coord_x = int((( x + 1 ) * half_size_width ))
        coord_y = int((( y + 1 ) * half_size_height ))

        self.framebuffer[coord_x][coord_y] = self.vertex_color

    def point(self, x, y):
        if 0 < x < self.width and 0 < y < self.height:
            self.framebuffer[x][y] = self.vertex_color

    def line(self, x0, y0, x1, y1):
        x0 = round(x0)
        y0 = round(y0)
        x1 = round(x1)
        y1 = round(y1)

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        if steep:
            x0, y0 =  y0, x0
            x1, y1 =  y1, x1

        if x0 > x1:
            x0, x1 = x1, x0 
            y0, y1 = y1, y0 

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        threshold = dx
        y =  y0

        for x in range(x0, x1 + 1):

            
            if steep:
                r.point(y, x)
            else:
                r.point(x, y)

            # offset += (dy/dx) * dx * 2
            offset += dy * 2

            if offset > threshold:
                y += 1 if y0 < y1 else  -1
                # threshold += 1 * dx * 2
                threshold += dx * 2


    def transform_vertex(self, vertex, scale, translate):
        return [
            (vertex[0] * scale[0]) + translate[0],
            (vertex[1] * scale[1]) + translate[1]
        ]

    def glRenderObject(self, obj, scale_factor, translate_factor):
        for face in obj.faces:
            if len(face) == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 =  r.transform_vertex(obj.vertices[f1], scale_factor, translate_factor)
                v2 =  r.transform_vertex(obj.vertices[f2], scale_factor, translate_factor)
                v3 =  r.transform_vertex(obj.vertices[f3], scale_factor, translate_factor)

                r.line(v1[0], v1[1], v2[0], v2[1])
                r.line(v2[0], v2[1], v3[0], v3[1])
                r.line(v3[0], v3[1], v1[0], v1[1])

            if len(face) == 4:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1

                v1 =  r.transform_vertex(obj.vertices[f1], scale_factor, translate_factor)
                v2 =  r.transform_vertex(obj.vertices[f2], scale_factor, translate_factor)
                v3 =  r.transform_vertex(obj.vertices[f3], scale_factor, translate_factor)
                v4 =  r.transform_vertex(obj.vertices[f4], scale_factor, translate_factor)

                r.line(v1[0], v1[1], v2[0], v2[1])
                r.line(v2[0], v2[1], v3[0], v3[1])
                r.line(v3[0], v3[1], v1[0], v1[1])
                r.line(v4[0], v4[1], v1[0], v1[1]) 

    def glColor(self, r, g, b):
        self.vertex_color = color(r, g, b)

    def glFinish(self):
        f = open(self.filename, 'bw')

        # Pixel header
        f.write(char('B'))
        f.write(char('M'))
        # tamaño archivo = 14 header + 40  info header + resolucion
        f.write(dword(14 + 40 + self.width * self.height * 3)) 
        f.write(word(0))
        f.write(word(0))
        f.write(dword(14 + 40))

        # Info header
        f.write(dword(40)) # tamaño header
        f.write(dword(self.width)) # ancho
        f.write(dword(self.height)) # alto
        f.write(word(1)) # numero de planos (siempre 1)
        f.write(word(24)) # bits por pixel (24 - rgb)
        f.write(dword(0)) # compresion
        f.write(dword(self.width * self.height * 3)) # tamaño imagen sin header
        f.write(dword(0)) # resolucion
        f.write(dword(0)) # resolucion
        f.write(dword(0)) # resolucion
        f.write(dword(0)) # resolucion


        for x in range(self.height):
            for y in range(self.width):
                f.write(self.framebuffer[y][x])


# IMPLEMENTACION
r = Render()
r.glInit('sr2-line.bmp')
r.glCreateWindow(1000, 1000)
r.glViewPort(0,0, 1000, 1000)
r.glClearColor(0, 0, 0)
r.glClear()

house = Obj('casa.obj')
scale_factor = (100, 100)
translate_factor = (500, 500)
r.glRenderObject(house, scale_factor, translate_factor)


r.glFinish()
