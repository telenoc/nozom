# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ProjectTask(models.Model):
    _inherit = 'project.task'

    start_date = fields.Date()


class ProjectTemplate(models.Model):
    _name = 'project.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    project_task_type_ids = fields.Many2many('project.task.type')
    task_ids = fields.One2many('project.template.task', 'project_template_id')


class ProjectTemplateTask(models.Model):
    _name = 'project.template.task'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    project_template_id = fields.Many2one('project.template')
    project_stage_id = fields.Many2one('project.task.type')
    # domain=lambda x: [('id', 'in', x.project_template_id.project_task_type_ids.ids)])
    no_of_days = fields.Integer(default=1)
    start_confirmation_date = fields.Boolean(default=True)
    task_id = fields.Many2one('project.template.task')
    days_from_depend_date = fields.Integer(default=0)
    confirmation_date = fields.Date(default = fields.date.today())
    start_date = fields.Date(compute="get_start_date")
    # default = fields.date.today()
    end_date = fields.Date(compute="get_end_date")

    @api.onchange('project_template_id', 'project_stage_id')
    def onchange_project_stage_id(self):
        if self.project_template_id:
            domain = {'project_stage_id': [('id', 'in', self.project_template_id.project_task_type_ids.ids if self.project_template_id else False)],
                      'task_id': [('id', 'in', self.search([('project_template_id', '=',self.project_template_id.id)]).ids)]}
            return {'domain': domain}

    @api.depends('confirmation_date', 'days_from_depend_date', 'task_id')
    def get_start_date(self):
        for record in self:
            if record.start_confirmation_date:
                if record.days_from_depend_date == 0:
                    d1 = record.confirmation_date
                else:
                    d1 = record.confirmation_date + timedelta(days=record.days_from_depend_date)
                record.start_date = d1
            else:
                if record.task_id:
                    task_end_date = record.task_id.end_date
                    if record.days_from_depend_date == 0:
                        d1 = task_end_date
                    else:
                        d1 = task_end_date + timedelta(days=record.days_from_depend_date)
                    record.start_date = d1

    @api.depends('start_date', 'no_of_days')
    def get_end_date(self):
        for record in self:
            if record.start_date and record.no_of_days:
                d1 = record.start_date + timedelta(days=record.no_of_days)
                record.end_date = d1
