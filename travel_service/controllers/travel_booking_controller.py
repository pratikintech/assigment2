from odoo import http
from odoo.http import request

class TravelBookingController(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        flights = request.env['flight.registry'].sudo().search([], limit=6)
        return request.render('website.homepage', {
            'flights': flights
        })
