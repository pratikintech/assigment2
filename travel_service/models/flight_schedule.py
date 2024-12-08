from odoo import api, fields, models, _


class FlightSchedule(models.Model):
    _name = 'flight.schedule'
    _description = 'Flight Schedule'

    flight_id = fields.Many2one('flight.registry', string='Flight', required=True)
    flight_name = fields.Char("Flight name", related="flight_id.flight_name")
    airline_code = fields.Char("Airline code", related="flight_id.airline_code")
    departure_date_time = fields.Datetime(string='Departure Date Time', required=True)
    arrival_date_time = fields.Datetime(string='Arrival Date Time', required=True)
    flight_duration = fields.Float(string='Flight Duration (Hours)', compute="_compute_flight_duration", store=True)
    frequency = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], string='Frequency', help='Days of the week the flight operates')
    origin_airport_id = fields.Many2one('booking.location', string='Origin Airport Location')
    destination_airport_id = fields.Many2one('booking.location', string='Destination Airport Location')
    stopover_airport_ids = fields.Many2many('booking.location', string='Via/Stopover Airports')
    seating_capacity = fields.Integer(string='Seating Capacity')
    status = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ], string='Flight Status', default='scheduled')
    is_available = fields.Boolean(string='Available', compute="_compute_is_available", store=True)

    @api.model
    def name_get(self):
        result = []
        for record in self:
            name = f"(origin location: {record.origin_airport_id},(origin location: {record.destination_airport_id}  )"
            result.append((record.id, name))
        return result

    @api.depends('departure_date_time', 'arrival_date_time', 'status', 'origin_airport_id', 'destination_airport_id')
    def _compute_is_available(self):
        for record in self:
            record.is_available = (record.status == 'scheduled'
                                   and record.departure_date_time > fields.Datetime.now()
                                   and record.origin_airport_id
                                   and record.destination_airport_id)

    @api.depends('departure_date_time', 'arrival_date_time')
    def _compute_flight_duration(self):
        for record in self:
            if record.arrival_date_time and record.departure_date_time:
                duration = record.arrival_date_time - record.departure_date_time
                record.flight_duration = duration.total_seconds() / 3600
            else:
                record.flight_duration = 0.0
