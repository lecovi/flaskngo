#!/usr/bin/env python
# Standard Lib imports
import os
# Third-party imports
# BITSON imports
from app import create_app
from app.extensions import celery
# from app.reports.functions import (update_members_amd,
#                                    update_members_by_category,
#                                    update_members_by_debt,
#                                    update_members_fee_debt,
#                                    update_members_without_debt,
#                                    update_today_cashed,
#                                    update_total_members)

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()