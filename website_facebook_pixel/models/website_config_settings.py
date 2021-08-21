# -*- coding: utf-8 -*-

from openerp import api, fields, models


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    facebook_pixel_key = fields.Char(related='website_id.facebook_pixel_key')
