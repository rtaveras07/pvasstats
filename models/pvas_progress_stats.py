# -*- coding: utf-8 -*-
from odoo import models, fields, tools

class PvasProgressStats(models.Model):
    _name = 'pvas.progress.stats'
    _description = 'PVAS Grade Progress Statistics'
    _auto = False
    _table = 'pvas_progress_stats'

    professor_id = fields.Many2one('res.users', string='Professor', readonly=True)
    course_id = fields.Many2one('pvas.courses', string='Course', readonly=True)
    subject_id = fields.Many2one('pvas.classes', string='Subject', readonly=True)
    total_grades = fields.Integer(string='Total Grades', readonly=True)

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
        GROUP BY g.teachers_ids, g.courses_ids, g.classes_ids
    """)

