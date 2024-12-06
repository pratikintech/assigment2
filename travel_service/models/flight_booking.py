from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

class FlightBooking(models.Model):
    _name = 'flight.booking'
    _description = 'Flight Booking'

    flight_id = fields.Many2one('flight.registry', string="Flight", required=True)
    flight_number = fields.Integer(related='flight_id.flight_no', string="Flight Number", store=True)
    flight_name = fields.Char(related='flight_id.flight_name', string="Flight name", store=True)

    departure_airport_code = fields.Char(related='flight_id.airline_code', string="Airline code", store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)
    class_of_travel = fields.Selection([
        ('economy', 'Economy'),
        ('business', 'Business')
    ], string='Class of Travel', required=True)
    num_traveler = fields.Integer(string="Num of traveler", default=1)
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)
    baggage_allowance = fields.Char(string='Baggage Allowance')
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.flight_name or 'N/A'} - {record.customer_id}"
            result.append((record.id, name))
        return result

    @api.depends('class_of_travel', 'num_traveler')
    def _compute_total_cost(self):
        for record in self:
            if record.num_traveler <= 0:
                record.total_cost = 0.0
                continue

            if record.class_of_travel == 'economy':
                record.total_cost = record.num_traveler * 1000
            elif record.class_of_travel == 'business':
                record.total_cost = record.num_traveler * 2500
            else:
                record.total_cost = 0.0

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
                        'name': f'Flight Booking: {record.flight_name} - {record.class_of_travel}',
                        'quantity': record.num_traveler,
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

    def get_invoice_details(self):
        """
        Retrieve detailed invoice information for display
        """
        self.ensure_one()
        if not self.invoice_id:
            return {}

        return {
            'invoice_number': self.invoice_id.name,
            'invoice_date': self.invoice_id.invoice_date,
            'total_amount': self.invoice_id.amount_total,
            'invoice_lines': [
                {
                    'name': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                } for line in self.invoice_id.invoice_line_ids
            ]
        }
