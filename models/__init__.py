# -*- coding: utf-8 -*-

from . import pvas_progress_stats

def init_models(cr):
    """Initialize database for this module"""
    cr.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name = 'pvas_progress_stats'
    """)
    if not cr.fetchone():
        from odoo import api, SUPERUSER_ID
        env = api.Environment(cr, SUPERUSER_ID, {})
        model = env['pvas.progress.stats']
        model.init()