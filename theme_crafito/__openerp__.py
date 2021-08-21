# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

{
    'name': 'Theme Crafito',
    'summary': 'Advanced Responsive Theme with A Range of Custom Snippets',
    'description': '''Theme Crafito
Business theme
Hardware theme
Hardware and tools theme
Single Page theme
Digital security theme
Event theme
Medical equipments theme
Crafito Theme
Odoo Crafito Theme
Crafito theme for Odoo
odoo custom theme
customizable odoo theme
odoo multipurpose theme
odoo 11 theme
multipurpose theme
odoo multipurpose theme
odoo responsive theme
responsive theme
odoo theme
odoo themes
ecommerce theme
odoo ecommerce themes
odoo website themes
odoo bootstrap themes
bootstrap themes
bootstrap theme
customize odoo theme
ecommerce store theme
theme for business
theme for ecommerce store
''',
    'category': 'Theme/Ecommerce',
    'version': '9.0.1.1.6',
    'author': 'AppJetty',
    'website': 'https://www.appjetty.com/',
    'depends': [
        'website_hr',
        'mass_mailing',
        'website_sale',
        'website_blog',
        'website_event_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/views.xml',
        'views/website_view.xml',
        'views/slider_views.xml',
        'views/snippets.xml',
        'views/theme_customize.xml',
        'views/theme.xml',
    ],
    'demo': [
        'demo/demo_homepage.xml',
    ],
    'support': 'support@appjetty.com',
    'live_test_url': 'http://theme-crafito.appjetty.com/',
    'images': [
        'static/description/splash-screen.png',
        'static/description/splash-screen_screenshot.png'
    ],
    'application': True,
    'price': 155.00,
    'currency': 'EUR',
}
