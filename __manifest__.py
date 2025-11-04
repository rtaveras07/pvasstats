{
    'name': 'PVAS Progress Statistics',
    'version': '17.0.1.0.0',
    'category': 'Education',
    'summary': 'Statistics for grade placement progress in PVAS',
    'description': """
        This module provides statistical analysis and visualization for grade placement progress in PVAS.
        Features include:
        - Progress tracking by professor
        - Course-wise grade placement analysis
        - Subject-wise statistics
        - Graphical representation of progress
    """,
    'author': 'Custom',
    'depends': ['pvas'],
    'data': [
        # SOLO archivos XML - ORDEN CRÍTICO
        'views/report_wizard_views.xml',  # 1. Define la acción PRIMERO
        'views/pvas_progress_views.xml',  # 2. Otras vistas
        'views/pvas_progress_menu.xml',   # 3. Menú principal
        
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}