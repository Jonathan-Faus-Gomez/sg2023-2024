# -*- coding: utf-8 -*-

from odoo import models, fields, api


class player(models.Model):
    _name = 'game.player'
    _description = 'El jugador'

    name = fields.Char()
    level = fields.Integer()

