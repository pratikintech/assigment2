# from odoo import http
# from odoo.http import request
#
# class WebsiteHomepage(http.Controller):
#     @http.route('/', type='http', auth='public', website=True)
#     def homepage(self, **kwargs):
#         return request.render('travel_service.home_template', {})
#
# class FlightWebsite(http.Controller):
#
#     @http.route('/flights', auth='public', website=True)
#     def flight_list(self):
#         flights = request.env['flight.registry'].sudo().search([])
#         return request.render('travel_service.flight_list_template', {
#             'flights': flights
#         })
#     # Route to display the flight registration form
#     @http.route('/flights/register', auth='public', website=True)
#     def flight_register_form(self):
#         return request.render('travel_service.flight_register_template')
#
#     # Route to handle form submission
#     @http.route('/flights/register/submit', auth='public', methods=['POST'], website=True,csrf=False)
#     def flight_register_submit(self, **kwargs):
#         # Create a new flight record using submitted data
#         request.env['flight.registry'].sudo().create({
#             'flight_no': kwargs.get('flight_no'),
#             'airline_code': kwargs.get('airline_code'),
#             'flight_name': kwargs.get('flight_name'),
#             'description': kwargs.get('description'),
#         })
#         return request.redirect('/flights')  # Redirect back to flight list
#
#     @http.route('/flights/<int:flight_id>', auth='public', website=True)
#     def flight_detail(self, flight_id):
#         flight = request.env['flight.registry'].sudo().browse(flight_id)
#         return request.render('travel_service.flight_detail_template', {
#             'flight': flight
#         })
