from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor

class MainPageDispatcher(Resource):

    def getChild(self, name, request):
        if name == b'':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        with open("/opt/thalassa/ThalassaApi/html/login.html", 'rb') as file_stream:
            data = file_stream.read()
        request.setHeader(b"content-type", b"text/html")
        return data

class WorldDispatcher(Resource):
    isLeaf = True

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)
    
    def render_GET(self, request):
        with open("/opt/thalassa/ThalassaApi/html/world.html", 'rb') as file_stream:
            data = file_stream.read()
        request.setHeader(b"content-type", b"text/html")
        return data

#resource = File('/tmp')
root = MainPageDispatcher()
root.putChild(b'world', WorldDispatcher())
factory = Site(root)
reactor.listenTCP(8888, factory)
reactor.run()