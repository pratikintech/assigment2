from odoo import api, fields, models, _


class FlightRegistry(models.Model):
    _name = "flight.registry"
    _description = "Flight Registry"

    flight_no = fields.Integer(string="FLIGHT NO", required=True)
    airline_code = fields.Char(string="Airline code", required=True)
    flight_name = fields.Char(string="flight name", required=True)
    description = fields.Text(string="description")
    flight_schedule_ids = fields.One2many('flight.schedule', 'flight_id', string='Flight Schedules')

    def name_get(self):
        result = []
        for record in self:
            # Customize the name display format
            name = f"[{record.airline_code}] {record.flight_name} (Flight No: {record.flight_no})"
            result.append((record.id, name))
        return result