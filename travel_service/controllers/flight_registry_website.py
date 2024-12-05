# from odoo import http
# from odoo.http import request
#
# class FlightWebsite(http.Controller):
#
#     # Route to display the list of flights
#     @http.route('/flights', auth='public', website=True)
#     def flight_list(self):
#         flights = request.env['flight.registry'].sudo().search([])  # Fetch all flights
#         return request.render('travel_service.flight_list_template', {
#             'flights': flights
#         })
#
#
