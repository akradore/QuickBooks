# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Twilio SMS Gateway",
  "summary"              :  "Send sms notifications using twilio gateway.",
  "category"             :  "Marketing",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-SMS-Twilio-Gateway.html",
  "description"          :  """http://webkul.com/blog/odoo-sms-twilio-gateway/""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=twilio_gateway&version=9.0",
  "depends"              :  ['sms_notification'],
  "data"                 :  [
                             'views/twilio_config_view.xml',
                             'views/sms_report.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  20,
  "currency"             :  "EUR",
}