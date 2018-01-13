from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor, threads

import cgi

import thalassa.logging as logging
import thalassa.factory as factory
import thalassa.players as players


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
        session_hash = request.getCookie(b'session_hash')
        if session_hash is None:
            self.logger.info("-> Session hash not found. Redirected to login page")
            request.redirect(b'login')
            request.finish()
            return NOT_DONE_YET
        self.logger.debug("-> Session Hash: "+str(session_hash, 'utf-8'))
        with open("/opt/thalassa/ThalassaApi/html/world.html", 'rb') as file_stream:
            data = file_stream.read()
        request.setHeader(b"content-type", b"text/html")
        self.logger.info("-> OK")
        return data


class WorldData(ThalassaTwistedResource):
    isLeaf = True

    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)
    
    def render_GET(self, request):
        self.logger.info("WORLD data request")
        threads.deferToThread(self.__gather_full_world_data, request=request)
        return NOT_DONE_YET

    def __gather_full_world_data(self, request):
        """ Return data required to display world view. """
        self.logger.info("WORLD data request")
        player = factory.Create(players.ExternalPlayer)
        player.authenticate(session_hash=request.getCookie(b'session_hash'))
        if not player.is_authenticated():
            request.setResponseCode(401)
            request.finish()
            return
        request.write(bytes(player.get_full_world_data().to_json(), "utf-8"))
        request.finish()

class Login(ThalassaTwistedResource):
    isLeaf = True

    def render_GET(self, request):
        self.logger.info("LOGIN page request")
        with open("/opt/thalassa/ThalassaApi/html/login.html", 'rb') as file_stream:
            data = file_stream.read()
        request.setHeader(b"content-type", b"text/html")
        self.logger.info("-> OK")
        return data

    def render_POST(self, request):
        if b"username" not in request.args or b"password" not in request.args:
            return self.render_GET(request)

        threads.deferToThread(self.__authenticate_user, request=request)
        return NOT_DONE_YET


    def __authenticate_user(self, request):

        username = cgi.escape(str(request.args[b"username"][0], 'utf-8'))
        password = cgi.escape(str(request.args[b"password"][0], 'utf-8'))
        self.logger.info("LOGIN request; User: {}, Password: {}".format(username, password))

        # TODO: Generate proper session hash and store it in redis
        new_player = factory.Create(players.ExternalPlayer)
        self.logger.debug("Is user authenticated: " + str(new_player.is_authenticated()))
        new_player.authenticate(username=username, password=password)
        self.logger.debug("Is user authenticated: " + str(new_player.is_authenticated()))
        if new_player.session_hash is None:
            return self.render_GET(request)

        request.addCookie(b'session_hash', new_player.session_hash)
        request.redirect(b'world')
        request.finish()


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