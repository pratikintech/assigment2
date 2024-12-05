from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import re


class BookingLocation(models.Model):
    _name = 'booking.location'
    _description = 'Booking Location'

    name = fields.Char(string='Location Name', required=True, help='e.g., City name, Airport name, Hotel name')
    location_type = fields.Selection([
        ('city', 'City'),
        ('airport', 'Airport'),
        ('hotel', 'Hotel')
    ], string='Location Type', required=True)
    address_id = fields.Many2one('res.partner', string='Address')
    latitude = fields.Float(string='Latitude', digits=(10, 6))
    longitude = fields.Float(string='Longitude', digits=(10, 6))
    time_zone = fields.Char(string='Time Zone', default=lambda self: self.env.user.tz, help='e.g., GMT+5:30')
    contact_number = fields.Char(string='Contact Number')
    email_address = fields.Char(string='Email Address')
    description = fields.Text(string='Description')
    accessibility_details = fields.Text(string='Accessibility Details', help='e.g., public transport, nearby landmarks')

    @api.constrains('contact_number')
    def _check_phone_number(self):
        for rec in self:
            if rec.contact_number and not re.match(r'^\+?\d{7,15}$', rec.contact_number):
                raise ValidationError("Please enter valid phone no")

    @api.constrains('email_address')
    def _check_email_number(self):
        for rec in self:
            if rec.email_address and '@' not in rec.email_address:
                raise UserError(_('Please Enter Correct Email'))
