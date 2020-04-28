import socket


class Config(object):
    SERVER_PORT = 8888
    SERVER_NAME = 'python-demo'
    HOST_NAME = socket.gethostname()
    IP_ADDRESS = socket.gethostbyname(HOST_NAME)
    HTTPS = False

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def get_eureka_uri(self):
        eureka_uri = ('https' if self.HTTPS else 'http') + '://'
        eureka_uri += self.EUREKA_HOST + ':' + str(self.EUREKA_PORT) + '/eureka/'
        return eureka_uri

    def get_uri(self):
        return 'http://' + self.IP_ADDRESS + ':' + str(self.SERVER_PORT) + '/'


class LocalConfig(Config):
    EUREKA_HOST = 'localhost'
    EUREKA_PORT = '9900'
    EUREKA_USER = 'admin'
    EUREKA_PWD = 'ad2020min'


class TestConfig(Config):
    EUREKA_HOST = '192.168.1.220'
    EUREKA_PORT = '9900'
    EUREKA_USER = 'admin'
    EUREKA_PWD = 'ad2020min'


mapping = {
    'local': LocalConfig,
    'test': TestConfig,
    'default': LocalConfig
}

import sys
import os

env = 'default'
num = len(sys.argv) - 1
if num >= 1:
    env = sys.argv[1]

APP_ENV = os.environ.get('APP_ENV', env).lower()
config = mapping[APP_ENV]()

if __name__ == '__main___':
    print(config)