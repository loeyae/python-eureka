import os
import signal

import tornado.ioloop
import tornado.httpserver
from tornado.web import Application
from tornado.httpclient import HTTPError
from tornado.routing import Router
from tornado.web import RequestHandler
from tornado.escape import json_encode

from Config import config
from ip import main as ip_main
from EurekaClient import EurekaClient

Client = EurekaClient()


class ApiResult(object):
    code = 200
    msg = 'Ok'
    data = None

    def __str__(self):
        return json_encode({'code': self.code, 'msg': self.msg, 'data': self.data})

    def ok(self, data):
        self.data = data
        return str(self)

    def fail(self, msg, data):
        self.code = 500
        self.msg = msg
        self.data = data
        return str(self)


def home(request: tornado.httputil.HTTPServerRequest):
    return ApiResult().ok(None)


resources = {}
resources['/'] = lambda request: home(request)
resources['/actuator/info'] = lambda request: Client.actuator.info()
resources['/actuator/health'] = lambda request: Client.actuator.health(Client)


class GetResource(RequestHandler):
    def get(self, path):
        self.head
        if path not in resources:
            raise HTTPError(404)
        self.finish(resources[path](self.request))


class PostResource(RequestHandler):
    def post(self, path):
        if path not in resources:
            raise HTTPError(404)
        self.finish(resources[path](self.request))


class HTTPMethodRouter(Router):
    def __init__(self, app):
        self.app = app

    def find_handler(self, request, **kwargs):
        handler = GetResource if request.method == "GET" else PostResource
        return self.app.get_handler_delegate(request, handler, path_args=[request.path])


if __name__ == "__main__":
    application = Application(static_path=os.path.join(os.path.dirname(__file__), 'statics'))
    router = HTTPMethodRouter(application)
    server = tornado.httpserver.HTTPServer(router)
    server.listen(config.SERVER_PORT)


    def ip_run():
        ip_main()


    def eureka():
        return Client.run()


    tornado.ioloop.PeriodicCallback(ip_run, 5000).start()
    tornado.ioloop.PeriodicCallback(eureka, 10000).start()
    instance = tornado.ioloop.IOLoop.current()

    def on_shutdown():
        return Client.remove()

    signal.signal(signal.SIGINT, lambda sig, frame: instance.add_callback_from_signal(on_shutdown))
    # signal.signal(signal.SIGTERM, lambda sig, frame: instance.add_callback_from_signal(on_shutdown))

    instance.start()
