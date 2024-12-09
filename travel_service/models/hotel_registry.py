from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
import re

class HotelRegistry(models.Model):
    _name = 'hotel.registry'
    _description = 'Hotel Registry'

    hotel_code = fields.Char(string='Hotel Code/Identifier', required=True)
    hotel_name = fields.Char(string='Hotel Name', required=True)
    hotel_address = fields.Many2one('res.partner', string='Hotel Address')  # , widget='address'
    contact_number = fields.Char(string='Contact Number')
    email_address = fields.Char(string='Email Address')
    # hotel_rating = fields.Float(string='Hotel Rating')
    hotel_rating = fields.Selection([
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5")
    ], string="Hotel Rating", default="1")
    number_of_rooms = fields.Integer(string='Number of Rooms')
    facilities = fields.Text(string='Facilities/Services', help='e.g., Wi-Fi, Pool, Spa')
    check_in_time = fields.Float(string='Check-in Time')
    check_out_time = fields.Float(string='Check-out Time')
    cancellation_policy = fields.Text(string='Cancellation Policy',
                                      default='Free cancellation up to 24 hours before check-in')
    hotel_room_ids = fields.One2many('hotel.room', 'hotel_id', string='Hotel Rooms')
    price_per_night = fields.Float(string='Price per Night')
    # @api.model
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = f"[{record.hotel_code}] {record.hotel_name} (Hotel Name: {record.hotel_name})"
    #         result.append((record.id, name))
    #     return result

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