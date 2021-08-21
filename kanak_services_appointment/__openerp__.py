# -*- coding: utf-8 -*-
# Copyright (C) Kanak Infosystems LLP.

{
    'name': 'Kanak Service Appointment',
    'version': '1.0',
    'summary': 'This module is used for bookinng services which inturn is related to a user who provides the service',
    'description': """
Kanak Service Appointment
================================
    """,
    'license': 'Other proprietary',
    'author': 'Kanak Infosystems LLP.',
    'images': ['static/description/banner.jpg'],
    'category': 'website',
    'depends': ['website', 'mail', 'calendar', 'website_sale', 'portal_sale'],
    'data': [
        'data/appointment_data.xml',
        'views/res_partner.xml',
        'views/calendar_view.xml',
        'views/appointment_template.xml',
        'views/calendar_asset.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
    ],
    'installable': True,
    'application': True,
    'price': 149,
    'currency': 'EUR',
    'live_test_url': 'http://52.77.80.196:8069/?db=Apt_services',
}
