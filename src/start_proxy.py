from mitmproxy.tools._main import mitmweb,mitmdump

if __name__ == '__main__':
    #mitmweb(args=['-s', './http_proxy.py', '-p', '18321', '--web-port', '18323'])
    mitmdump(args=['-s', './http_proxy.py', '-p', '18321'])

