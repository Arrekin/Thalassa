from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor

import cgi

import thalassa.logging as logging
import thalassa.factory as factory
import thalassa.player as player


class ThalassaTwistedResource(Resource):

    def __init__(self):
        super().__init__()
        self.logger = logging.get_logger("thalassa_api")

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)


class MainPageDispatcher(ThalassaTwistedResource):

    def getChild(self, name, request):
        if name == b'':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        return b'<html><body>You are on the main page</body></html>'


class WorldDispatcher(ThalassaTwistedResource):

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)
    
    def render_GET(self, request):
        self.logger.info("WORLD base page request")
        with open("/opt/thalassa/ThalassaApi/html/world.html", 'rb') as file_stream:
            data = file_stream.read()
        request.setHeader(b"content-type", b"text/html")
        return data


class WorldData(ThalassaTwistedResource):
    isLeaf = True

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)
    
    def render_GET(self, request):
        self.logger.info("WORLD data request")
        return b'you requested world data!'

class Login(ThalassaTwistedResource):
    isLeaf = True

    def render_GET(self, request):
        self.logger.info("LOGIN page request")
        with open("/opt/thalassa/ThalassaApi/html/login.html", 'rb') as file_stream:
            data = file_stream.read()
        request.setHeader(b"content-type", b"text/html")
        return data

    def render_POST(self, request):
        if b"username" not in request.args or b"password" not in request.args:
            return self.render_GET(request)

        username = cgi.escape(str(request.args[b"username"][0], 'utf-8'))
        password = cgi.escape(str(request.args[b"password"][0], 'utf-8'))
        self.logger.info("LOGIN request; User: {}, Password: {}".format(username, password))

        # TODO: Generate proper session hash and store it in redis
        new_player = factory.Create(player.ExternalPlayer)
        self.logger.debug("Is user authenticated: " + str(new_player.is_authenticated()))
        new_player.authenticate(username=username, password=password)
        self.logger.debug("Is user authenticated: " + str(new_player.is_authenticated()))
        if new_player.session_hash is None:
            return self.render_GET(request)

        request.args[b"session_hash"] = new_player.session_hash

        return WorldDispatcher().render_GET(request)


#resource = File('/tmp')
root = MainPageDispatcher()
world = WorldDispatcher()
root.putChild(b'world', world)
world.putChild(b'data', WorldData())
root.putChild(b'login', Login())
root.putChild(b'static', File('/opt/thalassa/ThalassaApi/static'))
twisted_factory = Site(root)
reactor.listenTCP(8888, twisted_factory)
reactor.run()