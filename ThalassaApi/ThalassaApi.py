from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor

import cgi

import thalassa.logging as logging
import thalassa.factory as factory
import thalassa.player as player

class MainPageDispatcher(Resource):

    def getChild(self, name, request):
        if name == b'':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        return b'<html><body>You are on the main page</body></html>'


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

class Login(Resource):
    isLeaf = True

    def render_GET(self, request):
        with open("/opt/thalassa/ThalassaApi/html/login.html", 'rb') as file_stream:
            data = file_stream.read()
        request.setHeader(b"content-type", b"text/html")
        return data

    def render_POST(self, request):
        print(request.args)
        if b"username" not in request.args or b"password" not in request.args:
            return self.render_GET(request)

        username = cgi.escape(str(request.args[b"username"][0]))
        password = cgi.escape(str(request.args[b"password"][0]))

        logger = logging.get_logger("thalassa_api")
        logger.info("Received logging request; User: {}, Password: {}".format(username, password))

        # TODO: Generate proper session hash and store it in redis
        new_player = factory.Create(player.ExternalPlayer)
        logger.debug("Is user authenticated: " + str(new_player.is_authenticated()))
        new_player.authenticate(username=username, password=password)
        logger.debug("Is user authenticated: " + str(new_player.is_authenticated()))
        session_hash = "MAKeiTGEnerAtedlaTER"
        request.args[b"session_hash"] = session_hash

        return WorldDispatcher().render_GET(request)


#resource = File('/tmp')
root = MainPageDispatcher()
root.putChild(b'world', WorldDispatcher())
root.putChild(b'login', Login())
twisted_factory = Site(root)
reactor.listenTCP(8888, twisted_factory)
reactor.run()