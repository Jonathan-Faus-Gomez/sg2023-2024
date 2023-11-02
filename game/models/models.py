# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

#probar demo
#valores por defecto general
class player(models.Model):
    _name = 'game.player'
    _description = 'Jugador'

    name = fields.Char(required=True)
    level = fields.Integer(default=1)
    dinos = fields.One2many('game.dino', 'player')
    edificios = fields.One2many('game.edificio', 'player')
    recursos = fields.One2many('game.recurso', 'player')

    @api.constrains('level')
    def _check_level(self):
        for record in self:
            if record.level < 1:
                raise ValidationError("No puedes tener un nivel tan bajo: %s" % record.level)


#valores por defecto

class dino(models.Model):
    _name = 'game.dino'
    _description = 'Dinosaurio'

    name = fields.Char()
    level = fields.Integer(default=1)
    tipo = fields.Selection([('1', 'Carnivoro'), ('2', 'Herbivoro'), ('3', 'Omnivoro')])
    player = fields.Many2one('game.player')
    vida = fields.Integer()
    ataque = fields.Integer()

    @api.constrains('level')
    def _check_level(self):
        for record in self:
            if record.level < 1:
                raise ValidationError("Un dino no puede tener un nivel tan bajo: %s" % record.level)

    # los carnívoros son los que más les mejora el ataque y menos el daño, los herbívoros al contrario y los omnívoros mejoran igual ambas estadísticas
    @api.depends('level', 'tipo')
    def _compute_vida(self):
        for record in self:
            if record.tipo == '1':  # Carnívoro
                record.vida = record.vida * 1.2
            elif record.tipo == '2':  # Herbívoro
                record.vida = record.vida * 1.4
            elif record.tipo == '3':  # Omnívoro
                record.vida = record.vida * 1.3

    @api.depends('level', 'tipo')
    def _compute_ataque(self):
        for record in self:
            if record.tipo == '1':  # Carnívoro
                record.ataque = record.ataque * 1.4
            elif record.tipo == '2':  # Herbívoro
                record.ataque = record.ataque * 1.2
            elif record.tipo == '3':  # Omnívoro
                record.ataque = record.ataque * 1.3




#valores por defecto
#relacion con recursos
#ataque tener limite y cada dino ocupe espacio
class edificio(models.Model):
    _name = 'game.edificio'
    _description = 'Edificio'

    name = fields.Char()
    tipo = fields.Selection([('1', 'Almacen'), ('2', 'Defensa'), ('3', 'Ataque'), ('4', 'Produccion')])
    level = fields.Integer(default=1)
    player = fields.Many2one('game.player')
    vida = fields.Integer()

    @api.constrains('level')
    def _check_level(self):
        for record in self:
            if record.level < 1:
                raise ValidationError("Un edificio no puede tener un nivel tan bajo: %s" % record.level)

    @api.depends('level')
    def _compute_vida(self):
        for record in self:
            record.vida = record.vida * 1.5

        # ALMACEN
        cantidad = fields.Integer(string='Cantidad', compute='_compute_cantidad')

        @api.depends('tipo')
        def _compute_cantidad(self):
            for edificio in self:
                if edificio.tipo == '1':
                    edificio.cantidad = 10000 * edificio.level


        # DEFENSA
        ataque = fields.Integer(string='Ataque', compute='_compute_ataque')

        @api.depends('tipo')
        def _compute_ataque(self):
            for edificio in self:
                if edificio.tipo == '2':
                    edificio.ataque = 100 * edificio.level / 0.7  # Calcula el ataque según tus necesidades



class recurso(models.Model):
    _name = 'game.recurso'
    _description = 'Recurso'

    name = fields.Char()
    tipo = fields.Selection([('1', 'Carne'), ('2', 'Vegetal'), ('3', 'Oro')])
    cantidad = fields.Integer()
    player = fields.Many2one('game.player')
