from rest_framework import serializers
from inventory_management_system.models import (Parts, Building, Location,
												Inventory_details, Move_log,
												Product_rate, Purchase)



class PartsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Parts
		fields = ('name', 'description')

class BuildingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Building
		fields = ('name',)

class LocationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Location
		fields = ('name', 'building_id')


class InventorySerializer(serializers.ModelSerializer):
	part_name = serializers.SerializerMethodField()
	building_name = serializers.SerializerMethodField()
	location_name = serializers.SerializerMethodField()
	description = serializers.SerializerMethodField()

	class Meta:
		model = Inventory_details
		fields = ( 'part_number', 'quantity', 'location_id', 'building_id',
				   'part_name', 'building_name', 'location_name', 'date_modified', 'description')

	def get_part_name(self, obj):
		return str(obj)

	def get_building_name(self, obj):
		return str(obj.building_id)

	def get_location_name(self, obj):
		return str(obj.location_id)

	def get_description(self, obj):
		return str(obj.get_parts_description(obj))

class MoveLogSerializer(serializers.ModelSerializer):
	part_name = serializers.SerializerMethodField()

	class Meta:
		model = Move_log
		fields = ('part_number_id', 'date', 'reason', 'user_id_id', 'from_inventory', 'to_inventory', 'quantity','part_name')

	def get_part_name(self, obj):
		return str(obj)

class ProductRateSerializer(serializers.ModelSerializer):

	class Meta:
		model = Product_rate
		fields = ('build_rate', 'product')


class PurchaseSerializer(serializers.ModelSerializer):
	part_name = serializers.SerializerMethodField()

	class Meta:
		model = Purchase
		fields = ('part_number', 'lead_time', 'qty_beamplus', 'qty_beampro', 'part_name', 'part_number_id')

	def get_part_name(self, obj):
		return str(obj)
