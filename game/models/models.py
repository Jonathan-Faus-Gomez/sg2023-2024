# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


# probar demo
# valores por defecto general
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


# valores por defecto


#las tropas del ejercito de este juego son dinosaurios
class dino(models.Model):
    _name = 'game.dino'
    _description = 'Dinosaurio'

    name = fields.Char()
    level = fields.Integer(default=1)
    tipo = fields.Selection([('1', 'Carnivoro'), ('2', 'Herbivoro'), ('3', 'Omnivoro')])
    player = fields.Many2one('game.player')
    vida = fields.Float(compute='_compute_vida')
    ataque = fields.Float(compute='_compute_ataque')
    tamany = fields.Selection([('1', 'Enano'), ('2', 'Pequeño'), ('3', 'Mediano'), ('4', 'Grande'), ('5', 'Gigante')])
    ocupa = fields.Integer(compute='_compute_ocupa')

    @api.constrains('level')
    def _check_level(self):
        for record in self:
            if record.level < 1:
                raise ValidationError("Un dino no puede tener un nivel tan bajo: %s" % record.level)

    # los carnívoros son los que más les mejora el ataque y menos el daño, los herbívoros al contrario y los omnívoros mejoran igual ambas estadísticas
    # error -> tengo que desinstalar e instalar de nuevo game

    @api.depends('tamany')
    def _compute_ocupa(self):
        for record in self:
            if record.tamany == '1':
                record.ocupa = 1
            elif record.tamany == '2':
                record.ocupa = 2
            elif record.tamany == '3':
                record.ocupa = 4
            elif record.tamany == '4':
                record.ocupa = 8
            elif record.tamany == '5':
                record.ocupa = 16
            else:
                record.ocupa = 0  # no deberia pasar(si pasa sus estadisticas serán todas 0 al multiplicar por 0)

    @api.depends('level')
    def _compute_vida(self):
        for record in self:
            record.vida = 1
            if record.tipo == '1':  # Carnívoro
                record.vida = 70 * record.level * 0.7 * record.ocupa
            elif record.tipo == '2':  # Herbívoro
                record.vida = 90 * record.level * 0.7 * record.ocupa
            elif record.tipo == '3':  # Omnívoro
                record.vida = 80 * record.level * 0.7 * record.ocupa

    @api.depends('level')
    def _compute_ataque(self):
        for record in self:
            record.ataque = 0
            if record.tipo == '1':  # Carnívoro
                record.ataque = 30 * record.level * 0.7 * record.ocupa
            elif record.tipo == '2':  # Herbívoro
                record.ataque = 20 * record.level * 0.7 * record.ocupa
            elif record.tipo == '3':  # Omnívoro
                record.ataque = 25 * record.level * 0.7 * record.ocupa


# valores por defecto
# relacion con recursos
# ataque tener limite y cada dino ocupe espacio
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
            if record.tipo == '1':
                record.vida = 1000 * record.level * 0.6
            elif record.tipo == '2':
                record.vida = 900 * record.level * 0.6
            elif record.tipo == '3':
                record.vida = 600 * record.level * 0.6
            elif record.tipo == '4':
                record.vida = 750 + record.level * 0.6

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
                    edificio.ataque = 100 * edificio.level * 0.8


class recurso(models.Model):
    _name = 'game.recurso'
    _description = 'Recurso'

    name = fields.Char()
    tipo = fields.Selection([('1', 'Carne'), ('2', 'Vegetal'), ('3', 'Oro')])
    cantidad = fields.Integer()
    player = fields.Many2one('game.player')


class batalla(models.Model):
    _name = 'game.batalla'
    _description = 'Batalla'

    start = fields.Datetime()
    end = fields.Datetime()
    name = fields.Char()
