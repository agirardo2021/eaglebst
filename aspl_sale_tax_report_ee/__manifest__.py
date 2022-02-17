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

{
    'name': 'Sale Tax Report (Enterprise)',
    'category': 'Account',
    'version': '1.0.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'summary': 'This module allows you to generate Sale Tax Report(PDF) base on entered dates, taxes and states.',
    'description': '''This module allows you to generate Sale Tax Report(PDF) base on entered dates, taxes and states.''',
    'price': 35.00,
    'currency': 'EUR',
    'depends': ['base', 'sale_management', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_tax_wiz_view.xml',
        'report/report.xml',
        'report/report_tax_by_state_temp_view.xml'
    ],
    'images': ['static/description/state_wise_tax_report.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
