# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
################################################################################

from odoo import models, fields, api


class SaleTaxReportPdf(models.AbstractModel):
    _name = 'report.aspl_sale_tax_report_ee.report_tax_by_state_temp'
    _description = "Report Sale Tax by State"

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'aspl_sale_tax_report_ee.report_tax_by_state_temp')
        return {
            'doc_ids': self.env['sale.tax.report'].browse(data['ids']),
            'doc_model': report.model,
            'docs': self,
            'data': data,
            'get_data': self.get_data,
        }

    def get_data(self, obj):
        if not obj.tax_ids:
            tax_ids = [tax.id for tax in self.env['account.tax'].search([('type_tax_use', '=', 'sale')])]
        else:
            tax_ids = [tax.id for tax in obj.tax_ids]
        if not obj.state_ids:
            state_ids = [state.id for state in self.env['res.country.state'].search([])]
        else:
            state_ids = [state.id for state in obj.state_ids]

        SQL = """SELECT am.id AS move_id,am.name AS invoice, am.invoice_date,t.name AS tax,t.id AS tax_id,t.amount AS tax_rate,
                    aml.price_subtotal,rp.name AS partner,
                    am.partner_shipping_id as city,
                    rp.state_id AS state,
                    (CASE WHEN am.move_type IN ('out_refund', 'in_refund') THEN -1 ELSE 1 END) * SUM(aml.price_subtotal) AS product_sales,
                    (CASE WHEN am.move_type IN ('out_refund', 'in_refund') THEN -1 ELSE 1 END) * SUM((aml.price_subtotal * t.amount) / 100) AS total_tax,
                    (CASE WHEN am.move_type IN ('out_refund', 'in_refund') THEN -1 ELSE 1 END) * SUM(aml.price_subtotal + ((aml.price_subtotal * t.amount) / 100)) AS total_invoice
                    FROM account_move_line AS aml
                    JOIN account_move_line_account_tax_rel r ON (aml.id = r.account_move_line_id)
                    JOIN account_tax t ON (r.account_tax_id = t.id)
                    JOIN account_move am ON (am.id = aml.move_id)
                    JOIN res_partner rp ON (rp.id = am.partner_id)
                    WHERE rp.state_id in %s
                    AND am.invoice_date <= '%s'
                    AND am.invoice_date >= '%s'
                    AND am.move_type in ('out_invoice','out_refund')
                    AND t.id in %s
                    GROUP BY am.id,t.id,r.account_tax_id,t.name,am.name, am.invoice_date,aml.price_subtotal,
                    am.move_type,rp.name,rp,state_id,am.partner_shipping_id,t.amount""" % (" (%s) " % ','.join(map(str, state_ids)),str(obj.to_date), str(obj.from_date),
                                                                            " (%s) " % ','.join(map(str, tax_ids)))

        without_tax_ids = [tax.id for tax in self.env['account.tax'].search([])]
        SQL_1 = """SELECT am.id AS move_id,am.name AS invoice, am.invoice_date,aml.price_subtotal,rp.name AS partner,am.partner_shipping_id as city,
			        rp.state_id AS state,
		            (CASE WHEN am.move_type IN ('out_refund', 'in_refund') THEN -1 ELSE 1 END) * SUM(aml.price_subtotal) AS product_sales,
		            (CASE WHEN am.move_type IN ('out_refund', 'in_refund') THEN -1 ELSE 1 END) * SUM(aml.price_subtotal) AS total_invoice
		            FROM account_move_line AS aml
                    JOIN account_move am ON (am.id = aml.move_id)
                    JOIN res_partner rp ON (rp.id = am.partner_id)
                    WHERE rp.state_id in %s
                    AND am.move_type in ('out_invoice','out_refund')
                    AND am.invoice_date <= '%s'
                    AND am.invoice_date >= '%s'
                    AND aml.product_id IS NOT NULL
                    AND aml.id NOT IN (SELECT r.account_move_line_id
                                        FROM account_move_line_account_tax_rel r 
                                        JOIN account_tax t ON (r.account_tax_id = t.id)
                                        WHERE aml.id = r.account_move_line_id
                                        AND t.id in %s)
                    GROUP BY am.id,am.name, am.invoice_date,aml.price_subtotal,
                    am.move_type,rp.name,rp,state_id,am.partner_shipping_id""" % (" (%s) " % ','.join(map(str, state_ids)),str(obj.to_date), str(obj.from_date),
                                                                   " (%s) " % ','.join(map(str, without_tax_ids)))

        self._cr.execute(SQL)
        tax_details = self._cr.dictfetchall()

        self._cr.execute(SQL_1)
        tax_not_details = self._cr.dictfetchall()

        custom_tax_detail = []
        for each_tax in tax_details:
            if each_tax.get('move_id') not in [x.get('move_id') for x in custom_tax_detail]:
                custom_tax_detail.append(each_tax)
            else:
                count = 0
                for custom_tax in custom_tax_detail:
                    if custom_tax.get('move_id') == each_tax.get('move_id') and custom_tax.get(
                            'tax_id') == each_tax.get('tax_id'):
                        custom_tax.update(
                            {'product_sales': custom_tax.get('product_sales') + each_tax.get('product_sales'),
                             'total_tax': custom_tax.get('total_tax') + each_tax.get('total_tax'),
                             'total_invoice': custom_tax.get('total_invoice') + each_tax.get('total_invoice')})
                        count = count + 1

                if count == 0:
                    custom_tax_detail.append(each_tax)

        custom_without_tax_detail = []
        for each_without_tax in tax_not_details:
            if each_without_tax.get('move_id') not in [x.get('move_id') for x in custom_without_tax_detail]:
                custom_without_tax_detail.append(each_without_tax)
            else:
                count = 0
                for custom_without_tax in custom_without_tax_detail:
                    if custom_without_tax.get('move_id') == each_without_tax.get('move_id'):
                        custom_without_tax.update(
                            {'product_sales': custom_without_tax.get('product_sales') + each_without_tax.get('product_sales'),
                             'total_invoice': custom_without_tax.get('total_invoice') + each_without_tax.get('total_invoice')})
                        count = count + 1

                if count == 0:
                    custom_without_tax_detail.append(each_without_tax)

        custom_tax_detail.extend(custom_without_tax_detail)

        final_dict={}
        for key in custom_tax_detail:
            if key['state'] not in final_dict:
                final_dict.update({key['state']: [key]})
            else:
                final_dict[key['state']] += [key]

        for key,value in final_dict.items():
            dic={}
            na_list=[]
            for k in value:
                if k.get('tax_id',False):
                    if k['tax_id'] not in dic:
                        dic.update({k['tax_id']: [k]})
                    else:
                        dic[k['tax_id']] += [k]
                else:
                    na_list.append(k)
                    dic.update({'NA':na_list})
            final_dict.update({key:dic})

        return final_dict

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
