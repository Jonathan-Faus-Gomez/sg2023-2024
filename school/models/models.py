# -*- coding: utf-8 -*-

from odoo import models, fields, api


class student(models.Model):
    _name = 'school.student'
    _description = 'The students'

    name = fields.Char()
    telefono = fields.Integer()
    nacimiento = fields.Datetime()
    mayorEdad = fields.Boolean()
    curso = fields.Selection(
        [('1', 'Primer curso'), ('2', 'Segundo curso'), ('3', 'Tercer curso'), ('4', 'Cuarto curso')])

    topics = fields.Many2many('school.topic')

    passed_topics = fields.Many2many(comodel_name="school.topic",
                                     relation="passes_topics_students",
                                     column1="student_id",
                                     column2="topic_id")

    qualification = fields.One2many('school.qualification', 'student')


class topic(models.Model):
    _name = 'school.topic'
    _description = 'The Topics'

    name = fields.Char()
    teacher = fields.Many2one('school.teacher')
    teacher_phone = fields.Char(relate="teacher.phone")
    students = fields.Many2many('school.student')

    passed_students = fields.Many2many(comodel_name="school.topic",
                                       relation="passes_topics_students",
                                       column1="topic_id",
                                       column2="student_id")

    qualification = fields.One2many('school.qualification', 'topic')


class teacher(models.Model):
    _name = "school.teacher"
    _description = "The teachers"

    name = fields.Char()
    phone = fields.Char()
    topics = fields.One2many('school.topic', 'teacher')


class qualification(models.Model):
    _name = "school.qualification"
    _description = "The qualifications"

    student = fields.Many2one('school.student')
    topic = fields.Many2one('school.topic')
    qualification = fields.Float()
