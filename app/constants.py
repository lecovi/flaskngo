# -*- coding:utf-8 -*-
"""
    constants
    ~~~~~~~~~

    Domi constants file
"""
# Standard Lib imports
from datetime import datetime
# Third-party imports
# BITSON imports

BITSON_DATE = datetime.strptime('15032014', "%d%m%Y").date()

SUBDIVISIONS = {'objects': [
                {'id': 0, 'description': 'Ciudad Autónoma de Buenos Aires'},
                {'id': 1, 'description': 'Buenos Aires'},
                {'id': 2, 'description': 'Catamarca'},
                {'id': 3, 'description': 'Córdoba'},
                {'id': 4, 'description': 'Corrientes'},
                {'id': 5, 'description': 'Entre Ríos'},
                {'id': 6, 'description': 'Jujuy'},
                {'id': 7, 'description': 'Mendoza'},
                {'id': 8, 'description': 'La Rioja'},
                {'id': 9, 'description': 'Salta'},
                {'id': 10, 'description': 'San Juan'},
                {'id': 11, 'description': 'San Luis'},
                {'id': 12, 'description': 'Santa Fe'},
                {'id': 13, 'description': 'Santiago del Estero'},
                {'id': 14, 'description': 'Tucumán'},
                {'id': 15, 'description': 'Chaco'},
                {'id': 17, 'description': 'Chubut'},
                {'id': 18, 'description': 'Formosa'},
                {'id': 19, 'description': 'Misiones'},
                {'id': 20, 'description': 'Neuquén'},
                {'id': 21, 'description': 'La Pampa'},
                {'id': 22, 'description': 'Río Negro'},
                {'id': 23, 'description': 'Santa Cruz'},
                {'id': 24, 'description': 'Tierra del Fuego'}
                ]
}
