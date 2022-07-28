from aiohttp import web

from app.views import UsersView

routes_list = [web.post('/register/', UsersView),
               web.get('/get-token/', UsersView)]
