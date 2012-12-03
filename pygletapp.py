'''
    Main point of entry for the MediaDisplay engine

    We are using cocos2d for the presentation layer
'''
from __future__ import division  # Float Division
from random import randint
import os
import sys
import cocos
from cocos.director import director
import pyglet.media
from pyglet import font, image
import pyglet.text
from pyglet import clock  # For http system...
from pyglet.gl import *
from pyglet.window import key
from pyglet.image.codecs import ImageDecodeException
import pyglet.image

from cocos.actions import *
from cocos.layer import *
from cocos.scenes.transitions import *
from cocos.sprite import *
from cocos import text
import random
import flask_api
import time

FULLSCREEN = False
WEBSERVER = True

director.init(resizable=True, width=1024, height=768)
if FULLSCREEN:
    director.window.set_fullscreen(True)

class QuitMediaServer(Exception):
    pass

class localDispatcher(pyglet.event.EventDispatcher): pass
localDispatcher.register_event_type("on_change_bgcolor")
localdispatcher = localDispatcher()


def http_poller(dt, http_server):
    '''
            Polls the http server for gevent wait() events
    '''
    # dt is like 0.01 or so, be sure to wait less than that to not hold pyglet up
    #print 'polling', dt,
    http_server._stopped_event.wait(.0001)
    #print 'finished'

class ForFunLayer(cocos.layer.Layer):
    '''
            A demo layer... for fun!
    '''
    is_event_handler = True
    objects = []

    def __init__(self):
        '''
                initialize the scrolling text and color
        '''
        super(ForFunLayer, self).__init__()
        x, y = director.get_window_size()
        title = text.Label(
            "CincyPy Flasklet Demo", (x / 2, y / 2), font_name='Gill Sans',
            font_size=60, anchor_x='center', anchor_y='center')
        title.element.color = (255, 255, 0, 255)
        self.objects.append(title)
        self.add(title)

        # For handling of on_add_text
        flask_api.eventdispatcher.push_handlers(self)
        localdispatcher.push_handlers(self)

    def on_change_bgcolor(self, color=None):
        # Add a quick bg layer to the bottom of the stack
        if color == None:
            color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.add(cocos.layer.ColorLayer(color[0], color[1], color[2], 255), z=-1)

    def on_add_text(self, t):
        '''
            Update the scrolling text
        '''
        x, y = director.get_window_size()
        l = text.Label(t, (randint(0,x - 100), randint(0,y - 50)), font_name='Gill Sans',
            font_size=40, anchor_x='center', anchor_y='center')
        l.element.color = (randint(0, 255), randint(0, 255), randint(0, 255), 255)
        self.objects.append(l)
        self.add(l)

    def on_reset(self):
        '''
            Reset the screen - note: objects are not actually deleted
        '''
        print 'here we go'
        for o in self.objects:
            self.remove(o)
            del o
        self.objects = []

    def on_key_press(self, keyp, mod):
        if keyp in (key.ENTER,):
            # Dispatch an event rather than directly call self()
            flask_api.eventdispatcher.add_text("your lucky number is %d" % (randint(0, 255)))
        elif keyp in (key.Q,):
            director.terminate_app = True
        elif keyp in (key.B,):
            # Dispatch a local event, rather than a flask_api.eventdispatcher event
            localdispatcher.dispatch_event("on_change_bgcolor")
        elif keyp in (key.R,):
            self.on_reset()

    def reset(self, offset_text=True):
        pass

    def ping(self):
        flask_api.eventdispatcher.pong()

if __name__ == "__main__":
    # Register Event Handler
    http_server = flask_api.runWebController()
    if http_server:
        print "web api started successfully!"
    else:
        # TODO add exception handling
        print "unable to start web api"

    # Schedule clock to update the http poller
    clock.schedule(http_poller, http_server)

    # initiate the pyglet run loop
    director.run(cocos.scene.Scene(ForFunLayer()))