import responder

from pheasant.core.page import Pages
from pheasant.core.pheasant import Pheasant


class App:
    def __init__(self, paths, ext):
        self.api = responder.API()
        self.store = {}
        self.store["pages"] = Pages(paths, ext)
        self.store["pages"].collect()
        self.api.add_route("/pages", self.pages)
        self.api.add_route("/pages/{id}", self.page)

    def run(self, port=8000):
        self.api.run(port=port)

    def pages(self, req, resp):
        self.store["pages"].collect()
        resp.media = {"success": True, **self.store["pages"].to_dict()}

    async def page(self, req, resp, *, id):
        page = self.store["pages"][int(id) - 1]
        if req.method == "get":
            resp.media = {"success": True, "id": id, "page": page.to_dict()}
            return
        elif req.method == "delete":
            page.cache.delete()
            resp.media = {"success": True, "id": id, "page": page.to_dict()}
        elif req.method == "put":
            converter = Pheasant(verbose=2)
            converter.jupyter.safe = True
            converter.convert(page.path)

    # data = await req.media()
