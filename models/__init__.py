# -*- coding: utf-8 -*-

from . import pvas_progress_stats,report_wizard ,pvas_student_stats
 

def init_models(cr):
    """Initialize database for this module"""
    # Verificar y crear vista de progreso de profesores
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
    
    # Verificar y crear vista de estadísticas de estudiantes
    cr.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name = 'pvas_student_stats'
    """)
    if not cr.fetchone():
        from odoo import api, SUPERUSER_ID
        env = api.Environment(cr, SUPERUSER_ID, {})
        model = env['pvas.student.stats']
        model.init()