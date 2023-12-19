# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
import os
import logging

_logger = logging.getLogger(__name__)


# from odoo.exceptions import ValidationError


# probar demo
# valores por defecto general
class player(models.Model):
    _name = 'game.player'
    _description = 'Jugador'

    name = fields.Char(required=True)
    level = fields.Integer(default=1)
    dinos = fields.One2many('game.dino', 'player', domain=[('level', '>', 1)])
    edificios = fields.One2many('game.edificio', 'player', ondelete='cascade')

    batallas = fields.Many2many('game.batalla')
    poder= fields.Integer(compute='_compute_poder')

    carne = fields.Integer(default=3000)
    vegetal = fields.Integer(default=3000)
    oro = fields.Integer(default=10000)

    @api.depends('dinos', 'edificios')
    def _compute_poder(self):
        for player in self:
            poder_total = 0
            for dino in player.dinos:
                poder_total += dino.vida + dino.ataque

            for edificio in player.edificios:
                poder_total += edificio.vida + edificio.ataque

            player.poder = poder_total



    def update_player_resources(self):
        for player in self.search([]):
            oro = player.oro
            carne = player.carne
            vegetal = player.vegetal
            for edificio in player.edificios:
                oro += edificio.produccionOro
                vegetal += edificio.produccionVegetal
                carne += edificio.produccionCarne

            player.oro = oro
            player.carne = carne
            player.vegetal = vegetal

    @api.constrains('level')
    def _check_level(self):
        for record in self:
            if record.level < 1:
                raise ValidationError("No puedes tener un nivel tan bajo: %s" % record.level)

    @api.constrains('dinos')
    def _calcular_espacio(self):
        for record in self:
            sum_tamany = sum(record.dinos.mapped('tamany'))
            for edificio in player.edificios:
                sum_capacidad = sum(edificio.mapped('capacidadMaxima'))
                if sum_tamany > sum_capacidad:
                    raise ValidationError("No caben más dinos en el campamento")

    @api.onchange('name')
    def _onchange_name(self):
        # Verifico si algun player ya tiene ese nombre
        existing_player = self.env['game.player'].search([('name', '=', self.name)])
        if existing_player:
            self.name = ''
            return {'warning': {'title': 'Nombre usado', 'message': 'Ese nombre ya está en uso por otro jugador'}}


# valores por defecto


# las tropas del ejercito de este juego son dinosaurios
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
    @api.model
    def find_player_by_name(self, player_name):
        # Devuelve el jugador si lo encuentra, sino devuelve null

        player = self.search([('name', '=', player_name)], limit=1)
        return player

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

# ataque tener limite y cada dino ocupe espacio
class edificio(models.Model):
    _name = 'game.edificio'
    _description = 'Edificio'

    name = fields.Char()
    tipo = fields.Selection([('1', 'Almacen'), ('2', 'Defensa'), ('3', 'Ataque'), ('4', 'Produccion')])
    tipoProduccion = fields.Selection([('1', 'Oro'), ('2', 'Carne'), ('3', 'Vegetal')])
    level = fields.Integer(default=1)
    player = fields.Many2one('game.player')
    vida = fields.Integer(compute='_compute_vida')

    produccionOro = fields.Float(compute='_compute_produccionOro')
    produccionCarne = fields.Float(compute='_compute_produccionCarne')
    produccionVegetal = fields.Float(compute='_compute_produccionVegetal')

    # ALMACEN
    capacidadMaxima = fields.Integer(string='capacidadMaxima', compute='_compute_cantidad')

    # DEFENSA
    ataque = fields.Integer(string='Ataque', compute='_compute_ataque')
    @api.depends('level')
    def _compute_produccion(self):
        for record in self:
            record.produccionOro = 0
            record.produccionCarne = 0
            record.produccionVegetal = 0
            if record.tipo == '4':
                if record.tipoProduccion == '1':
                    record.produccionOro = record.level * 1000
                elif record.tipoProduccion == '2':
                    record.produccionCarne = record.level * 50
                elif record.tipoProduccion == '3':
                    record.produccionVegetal = record.level * 50

    @api.constrains('level')
    def _check_level(self):
        for record in self:
            if record.level < 1:
                raise ValidationError("Un edificio no puede tener un nivel tan bajo: %s" % record.level)

    @api.depends('level')
    def _compute_vida(self):
        for record in self:
            record.vida = 0
            if record.tipo == '1':
                record.vida = 1000 * record.level * 0.6
            elif record.tipo == '2':
                record.vida = 900 * record.level * 0.6
            elif record.tipo == '3':
                record.vida = 600 * record.level * 0.6
            elif record.tipo == '4':
                record.vida = 750 + record.level * 0.6



    @api.depends('tipo')
    def _compute_cantidad(self):
        for edificio in self:
            if edificio.tipo == '1':
                edificio.capacidadMaxima = 100 * edificio.level



    @api.depends('tipo')
    def _compute_ataque(self):
        for edificio in self:
            edificio.ataque=0
            if edificio.tipo == '2':
                edificio.ataque = 100 * edificio.level * 0.8


class batalla(models.Model):
    _name = 'game.batalla'
    _description = 'Batalla'

    name = fields.Char()
    inicio = fields.Datetime(default=lambda self: fields.Datetime.now())
    fin = fields.Datetime(compute='_calcular_fin')
    tiempo_total = fields.Integer(compute='_calcular_fin')
    tiempo_restante = fields.Char(compute='_calcular_fin')
    progreso = fields.Float(compute='_calcular_fin')
    player1 = fields.Many2one('game.player', ondelete='set null')
    player2 = fields.Many2one('game.player', ondelete='set null')

    @api.constrains('player1', 'player2')
    def _verificar_jugadores(self):
        for record in self:
            if record.player1 and record.player2 and record.player1.id == record.player2.id:
                raise ValidationError("Un jugador no puede atacar a sí mismo")



    def calcular_batalla(self, player1, player2):
        partida = 0
        #0 empate
        #1 gana player1
        #-1 gana player2

        if player1.poder > player2.poder:
            partida = 1
        elif player2.poder > player1.poder:
            partida = -1

        if partida == 1:
            player1.write({'oro': player1.oro + 3000 * player1.level})
            player2.write({'oro': player2.oro - 3000 * player2.level})
            self.write({'ganador': player1.id})
        if partida == -1:
            player2.write({'oro': player2.oro + 3000 * player2.level})
            player1.write({'oro': player1.oro - 3000 * player1.level})
            self.write({'ganador': player2.id})

    def update_battles(self):
        domain = [('finalizado', '=', False), ('progreso', '>=', 100)]
        battle_count = self.search_count(domain)
        battles = self.search(domain, limit=battle_count)

        for record in battles:
            record.calcular_batalla(record.player1, record.player2)
            record.write({'finalizado': True})

    def finalizar_batalla(self):
        for record in self:
            if not record.finalizado:
                record.calcular_batalla(record.player1, record.player2)
                record.write({'progreso': 100.00, 'finalizado': True})

    @api.depends('inicio')
    def _calcular_fin(self):
        for record in self:
            fecha_inicio = fields.Datetime.from_string(record.inicio)
            fecha_fin = fecha_inicio + timedelta(hours=2)



            record.fin = fields.Datetime.to_string(fecha_fin)
            record.tiempo_total = (fecha_fin - fecha_inicio).total_seconds() / 60 #minutos

            tiempo_pasado = (datetime.now() - fecha_inicio).total_seconds() / 60
            restante = fecha_fin - datetime.now()
            record.tiempo_restante = "{:02}:{:02}:{:02}".format(restante.seconds // 3600, (restante.seconds // 60) % 60,
                                                                restante.seconds % 60)
            record.progreso = (tiempo_pasado * 100) / record.tiempo_total

