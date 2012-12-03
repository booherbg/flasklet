Flask/gevent/Bootstrap + pyglet = Fun
====================

A barebones flask web interface that controls a pyglet app. Uses gevent 
for web serving and hooks into pyglet's run loop, making for a single 
threaded paradigm. Uses Twitter Bootstrap for easing front-end anxiety.

This is meant as an example project, feel free to fork and have fun with it.
Can be run entirely with virtualenv

Fun features:
   * First known documented example of hooking gevent's HTTPServer into 
     pyglet's run loop, making the entire application single threaded
   * WebAPI communicates with pyglet via built in event-drive framework
   * Uses Bootstrap's components when possible for ease-of-use

Blaine Booher
blaine@cliftonlabs.com

Setup
=====
```bash
$ git clone http://github.com/booherbg/flasklet.git
$ virtualenv --no-site-packages flasklet
$ source flasklet/bin/activate
$ pip install -r requirements.txt
```

If you have a repository system that has a broken pyglet repo, use this:
pip install hg+https://pyglet.googlecode.com/hg/
