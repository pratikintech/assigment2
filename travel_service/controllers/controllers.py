# -*- coding: utf-8 -*-
# from odoo import http


# class TravelService(http.Controller):
#     @http.route('/travel_service/travel_service', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/travel_service/travel_service/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('travel_service.listing', {
#             'root': '/travel_service/travel_service',
#             'objects': http.request.env['travel_service.travel_service'].search([]),
#         })

#     @http.route('/travel_service/travel_service/objects/<model("travel_service.travel_service"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('travel_service.object', {
#             'object': obj
#         })
