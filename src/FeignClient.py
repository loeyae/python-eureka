import functools
import EurekaClient
import random

if len(EurekaClient.Client.application) < 1:
    EurekaClient.main()


def feign_client(name, url):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if EurekaClient.Client.application.get(name):
                _url = get_url_from_instance(EurekaClient.Client.application.get(name))
            else:
                _url = url
            if not _url:
                raise TypeError
            func.__dict__['url'] = _url
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_url_from_instance(application):
    instance = application['instance']
    if isinstance(instance, list):
        if len(instance) == 1:
            current = instance[0]
        else:
            current = load_balance(instance)

        return current['homePageUrl'] if current['homePageUrl'] else build_url(current)
    raise TypeError


def load_balance(instance):
    return random.choice(instance)


def build_url(instance):
    if instance['securePort']['@enabled'] == 'true':
        return 'https://' + instance['ipAddr'] + ':' + instance['securePort']['$'] + '/'
    else:
        return 'http://' + instance['ipAddr'] + ':' + instance['port']['$'] + '/'


@feign_client(name='test', url='aaa')
def f(a, b):
    print(config)


if __name__ == '__main__':
    f(1, 2)
