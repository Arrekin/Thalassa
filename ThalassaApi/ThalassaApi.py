from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor, threads

import cgi
import json

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

    def render_GET(self, request):
        return b'<html><body>You are on the main page</body></html>'


class WorldDispatcher(ThalassaTwistedResource):
    
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

    def render_GET(self, request):
        threads.deferToThread(self.__gather_full_world_data, request=request)
        return NOT_DONE_YET

    def __gather_full_world_data(self, request):
        """ Return data required to display world view. """
        try:
            self.logger.info("WORLD data request")
            try:
                db_session = factory.CreateDatabaseSession()
                player = factory.Create(players.ExternalPlayer)
                player.authenticate(db_session, session_hash=request.getCookie(b'session_hash'))
                if not player.is_authenticated():
                    request.setResponseCode(401)
                    request.finish()
                    return

                world_islands, world_fleets = player.get_full_world_data(db_session)
                full_data = {**world_islands.to_jsonready_dict(), **world_fleets.to_jsonready_dict()}
            except:
                # db_session.rollback() there is nothing to rollback
                raise
            finally:
                db_session.close()
            request.write(bytes(json.dumps(full_data), "utf-8"))
            request.finish()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            request.setResponseCode(500)
            request.finish()
        self.logger.info("-> OK")


class WorldCommandMoveFleet(ThalassaTwistedResource):
    isLeaf = True

    def render_POST(self, request):
        threads.deferToThread(self.__move_fleet, request=request)
        return NOT_DONE_YET

    def __move_fleet(self, request):
        """ Create new journey for the fleet. """
        try:
            self.logger.info("WORLD move fleet command!")
            try:
                db_session = factory.CreateDatabaseSession()
                player = factory.Create(players.ExternalPlayer)
                player.authenticate(db_session, session_hash=request.getCookie(b'session_hash'))
                if not player.is_authenticated():
                    request.setResponseCode(401)
                    request.finish()
                    return

                fleet_id = int(cgi.escape(str(request.args[b"fleet_id"][0], 'utf-8')))
                target_x = int(cgi.escape(str(request.args[b"x"][0], 'utf-8')))
                target_y = int(cgi.escape(str(request.args[b"y"][0], 'utf-8')))
                player.move_fleet_command(db_session, fleet_id=fleet_id, target_x=target_x, target_y=target_y)
                db_session.commit()
            except:
                db_session.rollback()
                raise
            finally:
                db_session.close()
            request.setResponseCode(204)
            request.finish()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            request.setResponseCode(500)
            request.finish()
        self.logger.info("-> OK")


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
        try:
            username = cgi.escape(str(request.args[b"username"][0], 'utf-8'))
            password = cgi.escape(str(request.args[b"password"][0], 'utf-8'))
            self.logger.info("LOGIN request; User: {}, Password: {}".format(username, password))

            # TODO: Generate proper session hash and store it in redis
            try:
                db_session = factory.CreateDatabaseSession()
                new_player = factory.Create(players.ExternalPlayer)
                new_player.authenticate(db_session, username=username, password=password)
                self.logger.debug("Is user authenticated: " + str(new_player.is_authenticated()))
            except:
                # db_session.rollback() # there is nothing to rollback
                raise
            finally:
                db_session.close()
            if new_player.session_hash is None:
                return self.render_GET(request)

            request.addCookie(b'session_hash', new_player.session_hash)
            request.redirect(b'world')
            request.finish()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            request.setResponseCode(500)
            request.finish()


#resource = File('/tmp')
root = MainPageDispatcher()
world = WorldDispatcher()
root.putChild(b'world', world)
world.putChild(b'data', WorldData())
world.putChild(b'cmd_move_fleet', WorldCommandMoveFleet())
root.putChild(b'login', Login())
root.putChild(b'static', File('/opt/thalassa/ThalassaApi/static'))
twisted_factory = Site(root)
reactor.listenTCP(8888, twisted_factory)
reactor.run()