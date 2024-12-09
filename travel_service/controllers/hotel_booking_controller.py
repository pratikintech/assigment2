from datetime import datetime
import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError

# Logger initialization
class HotelBookingController(http.Controller):
    _logger = logging.getLogger(__name__)

    @http.route('/hotel/booking', type='http', auth='public', website=True)
    def hotel_booking_page(self):
        try:
            # Fetch the list of available hotels
            hotels = request.env['hotel.registry'].sudo().search([])

            # Fetch distinct room types for the booking (hardcoded room types in this case)
            room_types = ['single', 'double', 'suite']
            self._logger.info("Fetched Hotels: %s", hotels)
            self._logger.info("Fetched Room Types: %s", room_types)

            return request.render('travel_service.hotel_booking_website_template', {
                'hotels': hotels,
                'room_types': room_types,  # Add room types to the template context
            })
        except Exception as e:
            self._logger.exception("Error fetching hotel data: %s", str(e))
            return request.render('travel_service.hotel_booking_error_template', {'error': str(e)})

    @http.route('/hotel/booking/submit', type='http', auth="public", methods=["POST"], website=True)
    def submit_booking(self, **post ):
        print(post)
        try:
            customer_name = post.get('customer_id')  # Assuming the field holds the customer name
            if not customer_name:
                raise UserError("Customer name is required.")

            # Fetch the customer record by name
            customer = request.env['res.partner'].sudo().search([('name', '=', customer_name)], limit=1)
            if not customer:
                raise UserError(f"Customer with name '{customer_name}' not found.")

            hotel_id = post.get("hotel_id")
            if not hotel_id:
                raise UserError("Hotel ID is required.")

            hotel = request.env['hotel.registry'].sudo().browse(int(hotel_id))
            if not hotel or not hotel.exists():
                raise UserError(f"Hotel with ID '{hotel_id}' not found.")

            # Extract the hotel name
            hotel_name = hotel.hotel_name  # Adjust if the field name differs
            print(f"Hotel Name: {hotel_name}")


            booking = request.env['hotel.booking'].sudo().create({
                'customer_id': customer.id,
                'hotel_id': post.get('hotel_id'),
                'hotel_name':hotel_name,
                'check_in_date': post.get('check_in_date'),
                'check_out_date': post.get('check_out_date'),
                'num_rooms': post.get('num_rooms'),
                'num_guests': post.get('num_guests'),
                'room_type': post.get('room_type'),
            })


            # Log booking creation
            self._logger.info("Booking created successfully: %s", booking.id)

            return request.render("travel_service.hotel_booking_success", {
                'booking': booking,
                'hotel_name': hotel_name
            })


        except UserError as e:
            self._logger.error("Error processing booking submission: %s", e.name)
            return request.render('travel_service.hotel_booking_error_template', {'error': e.name})
        except Exception as e:
            self._logger.exception("Error processing booking submission: %s", str(e))
            return request.render('travel_service.hotel_booking_error_template', {'error': str(e)})

    def calculate_booking_cost(self, booking):
        """
        Calculate the total cost for the booking based on room cost and number of days.
        """
        try:
            # Ensure the hotel_id is correctly linked to the hotel model
            hotel = booking.hotel_id  # booking.hotel_id should reference hotel.registry
            if not hotel:
                raise UserError("No hotel selected for booking.")

            # Fetch the price per night from the hotel registry
            price_per_night = hotel.price_per_night
            if not price_per_night:
                raise UserError("Room cost per night is not set for the selected hotel.")

            # Validate dates
            check_in_date = booking.check_in_date
            check_out_date = booking.check_out_date
            if not check_in_date or not check_out_date:
                raise UserError("Check-in and check-out dates are required.")
            if check_out_date <= check_in_date:
                raise UserError("Check-out date must be after check-in date.")

            # Calculate the number of days
            num_days = (check_out_date - check_in_date).days

            # Validate the number of rooms
            num_rooms = booking.num_rooms
            if not num_rooms or num_rooms <= 0:
                raise UserError("Number of rooms must be greater than zero.")

            # Calculate the total cost
            total_cost = price_per_night * num_days * num_rooms
            self._logger.info("Calculated total cost: %s", total_cost)

            return total_cost

        except UserError as e:
            self._logger.error("UserError in cost calculation: %s", e.name)
            raise
        except Exception as e:
            self._logger.exception("Unexpected error in cost calculation: %s", str(e))
            raise
    @http.route('/hotel/my_bookings', type='http', auth='user', website=True)
    def my_hotel_bookings(self,**kwargs):
        print("in my hotel booking")
        user_id = request.env.user.partner_id.id
        print("user id: ",user_id)
        search_query = kwargs.get('search_query', '')

        # Fetch bookings for the logged-in user
        domain = [('customer_id', '=', user_id)]

        # If there is a search query, filter bookings by flight name
        if search_query:
            domain.append(('hotel_id.hotel_name', 'ilike', '%' + search_query + '%'))

        bookings = request.env['hotel.booking'].sudo().search(domain)
        for field_name in bookings._fields:
            print("field_name: ", field_name)
        for booking in bookings:
            print("booking: ",booking)
            print("booking.invoice_id: ",booking.invoice_id)
            booking.invoice_id = booking.invoice_id

        return request.render('travel_service.hotel_booking_details_template', {
            'bookings': bookings,
            'search_query': search_query,
        })
    @http.route('/hotel/my_bookings/<int:hotel_id>', type='http', auth='public', website=True)
    def booking_details(self, hotel_id):
        print("in my hotel booking")
        try:
            user_id = request.env.user.partner_id.id
            booking = request.env['hotel.booking'].sudo().browse(hotel_id)
            print("booking: ",booking)

            # Check if the booking exists
            if not booking.exists():
                raise UserError(f"Booking with ID '{hotel_id}' not found.")

            # Log fetching booking details
            self._logger.info("Fetched Booking Details: %s", booking)

            return request.render('travel_service.hotel_booking_details_template', {
                'booking': booking,
                'hotel_name': booking.hotel_name,
                'customer_name': booking.customer_id.name,
            })

        except UserError as e:
            self._logger.error("Error fetching booking details: %s", e.name)
            return request.render('travel_service.hotel_booking_error_template', {'error': e.name})
        except Exception as e:
            self._logger.exception("Error fetching booking details: %s", str(e))
            return request.render('travel_service.hotel_booking_error_template', {'error': str(e)})

    @http.route('/hotel/booking/cancel/<int:hotel_id>', type='http', auth='user', website=True)
    def cancel_hotel_booking(self, hotel_id):
        try:
            # Find the booking for the current user
            booking = request.env['hotel.booking'].sudo().search([
                ('id', '=', hotel_id),
                ('customer_id', '=', request.env.user.partner_id.id)
            ], limit=1)

            if not booking:
                return request.render('travel_service.booking_error_template', {
                    'error': "Booking not found or you are not authorized to cancel this booking."
                })

            # Check if booking can be cancelled (e.g., not already cancelled or completed)
            if booking.state in ['draft', 'confirmed']:
                booking.action_cancel_booking()

                # Optional: Add a flash message
                return request.redirect('/hotel/my_bookings?message=Booking%20cancelled%20successfully')
            else:
                return request.render('travel_service.booking_error_template', {
                    'error': "This booking cannot be cancelled at this time."
                })

        except Exception as e:
            return request.render('travel_service.booking_error_template', {
                'error': str(e)
            })