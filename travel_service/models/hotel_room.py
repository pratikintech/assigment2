from odoo import models, fields

class HotelRoom(models.Model):
    _name = 'hotel.room'
    _description = 'Hotel Room'

    name = fields.Char(string='Room Name', required=True)
    room_type = fields.Selection([
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('suite', 'Suite')
    ], string='Room Type', required=True)
    description = fields.Text(string='Description')
    max_capacity = fields.Integer(string='Max Capacity')
    bed_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('queen', 'Queen'),
        ('king', 'King')
    ], string='Bed Type')
    feature_ids = fields.Many2many('product.product', string='Features', help='e.g., Wi-Fi, TV, AC, Mini-bar')
    price_per_night = fields.Float(string='Price Per Night', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    floor_number = fields.Integer(string='Floor Number')
    hotel_id = fields.Many2one('hotel.registry', string='Hotel id')
    room_size = fields.Float(string='Room Size (sq ft)')
    smoking_allowed = fields.Boolean(string='Smoking Allowed', default=False)
    special_notes = fields.Text(string='Special Notes')
