from flask import Flask, request, render_template, flash, redirect, url_for, g, session
# import simplejson

import pyglet.event
import sys
import os
from gevent.wsgi import WSGIServer
from random import randint

# ip address locator
from netifaces import interfaces, ifaddresses, AF_INET

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)  # Unique for each bootup
app.config.from_object(__name__)
DEFAULT_PORT = 9000

class WebEventDispatcher(pyglet.event.EventDispatcher):
    status = 'offline'

    def reset_display(self):
        self.dispatch_event('on_reset')

    def change_bgcolor(self, color=None):
        self.dispatch_event('on_change_bgcolor', color)

    def add_text(self, text=None):
        self.dispatch_event('on_add_text', text)

    def check_status(self):
        print 'sending ping...'
        self.dispatch_event('ping')

    def pong(self):
        # It's alive!
        print 'pong!'
        self.status = 'online'

    def on_change_bgcolor(self, text):
        '''
            Default event handler...
        '''
        print 'on_change_bgcolor was called!'

WebEventDispatcher.register_event_type("on_change_bgcolor")
WebEventDispatcher.register_event_type("on_add_text")
WebEventDispatcher.register_event_type("on_reset")
WebEventDispatcher.register_event_type("ping")
eventdispatcher = WebEventDispatcher()


################################## Utility Function ##############################
# From: http://stackoverflow.com/questions/7835030/obtaining-client-ip-address-from-a-wsgi-app-using-eventlet
def get_ipaddresses():
    ret = []
    for ifaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'0.0.0.0'}])]
        if len(addresses) > 0:
            ret.append((ifaceName, addresses[0]))
    return ret

def to_index():
    return redirect(url_for('index'))

@app.before_request
def before_request():
    if 'favicon' in request.path or 'static' in request.path:
        return
    eventdispatcher.check_status()


@app.context_processor
def global_vars():
    '''
        Passed directly into all templates, very cool.

        Called for every template request
    '''
    return dict({'status': eventdispatcher.status})

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add_text/")
@app.route("/add_text/<text>")
def add_text(text=''):
    print '/add_text/ with text: (%s)' % text
    eventdispatcher.add_text(text)
    flash("add_text event triggered successfully", "info")
    return to_index()

@app.route("/change_bgcolor/")
@app.route("/change_bgcolor/<color1>/<color2>/<color3>")
def change_bgcolor(color1=None, color2=None, color3=None):
    print '/change_bgcolor/'
    if color1 is None and color2 is None and color3 is None:
        eventdispatcher.change_bgcolor((randint(0, 255), randint(0, 255), randint(0, 255)))
    else:
        try:
            eventdispatcher.change_bgcolor((int(color1), int(color2), int(color3)))
        except ValueError:
            flash("Bad Color Values! Use rgb: (0:255, 0:255, 0:255)")
            return to_index()
    flash("change_bgcolor event triggered successfully", "info")
    return to_index()


@app.route("/reset/")
def reset():
    print '/reset/'
    eventdispatcher.reset_display()
    flash("reset_display event triggered successfully", "info")
    return to_index()
###################################################################

def runWebController(port=DEFAULT_PORT):
    '''
            Sets up the pointer to the display instance, runs the system
            No guarantees if displayInstance is set to None
    '''
    return gevent_controller(DEFAULT_PORT, False)


def gevent_controller(port, serve_forever=True):
    http_server = WSGIServer(('', int(port)), app)
    addresses = get_ipaddresses()
    sys.stderr.write("Web Client listening on:\n")
    for interface, ip in addresses:
        if ip != '0.0.0.0':
            sys.stderr.write("   http://%s:%d (%s)\n" % (ip, port, interface))
        else:
            sys.stderr.write("   %s has no ip address to listen on\n" % interface)
        sys.stderr.flush()

    if serve_forever:
        print "... starting serve_forever()"
        http_server.serve_forever()
        print "... serve_forever finished."
    else:
        http_server.start()
        return http_server


# def tornado():
#   from tornado.wsgi import WSGIContainer
#   from tornado.httpserver import HTTPServer
#   from tornado.ioloop import http_serverg

#   IOLoop = HTTPServer(WSGIContainer(app))
#   http_server.listen(5000)
#   IOLoop.instance().start()

# def twisted():
#   from twisted.python import log
#   from twisted.internet import reactor
#   from twisted.web.server import Site
#   from twisted.web.wsgi import WSGIResource

#   resource = WSGIResource(reactor, reactor.getThreadPool(), app)
#   site = Site(resource)
#   reactor.listenTCP(int(5000), site)
#   reactor.run()

if __name__ == "__main__":
    # runWebController()
    #twisted()
    http_server = gevent_controller(8080, False)
    while True:
        http_server._stopped_event.wait(.0001)
        #print "tick"
    print "... start() called successfully"
