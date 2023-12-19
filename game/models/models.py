# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
import os
# from odoo.exceptions import ValidationError


# probar demo
# valores por defecto general
class player(models.Model):
    _name = 'game.player'
    _description = 'Jugador'

    name = fields.Char(required=True)
    level = fields.Integer(default=1)
    dinos = fields.One2many('game.dino', 'player',domain=[('level','>',1)])
    edificios = fields.One2many('game.edificio', 'player', ondelete='cascade')


    carne = fields.Integer(default=3000)
    vegetal = fields.Integer(default=3000)
    oro = fields.Integer(default=10000)

    def update_player_resources(self):
        for edificio in self.edificios:
            if edificio.tipo == '4':  # Produccion
                    self.oro += edificio.produccionOro
                    self.carne += edificio.produccionCarne
                    self.vegetal += edificio.produccionVegetal

    @api.constrains('level')
    def _check_level(self):
        for record in self:
            if record.level < 1:
                raise ValidationError("No puedes tener un nivel tan bajo: %s" % record.level)

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
    imagen = fields.Image("Imagen",compute='_compute_imagen',store=True)




    @api.constrains('level')
    def _check_level(self):
        for record in self:
            if record.level < 1:
                raise ValidationError("Un dino no puede tener un nivel tan bajo: %s" % record.level)

    @api.depends('tipo')
    def _compute_imagen(self):
        for record in self:
            tipo_name = record.get_tipo_display().lower()  # Obtiene el nombre del tipo en minúsculas
            image_path = os.path.join('game', 'static', 'dino_images', f'{tipo_name}.png')

            try:
                with open(image_path, 'rb') as f:
                    record.imagen = base64.b64encode(f.read())
            except FileNotFoundError:
                record.imagen = False  # O manejar de otra manera si el archivo no se encuentra
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
    vida = fields.Integer()


    produccionOro = fields.Float(compute='_compute_produccionOro')
    produccionCarne = fields.Float(compute='_compute_produccionCarne')
    produccionVegetal = fields.Float(compute='_compute_produccionVegetal')
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
            if record.tipo == '1':
                record.vida = 1000 * record.level * 0.6
            elif record.tipo == '2':
                record.vida = 900 * record.level * 0.6
            elif record.tipo == '3':
                record.vida = 600 * record.level * 0.6
            elif record.tipo == '4':
                record.vida = 750 + record.level * 0.6

        # ALMACEN
        capacidadMaxima = fields.Integer(string='capacidadMaxima', compute='_compute_cantidad')

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
class batalla(models.Model):
    _name = 'game.batalla'
    _description = 'Batalla'

    name = fields.Char()
    start = fields.Datetime(default=lambda self: fields.Datetime.now())
    end = fields.Datetime(compute='_compute_end')
    tiempo_total = fields.Integer(compute='_compute_end')
    tiempo_restante = fields.Char(compute='_compute_end')
    progreso = fields.Float(compute='_compute_end')
    player1 = fields.Many2one('game.player')
    player2 = fields.Many2one('game.player')



    @api.depends('start')
    def _get_data_end(self):
        for t in self:
            fecha_start = fields.Datetime.from_string(t.start)
            fecha_end = fecha_start + timedelta(hours=2)

            t.end = fields.Datetime.to_string(fecha_end)
            t.tiempo_total = (fecha_end - fecha_start).total_seconds() / 60
            restante = relativedelta(fecha_end, datetime.now())
            t.tiempo_restante = str(restante.hours) + ":" + str(restante.minutes) + ":" + str(restante.seconds)

            tiempo_transcurrido = (datetime.now() - fecha_start).total_seconds()  # paso todo a segundos
            t.progreso = (tiempo_transcurrido * 100) / (t.tiempo_total * 60)

            if t.progreso > 100:
                t.progreso = 100
                t.tiempo_restante = '00:00:00'
