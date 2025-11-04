# -*- coding: utf-8 -*-
from odoo import models, fields, tools

class PvasProgressStats(models.Model):
    _name = 'pvas.progress.stats'
    _description = 'PVAS Grade Progress Statistics'
    _auto = False
    _table = 'pvas_progress_stats'

    professor_id = fields.Many2one('res.users', string='Profesor', readonly=True)
    course_id = fields.Many2one('pvas.courses', string='Curso', readonly=True)
    subject_id = fields.Many2one('pvas.classes', string='Asignatura', readonly=True)
    total_grades = fields.Integer(string='Total Calificaciones', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS
            SELECT
                ROW_NUMBER() OVER (ORDER BY g.teachers_ids, g.courses_ids, g.classes_ids) AS id,
                g.teachers_ids AS professor_id,
                g.courses_ids AS course_id,
                g.classes_ids AS subject_id,
                COUNT(*) AS total_grades
            FROM pvas_grades g
            WHERE
                COALESCE(g.cp1,0) > 0 OR COALESCE(g.cp2,0) > 0 OR COALESCE(g.cp3,0) > 0 OR COALESCE(g.cp4,0) > 0 OR
                COALESCE(g.pp1,0) > 0 OR COALESCE(g.pp2,0) > 0 OR COALESCE(g.pp3,0) > 0 OR COALESCE(g.pp4,0) > 0 OR
                COALESCE(g.ctp1,0) > 0 OR COALESCE(g.ctp2,0) > 0 OR COALESCE(g.ctp3,0) > 0 OR COALESCE(g.ctp4,0) > 0 OR
                COALESCE(g.ecp1,0) > 0 OR COALESCE(g.ecp2,0) > 0 OR COALESCE(g.ecp3,0) > 0 OR COALESCE(g.ecp4,0) > 0 OR
                COALESCE(g.ra1,0) > 0 OR COALESCE(g.ra2,0) > 0 OR COALESCE(g.ra3,0) > 0 OR COALESCE(g.ra4,0) > 0 OR
                COALESCE(g.ra5,0) > 0 OR COALESCE(g.ra6,0) > 0 OR COALESCE(g.ra7,0) > 0 OR COALESCE(g.ra8,0) > 0 OR
                COALESCE(g.ra9,0) > 0 OR COALESCE(g.ra10,0) > 0 OR COALESCE(g.ra11,0) > 0 OR COALESCE(g.ra12,0) > 0 OR
                COALESCE(g.ra13,0) > 0 OR COALESCE(g.ra14,0) > 0 OR COALESCE(g.ra15,0) > 0
            GROUP BY g.teachers_ids, g.courses_ids, g.classes_ids
        """)
