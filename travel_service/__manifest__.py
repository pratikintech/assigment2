# -*- coding: utf-8 -*-
{
    'name': "travel_service",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """ Long description of module's purpose""",
    'sequence':-500,
    'author': "Paresh Prajapati",
    'website': "https://www.paresh.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','product','account','website'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/flight_registry.xml',
        'views/flight_schedule.xml',
        'views/flight_booking.xml',
        'views/hotel_registry.xml',
        'views/hotel_room.xml',
        'views/hotel_booking.xml',
        'views/booking_record.xml',
        'views/booking_location.xml',
        'views/home_page.xml',
        'views/flight_booking_website_template.xml',
    ],

    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
