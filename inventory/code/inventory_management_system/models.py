from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.db import connections
import re, json
import time
import datetime
import math



class Parts(models.Model):
    name        = models.CharField(max_length=254, unique=True, verbose_name='Part Name')
    description = models.CharField(max_length=254, verbose_name='Part Description')

    def __unicode__(self):
        return unicode(self.name)

    def get_parts_name(self):
        part_names = self.objects.only('name', flat=True)
        return part_names

    def get_parts_description(self):
        parts_description = self.objects.only('description', flat=True)

    class Meta:
        verbose_name = 'Parts'
        verbose_name_plural = 'Parts'

class Building(models.Model):
    name         = models.CharField(max_length=254, unique=True, verbose_name='Name')

    def __unicode__(self):
        return unicode(self.name)

    def get_building_names(self):
        building_names = self.objects.only('name', flat=True)
        return part_names

    class Meta:
        verbose_name = 'Building'

class Location(models.Model):
    name         = models.CharField(max_length=254, unique=True, verbose_name='Name')
    building_id  = models.ForeignKey(Building, on_delete=models.PROTECT)

    def __unicode__(self):
        return unicode(self.name)

    def get_location_names(self):
        location_names = self.objects.only('name', flat=True)
        return part_names

    class Meta:
        verbose_name = 'Location'

class Inventory_details(models.Model):
    part_number   = models.ForeignKey(Parts, on_delete=models.PROTECT)
    # description   = models.CharField(max_length=510)
    # description   = Parts.objects.get(part_number=)
    quantity      = models.PositiveIntegerField()
    location_id   = models.ForeignKey(Location, default="1", on_delete=models.PROTECT)
    building_id   = models.ForeignKey(Building, on_delete=models.PROTECT)
    date_created  = models.DateTimeField(auto_now_add=True, verbose_name='Date Created')
    date_modified = models.DateTimeField(auto_now=True, verbose_name='Date Modified')

    def __unicode__(self):
        return unicode(self.part_number)

    def create(self, part_id):
        part_info = self.objects.get(part_number=part_id)
        return part_info

    def get_parts_description(self, part_id):
        parts_description = Parts.objects.filter(name=str(part_id)).values_list('description')
        return str(parts_description[0][0])


    class Meta:
        verbose_name = 'Inventory Details'
        verbose_name_plural = 'Inventory Details'

class Move_log(models.Model):
    part_number        = models.ForeignKey(Parts, on_delete=models.PROTECT)
    quantity           = models.PositiveIntegerField()
    from_inventory     = models.CharField(max_length=15)
    to_inventory       = models.CharField(max_length=15)
    date         	   = models.DateTimeField(auto_now_add=True)
    user_id            = models.ForeignKey(User)
    reason             = models.TextField(verbose_name='Reason')

    def __unicode__(self):
        return unicode(self.part_number)

    class Meta:
        verbose_name = 'Move Log'

class Product_rate(models.Model):
    build_rate   = models.FloatField(verbose_name='Build Rate')
    product     = models.CharField(max_length=254)

    def __unicode__(self):
        return unicode(self.product)

    class Meta:
        verbose_name = 'Product Rate'

class Purchase(models.Model):
    part_number   = models.ForeignKey(Parts, on_delete=models.PROTECT)
    lead_time     = models.PositiveIntegerField(verbose_name='Lead Time')
    qty_beamplus  = models.PositiveIntegerField(verbose_name='Quantity BeamPlus')
    qty_beampro   = models.PositiveIntegerField(verbose_name='Quantity BeamPro')

    def __unicode__(self):
        return unicode(self.part_number)

    class Meta:
        verbose_name = 'Purchases'
        verbose_name_plural = 'Purchases'
