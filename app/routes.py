from aiohttp import web

from views import UsersView, AdvertisementsView

routes_list = [
    web.post('/register/', UsersView),
    web.get('/get-token/', UsersView),
    web.post('/advertisements/', AdvertisementsView),
    web.get('/advertisements/{adv_id:\d+}/', AdvertisementsView),
    web.get('/advertisements/', AdvertisementsView),
    web.delete('/advertisements/{adv_id:\d+}/', AdvertisementsView),
    web.patch('/advertisements/{adv_id:\d+}/', AdvertisementsView)
]
