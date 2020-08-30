# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_template_id = fields.Many2one('project.template')
    project_manager_id = fields.Many2one('res.users')
    project_id = fields.Many2one('project.project')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        lst = []
        if self.project_template_id:
            project_obj = self.env['project.project']
            task_obj = self.env['project.task']
            project_id = project_obj.create({
                'name': self.project_template_id.name,
                'user_id': self.project_manager_id.id,
            })
            if self.project_template_id.project_task_type_ids:
                for i in self.project_template_id.project_task_type_ids:
                    i.project_ids = [[6, 0, [project_id.id]]]
            if self.project_template_id.task_ids:
                print("lennnnnnnnn", len(self.project_template_id.task_ids))
                task_ids = self.project_template_id.task_ids.filtered(lambda i: i.start_confirmation_date == True)
                depend_task_ids = self.project_template_id.task_ids.filtered(lambda i: i.start_confirmation_date == False)
                print("..................: task_ids", task_ids)
                # raise UserError(_("dddddddddddddddddddddd"))
                for t in task_ids:
                    print("t1", t.confirmation_date)
                    t.confirmation_date = self.date_order
                    print("t2", t.confirmation_date)
                    task_obj.create({
                        'name': self.name + " " + t.name,
                        'start_date': t.start_date,
                        'date_deadline': t.end_date,
                        'project_id': project_id.id,
                        'user_id': self.project_manager_id.id,
                        'stage_id': t.project_stage_id.id,
                    })
                for d in depend_task_ids:
                    task_obj.create({
                        'name': self.name + " " + d.name,
                        'start_date': d.start_date,
                        'date_deadline': d.end_date,
                        'project_id': project_id.id,
                        'user_id': self.project_manager_id.id,
                        'stage_id': d.project_stage_id.id,
                    })
                # raise UserError(_("dddddddddddddddddddddd"))
                #
                #
                # for t in self.project_template_id.task_ids:
                #     if t.start_confirmation_date:
                #         t.confirmation_date = self.date_order
                #         task_obj.create({
                #             'name': self.name + " " + t.name,
                #             'date_assign': t.start_date,
                #             'date_deadline': t.end_date,
                #             'project_id': project_id.id,
                #             'user_id': self.project_manager_id.id,
                #             'stage_id': t.project_stage_id.id,
                #         })
                #
                #     else:
                #         if t.task_id.start_date:
                #             task_obj.create({
                #                 'name': self.name + " " + t.name,
                #                 'date_assign': t.start_date,
                #                 'date_deadline': t.end_date,
                #                 'project_id': project_id.id,
                #                 'user_id': self.project_manager_id.id,
                #                 'stage_id': t.project_stage_id.id,
                #             })
                        # else:
                        #     lst.append(t)

            self.project_id = project_id.id
        return res