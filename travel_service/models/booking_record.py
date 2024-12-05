from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import logging

_logger = logging.getLogger(__name__)


class BookingRecord(models.Model):
    _name = 'booking.record'
    _description = 'Booking Record'

    booking_id = fields.Char(string='Booking ID', required=True, copy=False,
                             default=lambda self: self.env['ir.sequence'].next_by_code('booking.record'))
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    booking_type = fields.Selection([
        ('flight', 'Flight'),
        ('hotel', 'Hotel')
    ], string='Booking Type', required=True)
    service_id = fields.Reference([('flight.registry', 'Flight'), ('hotel.registry', 'Hotel')], string='Flight/Hotel',
                                  required=True, )
    booking_date_time = fields.Datetime(string='Booking Date Time', default=fields.Datetime.now)
    start_date_time = fields.Datetime(string='Travel/Stay Start Date Time')
    end_date_time = fields.Datetime(string='Travel/Stay End Date Time')
    num_travelers = fields.Integer(string='Number of Travelers/Guests')
    total_amount = fields.Float(string='Total Amount')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid')
    ], string='Payment Status', compute='_compute_payment_status', store=True)
    booking_status = fields.Selection([
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled')
    ], string='Booking Status', default='pending')
    special_requests = fields.Text(string='Special Requests')
    cancellation_policy = fields.Text(string='Cancellation Policy',
                                      default='Free cancellation up to 24 hours before the start date')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)
    invoice_status = fields.Char(string='Invoice Status', compute='_compute_invoice_status', store=True)

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.booking_id} - {record.booking_type}"
            result.append((record.id, name))
        return result

    @api.depends('invoice_id', 'invoice_id.payment_state')
    def _compute_invoice_status(self):
        """
        Compute the invoice status based on the associated invoice's payment state
        """
        print("In compute invoice status")

        for record in self:
            print("record.invoice,id: ",record.invoice_id)
            if not record.invoice_id:
                record.invoice_status = 'No Invoice'
            else:
                # Map Odoo's invoice payment states to custom statuses
                payment_state_mapping = {
                    'not_paid': 'Unpaid',
                    'in_payment': 'Partially Paid',
                    'paid': 'Paid',
                    'partial': 'Partially Paid',
                    'reversed': 'Reversed'
                }
                record.invoice_status = payment_state_mapping.get(record.invoice_id.payment_state, 'Unknown')

    @api.depends('invoice_id', 'invoice_id.payment_state')
    def _compute_payment_status(self):
        """
        Compute payment status based on the invoice's payment state
        """
        print("IN compute payment status")
        for record in self:
            _logger.info(f"Invoice: {record.invoice_id}")
            _logger.info(
                f"Invoice Payment State: {record.invoice_id.payment_state if record.invoice_id else 'No Invoice'}")

            if not record.invoice_id:
                record.payment_status = 'unpaid'
            else:
                payment_state_mapping = {
                    'not_paid': 'unpaid',
                    'in_payment': 'partially_paid',
                    'paid': 'paid',
                    'partial': 'partially_paid',
                    'reversed': 'unpaid'
                }
                record.payment_status = payment_state_mapping.get(record.invoice_id.payment_state, 'unpaid')

    def action_create_invoice(self):
        """Create an invoice for the booking."""
        for record in self:
            if not record.customer_id:
                raise ValidationError("Please select a customer before creating an invoice.")

            move_vals = {
                'move_type': 'out_invoice',
                'partner_id': self.customer_id.id,
                'currency_id': self.env.company.currency_id.id,  # Set default currency
                'journal_id': self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Booking: {}'.format(self.customer_id or 'N/A'),
                    'quantity': 1,
                    'price_unit': self.total_amount,
                    'account_id': self.env['account.account'].search([('code', '=', '400000')], limit=1).id,
                })],
            }
            invoice = self.env['account.move'].create(move_vals)

            record.invoice_id = invoice.id

    def action_view_invoice(self):
        """Redirect to the invoice."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }