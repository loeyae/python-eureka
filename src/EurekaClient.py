import time
import traceback
from typing import Callable

import tornado.ioloop
import tornado.httpclient
import Config
from tornado.escape import json_decode, json_encode
from enum import Enum


class EurekaStatus(Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    OUT_OF_SERVICE = 'OUT_OF_SERVICE'


class EurekaClient(object):
    REGISTERED = False
    STATUS = EurekaStatus.UP
    COUNTER = 0

    def __init__(self):
        self.application = {}
        self.config = Config.config
        self.secure_port = 443
        self.name = self.config.SERVER_NAME
        self.port = self.config.SERVER_PORT
        self.uri = self.config.get_eureka_uri()
        self.instance_id = self.name + "(" + str(self.config.IP_ADDRESS) + ":" + str(self.port) + ")"
        self.client = tornado.httpclient.AsyncHTTPClient()

    def set_status(self, status: EurekaStatus):
        self.STATUS = status

    def all(self):
        url = self.uri + 'apps'
        request = tornado.httpclient.HTTPRequest(url)

        def f(response: tornado.httpclient.HTTPResponse):
            if response.body:
                result = json_decode(response.body)
                application = result['applications']['application']
                for app in application:
                    self.application[str(app['name']).lower()] = application

        return self._request(request, f)

    def register(self):
        json = {
            "instance": {
                "instanceId": self.instance_id,
                "app": str(self.name).upper(),
                "appGroutName": None,
                "ipAddr": self.config.IP_ADDRESS,
                "sid": "na",
                "homePageUrl": self.config.get_uri(),
                "statusPageUrl": self.config.get_uri() + 'actuator/info',
                "healthCheckUrl": self.config.get_uri() + 'actuator/health',
                "secureHealthCheckUrl": None,
                "vipAddress": self.name,
                "secureVipAddress": self.name,
                "countryId": 1,
                "dataCenterInfo": {
                    "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                    "name": "MyOwn"
                },
                "hostName": self.config.IP_ADDRESS,
                "status": EurekaStatus.UP.value,
                "leaseInfo": None,
                "isCoordinatingDiscoveryServer": False,
                "lastUpdatedTimestamp": int(time.time() * 1000),
                "lastDirtyTimestamp": int(time.time() * 1000),
                "actionType": None,
                "asgName": None,
                "overridden_status": "UNKNOWN",
                "port": {
                    "$": self.port,
                    "@enabled": "true"
                },
                "securePort": {
                    "$": self.secure_port,
                    "@enabled": "false"
                },
                "metadata": {
                    "@class": "java.util.Collections$EmptyMap"
                }
            }
        }
        uri = self.uri + 'apps/' + self.name;
        request = tornado.httpclient.HTTPRequest(uri, 'POST')
        request.headers.add('content-type', 'application/json')
        request.body = json_encode(json)
        ret = self._request(request, lambda x: x)
        if ret:
            self.REGISTERED = True
        return ret

    def remove(self):
        uri = self.uri + 'apps/' + self.name + '/' + self.instance_id
        request = tornado.httpclient.HTTPRequest(uri, 'DELETE')
        return self._request(request, lambda x: x)

    def heartbeat(self):
        uri = self.uri + 'apps/' + self.name + '/' + self.instance_id
        request = tornado.httpclient.HTTPRequest(uri, 'PUT')
        request.body = json_encode({'status': self.STATUS.value})
        return self._request(request, lambda x: x)

    def status(self):
        uri = self.uri + 'apps/' + self.name + '/' + self.instance_id + '/status?value=' + self.STATUS.value
        request = tornado.httpclient.HTTPRequest(uri, 'PUT')
        request.body = json_encode({})
        return self._request(request, lambda x: x)

    async def _request(self, request: tornado.httpclient.HTTPRequest, callback: Callable):
        if not callback:
            callback = lambda response: True
        request.auth_username = self.config.EUREKA_USER
        request.auth_password = self.config.EUREKA_PWD
        request.headers.add('Accept', 'application/json;charset=UTF-8')
        try:
            response = await self.client.fetch(request)
            if len(response.body) > 1:
                callback(response)
                if response.body.startswith(b'{') and response.body.endswith(b'}'):
                    return json_decode(response.body.decode('UTF-8'))
                return response.body.decode('UTF-8')
            if response.code == 200 or response.code == 204:
                return True
            return False
        except tornado.httpclient.HTTPClientError as e:
            print(traceback.TracebackException.from_exception(e))
            return False

    async def run(self):
        if not self.REGISTERED:
            await self.register()
        else:
            if self.COUNTER > 5:
                self.COUNTER = 0
                await self.status()
            else:
                self.COUNTER += 1
                await self.heartbeat()
                await self.all()

    class actuator():

        @classmethod
        def info(cls):
            return json_encode([])

        @classmethod
        def health(cls):
            return json_encode({'status': Client.STATUS.value})


Client = EurekaClient()

def main():
    tornado.ioloop.IOLoop.current().run_sync(Client.all)

if __name__ == '__main__':
    def f():
        return Client.remove()
    ret = tornado.ioloop.IOLoop.current().run_sync(f)

