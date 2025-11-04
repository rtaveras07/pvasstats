# -*- coding: utf-8 -*-
from odoo import models, fields, api
from statistics import mean

class StudentReportWizard(models.TransientModel):
    _name = 'pvas.student_report_wizard'
    _description = 'Wizard para reporte de estudiantes por curso'

    course_id = fields.Many2one('pvas.courses', string='Curso', required=True)
    student_id = fields.Many2one('pvas.students', string='Estudiante (Opcional)')  
    subject_id = fields.Many2one('pvas.classes', string='Asignatura (Opcional)')

    report_type = fields.Selection([
        ('detailed', 'Reporte Detallado'),
        ('summary', 'Reporte Resumido'),
    ], string='Tipo de Reporte', default='detailed', required=True)

    detailed_results = fields.Html(string='Resultados Detallados', compute='_compute_results')
    summary_results = fields.Html(string='Resultados Resumidos', compute='_compute_results')

    # -------------------------------------------------------------
    # ONCHANGE: filtra estudiantes y asignaturas dinámicamente
    # -------------------------------------------------------------
    @api.onchange('course_id')
    def _onchange_course_id(self):
        self.subject_id = False
        self.student_id = False
        if not self.course_id:
            return {}
        return {
            'domain': {
                'student_id': [('courses_ids', '=', self.course_id.id)],
                'subject_id': [('id', 'in', self._get_subjects_from_grades(self.course_id.id))]
            }
        }

    def _get_subjects_from_grades(self, course_id):
        """Obtiene las asignaturas que tienen calificaciones en este curso."""
        grades = self.env['pvas.grades'].search([('courses_ids', '=', course_id)])
        return list(set(grades.mapped('classes_ids.id')))

    # -------------------------------------------------------------
    # COMPUTE: Genera contenido según tipo de reporte
    # -------------------------------------------------------------
    @api.depends('course_id', 'subject_id', 'student_id', 'report_type')
    def _compute_results(self):
        for wizard in self:
            if not wizard.course_id:
                msg = '<p>Seleccione un curso para ver los resultados</p>'
                wizard.detailed_results = msg
                wizard.summary_results = msg
                continue

            if wizard.report_type == 'detailed':
                wizard.detailed_results = wizard._get_detailed_results()
                wizard.summary_results = False
            else:
                wizard.summary_results = wizard._get_summary_results()
                wizard.detailed_results = False

    # -------------------------------------------------------------
    # DETALLADO: vista extendida por estudiante
    # -------------------------------------------------------------
    def _get_detailed_results(self):
        students = self._get_students()
        if not students:
            return '<p>No hay estudiantes para el curso seleccionado</p>'

        html = self._get_table_styles()

        for student in students:
            html += f"""
            <div class="student-header">
                📊 Reporte para: {student.nombre or ''} {student.lastname or ''} - Curso: {self.course_id.name}
            </div>
            """
            html += self._get_student_detailed_report(student)

        return html

    def _get_student_detailed_report(self, student):
        domain = [
            ('courses_ids', '=', self.course_id.id),
            ('students_ids', '=', student.id)
        ]
        if self.subject_id:
            domain.append(('classes_ids', '=', self.subject_id.id))

        grades = self.env['pvas.grades'].search(domain)
        if not grades:
            return f'<p>No hay calificaciones para {student.nombre} {student.lastname}</p>'

        general, technical = {}, {}
        for g in grades:
            subject = g.classes_ids
            (technical if subject.classtype == 'T' else general).setdefault(subject.id, {
                'name': subject.name, 'grades': []
            })['grades'].append(g)

        html = ""
        html += self._render_general_subjects(general)
        html += self._render_technical_modules(technical)

        if not general and not technical:
            html += '<p>No hay calificaciones registradas para este estudiante</p>'

        html += "<hr style='margin: 30px 0; border: 1px dashed #ccc;'>"
        return html

    # -------------------------------------------------------------
    # TABLAS DE ASIGNATURAS GENERALES Y MÓDULOS TÉCNICOS
    # -------------------------------------------------------------
    def _render_general_subjects(self, subjects):
        if not subjects:
            return ""
        html = """
        <div class="section-header">ASIGNATURAS GENERALES - COMPETENCIAS FUNDAMENTALES</div>
        <table class="report-table">
            <thead>
                <tr>
                    <th rowspan="2">#</th><th rowspan="2">Asignaturas</th>
                    <th colspan="4">Comunicativa</th>
                    <th colspan="4">Pensamiento Lógico</th>
                    <th colspan="4">Ética Ciudadana</th>
                    <th colspan="4">Científica / Tecnológica</th>
                    <th colspan="4">Promedio Competencias</th>
                    <th rowspan="2">Cal.Final</th>
                    <th rowspan="2">Profesor</th>
                </tr>
                <tr>
                    """ + ''.join(f"<th>P{i}</th>" for i in range(1, 5)) * 5 + "</tr></thead><tbody>"
        for idx, (sid, sub) in enumerate(sorted(subjects.items()), 1):
            g = sub['grades'][0]
            html += f"""
            <tr>
                <td>{idx}</td>
                <td class="subject-name">{sub['name']}</td>
            """
            for fieldset in [['cp1','cp2','cp3','cp4'], ['pp1','pp2','pp3','pp4'],
                             ['ecp1','ecp2','ecp3','ecp4'], ['ctp1','ctp2','ctp3','ctp4']]:
                html += ''.join(f"<td>{getattr(g, f, '') or ''}</td>" for f in fieldset)
            html += ''.join("<td></td>" for _ in range(4))  # PC1-PC4 placeholder
            html += f"<td>{g.promediogral or ''}</td></tr>"
            html += f"<td>{g.teachers_ids.name or ''}</td></tr>"
        html += "</tbody></table>"
        return html

    def _render_technical_modules(self, modules):
        if not modules:
            return ""
        html = """
        <div class="section-header">MÓDULOS TÉCNICOS - RESULTADOS DE APRENDIZAJE</div>
        <table class="report-table">
            <thead>
                <tr>
                    <th>#</th><th>Resultados de Aprendizaje</th>
                    """ + ''.join(f"<th>RA{i}</th>" for i in range(1, 15)) + "<th>Cal.Final</th></tr></thead><tbody>"
        for idx, (mid, mod) in enumerate(sorted(modules.items()), 1):
            g = mod['grades'][0]
            html += f"""
            <tr>
                <td>{idx}</td>
                <td class="subject-name">{mod['name']}</td>
            """
            html += ''.join(f"<td>{getattr(g, f'ra{i}', '') or ''}</td>" for i in range(1, 15))
            html += f"<td>{g.promedio or ''}</td></tr>"
            html += f"<td>{g.teachers_ids.name or ''}</td></tr>"
        html += "</tbody></table>"
        return html

    # -------------------------------------------------------------
    # RESUMEN GENERAL
    # -------------------------------------------------------------
    def _get_summary_results(self):
        students = self._get_students()
        if not students:
            return '<p>No hay estudiantes para el curso seleccionado</p>'

        html = f"""
        <div style="background-color: #f8f9fa; padding: 15px; margin-bottom: 15px; border-radius: 5px;">
            <h3 style="margin: 0 0 10px 0;">Reporte Resumido - {self.course_id.name}</h3>
            <p><strong>Total Estudiantes:</strong> {len(students)}</p>
        </div>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background-color: #e9ecef;">
                    <th>Estudiante</th><th>Asignaturas</th><th>Promedio General</th><th>Estatus</th>
                </tr>
            </thead><tbody>
        """
        for s in students:
            grades = self.env['pvas.grades'].search([
                ('students_ids', '=', s.id),
                ('courses_ids', '=', self.course_id.id)
            ])
            promedios = [g.promediogral for g in grades if g.promediogral]
            promedio = mean(promedios) if promedios else 0
            estado = self._estado(promedio)
            html += f"""
            <tr>
                <td>{s.nombre or ''} {s.lastname or ''}</td>
                <td>{len(set(grades.mapped('classes_ids.id')))}</td>
                <td><b>{promedio:.2f}</b></td>
                <td>{estado}</td>
            </tr>
            """
        html += "</tbody></table>"
        return html

    # -------------------------------------------------------------
    # AUXILIARES
    # -------------------------------------------------------------
    def _get_students(self):
        if self.student_id:
            return self.student_id
        grades = self.env['pvas.grades'].search([('courses_ids', '=', self.course_id.id)])
        return self.env['pvas.students'].browse(list(set(grades.mapped('students_ids.id'))))

    def _estado(self, promedio):
        if promedio >= 87.5:
            return '<span style="color:#28a745;font-weight:bold;">MERITORIO</span>'
        elif promedio >= 70:
            return '<span style="color:#17a2b8;">APROBADO</span>'
        else:
            return '<span style="color:#ffc107;font-weight:bold;">EN PROCESO</span>'

    def _get_table_styles(self):
        return """
        <style>
            .report-table {width:100%;border-collapse:collapse;font-size:12px;margin-bottom:20px;}
            .report-table th,.report-table td {border:1px solid #000;padding:4px 6px;text-align:center;}
            .report-table th {background-color:#f2f2f2;}
            .subject-name {text-align:left;font-weight:bold;}
            .section-header {background:#e6e6e6;font-weight:bold;text-align:center;margin:10px 0;padding:8px;border:1px solid #ccc;}
            .student-header {background:#d4edda;font-weight:bold;text-align:left;margin:15px 0;padding:8px;border:1px solid #c3e6cb;border-radius:4px;}
        </style>
        """
