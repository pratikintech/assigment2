from odoo import http
from odoo.http import request

class FlightBookingController(http.Controller):
    @http.route('/flight/booking', type='http', auth='public', website=True)
    def flight_booking_page(self, **kwargs):
        flight_registry = request.env['flight.registry'].sudo().search([])

        # Fetch the departure and destination locations for the dropdown
        departure_locations = request.env['booking.location'].sudo().search([])
        destination_locations = request.env['booking.location'].sudo().search([])

        return request.render('travel_service.flight_booking_website_template', {
            'flight_registry': flight_registry,
            'departure_locations': departure_locations,
            'destination_locations': destination_locations,
        })

    @http.route('/flight/available', type='http', auth='public', website=True, methods=['GET'], csrf=False)
    def search_flights(self, **kwargs):
        print("In search_flights")
        departure_location = kwargs.get('departure_location')
        arrival_location = kwargs.get('arrival_location')

        if departure_location:
            departure_location = int(departure_location)
        else:
            departure_location = None

        if arrival_location:
            arrival_location = int(arrival_location)
        else:
            arrival_location = None

        # Debug information
        print(f"Departure Location ID: {departure_location}")
        print(f"Arrival Location ID: {arrival_location}")

        flight_schedules = request.env['flight.schedule'].sudo().search([
            ('origin_airport_id', '=', departure_location),
            ('destination_airport_id', '=', arrival_location),
            ('is_available', '=', True)
        ])

        # Fetch the departure and destination locations for the dropdown
        departure_locations = request.env['booking.location'].sudo().search([])
        destination_locations = request.env['booking.location'].sudo().search([])

        return request.render('travel_service.available_flight_template', {
            'flight_schedules': flight_schedules,
            'departure_locations': departure_locations,
            'destination_locations': destination_locations,
        })

    @http.route('/flight/booking', type='http', auth='user', website=True, methods=['POST'],csrf=False)
    def create_flight_booking(self, **post):
        try:
            # Print all received POST data for debugging
            print("Received POST data:", post)

            # Explicit type conversion with error checking
            try:
                departure_location = int(post.get('departure_location', False))
                arrival_location = int(post.get('arrival_location', False))
                flight_id = int(post.get('flight_id', False))
                num_travelers = int(post.get('num_traveler', 1))
                class_of_travel = post.get('class_of_travel', 'economy')
            except (ValueError, TypeError) as conv_error:
                print("Conversion Error:", conv_error)
                return request.render('travel_service.booking_error_template', {
                    'error': f"Invalid input: {conv_error}. Please ensure all fields are correctly filled."
                })

            # Validate that converted values are not False
            if not all([departure_location, arrival_location, flight_id]):
                return request.render('travel_service.booking_error_template', {
                    'error': "Missing required booking parameters. Please fill in all fields."
                })

            # Search for matching flight schedule
            flight_schedule = request.env['flight.schedule'].sudo().search([
                ('origin_airport_id', '=', departure_location),
                ('destination_airport_id', '=', arrival_location),
                ('flight_id', '=', flight_id)
            ], limit=1)


            # If no matching flight schedule is found
            if not flight_schedule:
                return request.render('travel_service.booking_error_template', {
                    'error': "No matching flight schedule found for the selected route."
                })

            # Prepare booking values
            booking_vals = {
                'flight_id': flight_id,
                'class_of_travel': class_of_travel,
                'num_traveler': num_travelers,
                'customer_id': request.env.user.partner_id.id,
            }

            # Print booking values for debugging
            print("Booking Values:", booking_vals)

            # Create booking
            booking = request.env['flight.booking'].sudo().create(booking_vals)

            # Confirm booking if method exists
            if hasattr(booking, 'action_confirm_booking'):
                booking.action_confirm_booking()

            return request.render('travel_service.flight_booking_success', {
                'booking': booking
            })

        except Exception as e:
            # Log the full error for server-side debugging
            import traceback
            traceback.print_exc()

            # Render error template with specific error message
            return request.render('travel_service.booking_error_template', {
                'error': str(e)
            })

    @http.route('/flight/my_bookings', type='http', auth='user', website=True)
    def my_flight_bookings(self,**kwargs):
        print("in my flight booking")
        user_id = request.env.user.partner_id.id
        search_query = kwargs.get('search_query', '')

        # Fetch bookings for the logged-in user
        domain = [('customer_id', '=', user_id)]

        # If there is a search query, filter bookings by flight name
        if search_query:
            domain.append(('flight_id.flight_name', 'ilike', '%' + search_query + '%'))

        bookings = request.env['flight.booking'].sudo().search(domain)
        # for field_name in bookings._fields:
        #     print("field_name: ", field_name)
        for booking in bookings:
            # print("booking: ",booking)
            # print("booking.invoice_id: ",booking.invoice_id)
            booking.invoice_id = booking.invoice_id

        return request.render('travel_service.my_flight_bookings_template', {
            'bookings': bookings,
            'search_query': search_query,
        })

    @http.route('/flight/booking/detail/<int:booking_id>', type='http', auth='user', website=True)
    def flight_booking_detail(self, booking_id):
        # Fetch the booking record based on the provided ID
        booking = request.env['flight.booking'].sudo().browse(booking_id)

        if not booking.exists() or booking.customer_id.id != request.env.user.partner_id.id:
            # If the booking does not exist or does not belong to the user, return a 404
            return request.not_found()

        return request.render('travel_service.flight_booking_success', {
            'booking': booking
        })

    @http.route('/flight/booking/cancel/<int:booking_id>', type='http', auth='user', website=True)
    def cancel_flight_booking(self, booking_id):
        try:
            # Find the booking for the current user
            booking = request.env['flight.booking'].sudo().search([
                ('id', '=', booking_id),
                ('customer_id', '=', request.env.user.partner_id.id)
            ],limit=1)
            print("bookgin: ",booking)
            print("booking.state: ",booking.state)



            if not booking:
                return request.render('travel_service.booking_error_template', {
                    'error': "Booking not found or you are not authorized to cancel this booking."
                })

            # Check if booking can be cancelled (e.g., not already cancelled or completed)
            if booking.state in ['draft', 'confirmed']:
                print("this booking has bookign state draft or confo")
                booking.action_cancel_booking()

                # Optional: Add a flash message
                return request.redirect('/flight/my_bookings?message=Booking%20cancelled%20successfully')
            else:
                return request.render('travel_service.booking_error_template', {
                    'error': "This booking cannot be cancelled at this time."
                })

        except Exception as e:
            return request.render('travel_service.booking_error_template', {
                'error': str(e)
            })

