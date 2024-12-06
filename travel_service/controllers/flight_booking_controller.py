from odoo import http
from odoo.http import request

class FlightBookingController(http.Controller):
    @http.route('/flight/booking', type='http', auth='public', website=True)
    def flight_booking_page(self):
        flight_registry = request.env['flight.registry'].sudo().search([])
        return request.render('travel_service.flight_booking_website_template', {'flight_registry': flight_registry})

    @http.route('/flight/booking', type='http', auth='user', website=True, methods=['POST'],csrf=False)
    def create_flight_booking(self, **post):
        try:
            # Validate and create flight booking
            booking_vals = {
                'flight_id': int(post.get('flight_id')),
                'class_of_travel': post.get('class_of_travel'),
                'num_traveler': int(post.get('num_traveler', 1)),
                'customer_id': request.env.user.partner_id.id,
            }
            print("bookings_vals: ",booking_vals)
            # Create booking
            booking = request.env['flight.booking'].sudo().create(booking_vals)
            booking.action_confirm_booking()

            return request.render('travel_service.flight_booking_success', {
                'booking': booking
            })
        except Exception as e:
            return request.render('travel_service.booking_error_template', {
                'error': str(e)
            })