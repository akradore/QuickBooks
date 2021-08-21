{
    'name': 'Import Image from URL',
    'description': """Import any Odoo model image field using URL.
    """,
    'author': 'Nilesh Sheliya',
    'category': 'Extra Tools',
    "price": 20.00,
    "live_test_url": "https://odoo.sheliyainfotech.com/contactus?description=demo:import_all_image_from_url&odoo_version=9.0",
    "currency": "EUR",
    'website':'',
    'depends': ['base_import'],
    'external_dependencies': {'python': ['urlparse']},
    "images": ["static/description/import_img_demo.png"],

    'data':[
            ],
    'application': True,
    'license': 'OPL-1',
    'version': '9.0.1.0',
}
