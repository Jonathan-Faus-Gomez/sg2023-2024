# -*- coding: utf-8 -*-

from odoo import models, fields, api


class player(models.Model):
    _name = 'game.player'
    _description = 'Jugador'

    name = fields.Char(required=True)
    level = fields.Integer()
    dino = fields.One2many('game.dino','player')

class dino(models.Model):
    _name= 'game_dino'
    _description= 'Dinosaurio'

    level = fields.Integer()
    tipo = fields.Selection([('1', 'Carnivoro'), ('2', 'Herbivoro'), ('3', 'Omnivoro')])
    player=fields.Many2one('game.player')



class edificio(models.Model):
    _name= 'game_edificio'
    _description= 'Edificio'

    tipo = fields.Selection([('1', 'Almacen'), ('2', 'Defensa'),('3', 'Ataque'), ('4', 'Produccion')])
