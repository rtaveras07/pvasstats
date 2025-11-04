# -*- coding: utf-8 -*-
from odoo import models, fields, tools

class PvasStudentStats(models.Model):
    _name = 'pvas.student.stats'
    _description = 'Estadísticas de Asignaturas Calificadas por Estudiante'
    _auto = False
    _table = 'pvas_student_stats'

    student_id = fields.Many2one('pvas.students', string='Estudiante', readonly=True)
    course_id = fields.Many2one('pvas.courses', string='Curso', readonly=True)
    total_subjects_competences = fields.Integer(
        string='Asignaturas con Competencias Calificadas', 
        readonly=True,
        help="Número de asignaturas con al menos una competencia calificada (> 0)"
    )
    total_subjects_ra = fields.Integer(
        string='Asignaturas con RAs Calificados', 
        readonly=True,
        help="Número de asignaturas con al menos un Resultado de Aprendizaje calificado (> 0)"
    )
    total_subjects_graded = fields.Integer(
        string='Total Asignaturas Calificadas', 
        readonly=True,
        help="Número total de asignaturas con cualquier tipo de calificación (> 0)"
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS
            SELECT
                ROW_NUMBER() OVER (ORDER BY g.students_ids, g.courses_ids) AS id,
                g.students_ids AS student_id,
                g.courses_ids AS course_id,
                COUNT(DISTINCT CASE WHEN (
                    COALESCE(g.cp1,0) > 0 OR COALESCE(g.cp2,0) > 0 OR COALESCE(g.cp3,0) > 0 OR COALESCE(g.cp4,0) > 0 OR
                    COALESCE(g.pp1,0) > 0 OR COALESCE(g.pp2,0) > 0 OR COALESCE(g.pp3,0) > 0 OR COALESCE(g.pp4,0) > 0 OR
                    COALESCE(g.ctp1,0) > 0 OR COALESCE(g.ctp2,0) > 0 OR COALESCE(g.ctp3,0) > 0 OR COALESCE(g.ctp4,0) > 0 OR
                    COALESCE(g.ecp1,0) > 0 OR COALESCE(g.ecp2,0) > 0 OR COALESCE(g.ecp3,0) > 0 OR COALESCE(g.ecp4,0) > 0
                ) THEN g.classes_ids END) AS total_subjects_competences,
                COUNT(DISTINCT CASE WHEN (
                    COALESCE(g.ra1,0) > 0 OR COALESCE(g.ra2,0) > 0 OR COALESCE(g.ra3,0) > 0 OR COALESCE(g.ra4,0) > 0 OR
                    COALESCE(g.ra5,0) > 0 OR COALESCE(g.ra6,0) > 0 OR COALESCE(g.ra7,0) > 0 OR COALESCE(g.ra8,0) > 0 OR
                    COALESCE(g.ra9,0) > 0 OR COALESCE(g.ra10,0) > 0 OR COALESCE(g.ra11,0) > 0 OR COALESCE(g.ra12,0) > 0 OR
                    COALESCE(g.ra13,0) > 0 OR COALESCE(g.ra14,0) > 0 OR COALESCE(g.ra15,0) > 0
                ) THEN g.classes_ids END) AS total_subjects_ra,
                COUNT(DISTINCT CASE WHEN (
                    COALESCE(g.cp1,0) > 0 OR COALESCE(g.cp2,0) > 0 OR COALESCE(g.cp3,0) > 0 OR COALESCE(g.cp4,0) > 0 OR
                    COALESCE(g.pp1,0) > 0 OR COALESCE(g.pp2,0) > 0 OR COALESCE(g.pp3,0) > 0 OR COALESCE(g.pp4,0) > 0 OR
                    COALESCE(g.ctp1,0) > 0 OR COALESCE(g.ctp2,0) > 0 OR COALESCE(g.ctp3,0) > 0 OR COALESCE(g.ctp4,0) > 0 OR
                    COALESCE(g.ecp1,0) > 0 OR COALESCE(g.ecp2,0) > 0 OR COALESCE(g.ecp3,0) > 0 OR COALESCE(g.ecp4,0) > 0 OR
                    COALESCE(g.ra1,0) > 0 OR COALESCE(g.ra2,0) > 0 OR COALESCE(g.ra3,0) > 0 OR COALESCE(g.ra4,0) > 0 OR
                    COALESCE(g.ra5,0) > 0 OR COALESCE(g.ra6,0) > 0 OR COALESCE(g.ra7,0) > 0 OR COALESCE(g.ra8,0) > 0 OR
                    COALESCE(g.ra9,0) > 0 OR COALESCE(g.ra10,0) > 0 OR COALESCE(g.ra11,0) > 0 OR COALESCE(g.ra12,0) > 0 OR
                    COALESCE(g.ra13,0) > 0 OR COALESCE(g.ra14,0) > 0 OR COALESCE(g.ra15,0) > 0
                ) THEN g.classes_ids END) AS total_subjects_graded
            FROM pvas_grades g
            WHERE g.students_ids IS NOT NULL
            GROUP BY g.students_ids, g.courses_ids
        """)