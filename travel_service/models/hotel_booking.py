from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HotelBooking(models.Model):
    _name = 'hotel.booking'
    _description = 'Hotel Booking'

    booking_id = fields.Many2one('booking.record', string='Booking', required=True,domain="[('booking_type', '=', 'hotel')]")
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    hotel_id = fields.Many2one('hotel.registry', string='Hotel id')
    hotel_name = fields.Char(
        string='Hotel Name',
        compute='_compute_hotel_name',
        store=True
    )
    room_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite')
    ], string='Room Type', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)
    num_rooms = fields.Integer(string='Number of Rooms')
    room_cost = fields.Float(string='Room Cost', compute='_compute_room_cost', store=True)
    num_days = fields.Integer(string='Number of Days')
    guest_names = fields.Text(string='Guest Names', help='Comma-separated names for multiple guests')
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)

    @api.model
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.booking_id}] {record.hotel_name} (Hotel Name: {record.hotel_name})"
            result.append((record.id, name))
        return result

    @api.depends('room_type')
    def _compute_room_cost(self):
        """Compute room cost based on room type."""
        cost_mapping = {
            'single': 100,
            'double': 150,
            'suite': 250,
        }
        for record in self:
            record.room_cost = cost_mapping.get(record.room_type, 0)

    @api.depends('num_rooms', 'num_days', 'room_cost')
    def _compute_total_cost(self):
        """Compute the total cost of the booking."""
        for record in self:
            if record.num_rooms > 0 and record.num_days > 0:
                record.total_cost = record.num_rooms * record.num_days * record.room_cost
            else:
                record.total_cost = 0

    def action_confirm_booking(self):
        """Confirm the booking and create an invoice."""
        for record in self:
            if not record.invoice_id:
                if not record.customer_id:
                    raise ValidationError("Please select a customer before confirming the booking.")
                invoice_vals = {
                    'move_type': 'out_invoice',
                    'partner_id': record.customer_id.id,
                    'invoice_line_ids': [(0, 0, {
                        'name': f'Hotel Booking: {record.hotel_id.hotel_name} - {record.room_type}',
                        'quantity': 1,
                        'price_unit': record.total_cost,
                    })],
                }
                invoice = self.env['account.move'].create(invoice_vals)
                record.invoice_id = invoice.id
            record.state = 'confirmed'

    def action_cancel_booking(self):
        """Cancel the booking."""
        for record in self:
            record.state = 'cancelled'

    def action_view_invoice(self):
        """Redirect to the invoice."""
        self.ensure_one()
        if not self.invoice_id:
            raise ValidationError("No invoice found for this booking.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    @api.depends('booking_id', 'booking_id.service_id')
    def _compute_hotel_name(self):
        for record in self:
            if record.booking_id and record.booking_id.service_id:
                # Explicitly check if the service_id is a hotel.registry record
                if record.booking_id.service_id._name == 'hotel.registry':
                    record.hotel_name = record.booking_id.service_id.hotel_name
                else:
                    record.hotel_name = False
            else:
                record.hotel_name = False
