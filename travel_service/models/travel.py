from odoo import api, fields, models, _
from datetime import date


class TravelService(models.Model):
    _name = "travel.ser"
    _description = "Travel Service"

    name = fields.Char(string="name", required=True)
