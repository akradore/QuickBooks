from openerp import models,api
from urlparse import urlparse
import base64
import requests

request_header = {
                "Accept-Language":"en-US,en;q=0.8",
                "User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
                "Connection":"keep-alive",
                }
class Import(models.TransientModel):

    _inherit = 'base_import.import'
    

    def _convert_import_data(self, record, fields, options, context=None):
        data, import_fields = super(Import,self)._convert_import_data(record, fields, options, context)
        all_fields = self.pool[record.res_model].fields_get(record._cr,record._uid)
        for name, field in all_fields.iteritems():
            if field['type'] in ('binary') and name in import_fields:
                index = import_fields.index(name)
                for i,line in enumerate(data):
                    if not line[index]:
                        continue
                    parsed_url = urlparse(line[index])
                    if parsed_url.scheme:
                        try:
                            content = base64.b64encode(requests.get(line[index],headers=request_header).content)
                        except Exception,e:
                            content = ''
                            pass
                        lst = list(line)
                        lst[index] = content
                        data[i] = tuple(lst)
        return data, import_fields                

    