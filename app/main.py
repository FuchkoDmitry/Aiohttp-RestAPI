from aiohttp import web

from app.routes import routes_list
from init_db import init_orm

app = web.Application()
app.router.add_routes(routes_list)
app.cleanup_ctx.append(init_orm)
web.run_app(app)