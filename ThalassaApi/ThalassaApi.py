from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor

class MainPageDispatcher(Resource):
    isLeaf = True
    def __init__(self):
        super().__init__()

    def render_GET(self, request):
        with open("/opt/Thalassa/html/login.html", 'rb') as file_stream:
            data = file_stream.read()
        request.setHeader(b"content-type", b"text/html")
        return data

#resource = File('/tmp')
root = MainPageDispatcher()
factory = Site(root)
reactor.listenTCP(8888, factory)
reactor.run()