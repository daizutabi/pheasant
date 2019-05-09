from typing import List

import responder

# from pheasant.utils.cache import collect

api = responder.API()
paths: List[str] = []


# class GetPages:
#     def on_get(self, req, resp):
#         pages = collect()
#         resp.media = {"status": True, "todos": todos}
#
#
# api.add_route("/pages", GetList)
