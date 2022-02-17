# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning, UserError


class SaleTaxReport(models.TransientModel):
    _name = 'sale.tax.report'
    _description = "Sale Tax Report"

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    tax_ids = fields.Many2many("account.tax", string="Taxes",domain="[('type_tax_use', '=', 'sale')]")
    state_ids = fields.Many2many('res.country.state', string='States')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id,
                                 required=True)

    @api.onchange('to_date')
    def validate_date(self):
        if self.from_date > self.to_date:
            raise UserError(_("To Date Must Be Greater Than From Date"))

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data = {'ids': self.ids,
                'model': 'sale.tax.report',
                'form': data
                }
        return self.env.ref('aspl_sale_tax_report_ee.action_report_tax_by_state').report_action(self, data=data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
