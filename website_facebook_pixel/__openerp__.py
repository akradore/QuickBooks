# -*- coding: utf-8 -*-
# Copyright (C) 2019 Yurii Razumovskyi <GarazdCreation@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Website Facebook Pixel',
    'version': '9.0.1.0.1',
    'category': 'Website',
    'author': 'Garazd Creation',
    'website': "https://garazd.biz",
    'license': 'LGPL-3',
    'summary': """
        Module adds Facebook Pixel to website pages.
    """,
    'description': 'Adds Facebook Pixel to website pages.',
    'images': ['static/description/banner.png'],
    'depends': [
        'website',
    ],
    'data': [
        'views/website_templates.xml',
        'views/website_config_settings.xml',
    ],
    'price': 15.0,
    'currency': 'EUR',
    'support': 'support@garazd.biz',
    'application': False,
    'installable': True,
    'auto_install': False,
}
