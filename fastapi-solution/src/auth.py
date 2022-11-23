from fastapi import Cookie
import requests

URL_SERVISE_AUTH = 'http://192.168.14.88:4242//api/v1/users/verify_token'

def token_verification(func):
    def wrapper(access_token_cookie = Cookie(), refresh_token_cookie = Cookie()):
        cookies  = dict(access_token_cookie = access_token_cookie,
                        refresh_token_cookie = refresh_token_cookie)
        resp = requests.get(URL_SERVISE_AUTH, cookies=cookies)
        if not resp.json():
            return {'error':'Token expired'}
        return func()
    return wrapper