# -*- coding: utf-8 -*-

#Copyright (c) 2007-8, Playful Invention Company.
#Copyright (c) 2008-9, Walter Bender

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import pango

class Sprites:
    def __init__(self, canvas):
        self.canvas = canvas
        self.area = self.canvas.window
        self.gc = self.area.new_gc()
        self.cm = self.gc.get_colormap()
        self.color = self.cm.alloc_color('black')
        self.fd = pango.FontDescription('Sans')
        self.list = []

    def get_sprite(self, i):
        if i < 0 or i > len(self.list)-1:
            return(None)
        else:
            return(self.list[i])

    def length_of_list(self):
        return(len(self.list))

    def append_to_list(self,spr):
        self.list.append(spr)

    def insert_in_list(self,spr,i):
        if i < 0:
            self.list.insert(0, spr)
        elif i > len(self.list)-1:
            self.list.append(spr)
        else:
            self.list.insert(i, spr)

    def remove_from_list(self,spr):
        if spr in self.list:
            self.list.remove(spr)

    def find_sprite(self, pos):
        list = self.list
        list.reverse()
        for spr in list:
            if spr.hit(pos): return spr
        return None

    def redraw_sprites(self):
        for spr in self.list:
            spr.draw()


class Sprite:
    def __init__(self, sprites, x, y, image):
        self.x = x
        self.y = y
        self.layer = 100
        self.label = None
        self.set_image(image)
        self.sprites = sprites
        self.sprites.append_to_list(self)

    def set_image(self, image):
        self.image = image
        if isinstance(self.image,gtk.gdk.Pixbuf):
            self.width = self.image.get_width()
            self.height = self.image.get_height()
        else:
            self.width, self.height = self.image.get_size()

    def move(self, pos):
        self.inval()
        self.x,self.y = pos
        self.inval()

    def set_shape(self, image):
        self.inval()
        self.set_image(image)
        self.inval()

    def set_layer(self, layer):
        self.sprites.remove_from_list(self)
        self.layer = layer
        for i in range(self.sprites.length_of_list()):
            if layer < self.sprites.get_sprite(i).layer:
                self.sprites.insert_in_list(i, self)
                self.inval()
                return
        self.sprites.append_to_list(self)
        self.inval()

    def set_label(self, label):
        if type(label) is str or type(label) is unicode:
            self.label = label.replace("\0"," ")
        else:
            self.label = str(label)
        inval(self)

    def hide(self):
        self.inval()
        self.sprites.remove_from_list(self)

    def inval(self):
        self.sprites.area.invalidate_rect(
            gtk.gdk.Rectangle(self.x,self.y,self.width,self.height), False)

    def draw(self):
        if isinstance(self.image,gtk.gdk.Pixbuf):
            self.sprites.area.draw_pixbuf(
                self.sprites.gc, self.image, 0, 0, self.x, self.y)
        else:
            self.sprites.area.draw_drawable(
                self.sprites.gc, self.image, 0, 0, self.x, self.y, -1, -1)

    def hit(self, pos):
        x, y = pos
        if x < self.x:
            return False
        if x > self.x+self.width:
            return False
        if y < self.y:
            return False
        if y > self.y+self.height:
            return False
        return True

    def draw_label(self, scale, horiz_align="center", vert_align="middle"):
        if self.label is None:
            return
        pl = self.sprites.canvas.create_pango_layout(self.label)
        self.sprites.fd.set_size(int(scale*pango.SCALE))
        pl.set_font_description(self.sprites.fd)
        w = pl.get_size()[0]/pango.SCALE
        if horiz_align == "center":
            x = int(((self.x+self.width)/2)-(w/2))
        elif horiz_align == 'left':
            x = self.x
        else: # right align
            x = self.x+self.width-w
        h = pl.get_size()[1]/pango.SCALE
        if vert_align == "middle":
            y = int(((self.y+self.height)/2)-h/2)
        elif vert_align == "top":
            y = int(h/2)
        else: # bottom align
            y = int(self.height-h)
        self.sprites.gc.set_foreground(self.sprites.color)
        self.sprites.area.draw_layout(self.sprites.gc, x, y, pl)
