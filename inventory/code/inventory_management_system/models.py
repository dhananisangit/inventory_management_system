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


# 	def getReportData(self):
# 		reportData = self.calculateQtyForReport()
# 		existing_quote_mapping, incoming_orders = self.getPurchaseQuoteMapping()
# 		new_quote = self.getPurchaseReportFigures(existing_quote_mapping, reportData, incoming_orders)

# 		for key in reportData:
# 			if key not in new_quote:
# 				data = {key:{'pn':key,'qty_on_quote':'0','qty_to_be_delivered':'0','deliver_date':'N/A','po_number':'N/A', 'qty_in_stock':reportData[key]['qty']}}
# 				new_quote.update(data)

# 		return new_quote


# 	def getPurchaseReportFigures(self, existing_quote_mapping, reportData, incoming_orders):
# 		new_quote = {}
# 		for quote in existing_quote_mapping:
# 			if quote[0][4:8] in reportData and reportData[quote[0][4:8]]['pn']==quote[0][4:8]:
# 				if quote[2]=='draft' or quote[2]=='sent':
# 					data = {quote[0][4:8]:{'pn':quote[0][4:8],'qty_on_quote':quote[3],'qty_to_be_delivered':'0','deliver_date':quote[4],'po_number':quote[1], 'qty_in_stock':reportData[quote[0][4:8]]['qty']}}
# 					new_quote.update(data)
# 				elif quote[2]=='approved':
# 					for item in incoming_orders:
# 						if quote[7]==item[2]:
# 							data = {quote[0][4:8]:{'pn':quote[0][4:8],'qty_on_quote':'0','qty_to_be_delivered':item[1],'deliver_date':quote[4],'po_number':quote[1], 'qty_in_stock':reportData[quote[0][4:8]]['qty']}}
# 							new_quote.update(data)
# 		return new_quote

# 	def addBusinessDays(self, startingDate, daysToAdjust):
# 		business_days_to_add = daysToAdjust
# 		current_date = startingDate
# 		while business_days_to_add > 0:
# 			current_date += datetime.timedelta(days=1)
# 			weekday = current_date.weekday()
# 			if weekday >= 5: # sunday = 6 and saturday = 5
# 				continue
# 			business_days_to_add -= 1
# 		return '%s/%s/%s'%(current_date.month,current_date.day,current_date.year)


# 	def calculateQtyForReport(self):
# 		rows = self.getInventory()
# 		reportData = {}
# 		for row in rows:
# 			r = str(row[0])
# 			if r in reportData:
# 				reportData[r]['qty']+= row[2]
# 				if reportData[r]['desc'] is None and row[1] is not None:
# 					reportData[r]['desc']=row[1]
# 			else:
# 				data = {row[0]:{'pn':row[0],'desc':row[1],'qty':row[2]}}
# 				reportData.update(data)
# 		return reportData


# 	def getPurchaseQuoteMapping(self):
# 		with connections['sterp'].cursor() as cursor:
# 			cursor.execute("SELECT product_product.default_code, purchase_order.name, purchase_order.state, purchase_order_line.product_qty, purchase_order_line.date_planned, res_partner.name, purchase_order_line.price_unit, purchase_order.id FROM purchase_order INNER JOIN purchase_order_line ON purchase_order.id=purchase_order_line.order_id INNER JOIN product_product ON purchase_order_line.product_id=product_product.id FULL OUTER JOIN res_partner ON purchase_order.partner_id=res_partner.id WHERE (purchase_order.state='draft' OR purchase_order.state='sent' OR purchase_order.state='approved') AND product_product.default_code LIKE '83-0%'")
# 			existing_quote_mapping = cursor.fetchall()
# 			cursor.execute("SELECT stock_picking.min_date, purchase_order_line.product_qty, purchase_order.id FROM stock_picking INNER JOIN purchase_order ON stock_picking.purchase_id=purchase_order.id INNER JOIN purchase_order_line ON purchase_order.id=purchase_order_line.order_id WHERE stock_picking.type='in' AND stock_picking.state='assigned'")
# 			incoming_orders = cursor.fetchall()

# 		return (existing_quote_mapping, incoming_orders)


# 	def getInventoryDetails(self, partname):
# 		with connections['default'].cursor() as cursor:
# 			cursor.execute("SELECT qty, location, building, date FROM inventory_details WHERE pn=\'%s\'" % partname)
# 			row = cursor.fetchall()
# 		with connections['sterp'].cursor() as cursor:
# 			cursor.execute("SELECT product_product.default_code, purchase_order_line.price_unit, purchase_order.date_order, res_partner.name FROM purchase_order_line INNER JOIN product_product ON purchase_order_line.product_id=product_product.id INNER JOIN purchase_order ON purchase_order_line.order_id=purchase_order.id FULL OUTER JOIN res_partner ON purchase_order.partner_id=res_partner.id WHERE product_product.default_code='83-0%s' ORDER BY purchase_order.date_order DESC LIMIT 1;"%(partname))
# 			part_details = cursor.fetchall()
# 		return (row, part_details)


# 		with connections['default'].cursor() as cursor:
# 			cursor.execute(query)
# 		return "done"

# 	def saveBuildRate(self, data):
# 		d =json.dumps(data)
# 		s = json.loads(d)
# 		beamplus = 'Beam+'
# 		beampro = 'BeamPro'
# 		with connections['default'].cursor() as cursor:
# 			cursor.execute("""UPDATE product_rate SET build_rate=%s WHERE product=\'%s\'"""% (s['beampro'], beampro))
# 			cursor.execute("""UPDATE product_rate SET build_rate=%s WHERE product=\'%s\'"""% (s['beamplus'], beamplus))
# 			#row = cursor.fetchall()
# 		return "done"



# 	def getSFDCKeyChainValues(self):
# 		with connections['default'].cursor() as cursor:
# 			cursor.execute("SELECT * FROM sfdc_credentials")
# 			row = cursor.fetchall()
# 		return row

# 	def getSuppNumbers(self):
# 		with connections['sterp'].cursor() as cursor:
# 			cursor.execute("SELECT DISTINCT origin FROM stock_move WHERE origin LIKE 'SUPP%' ")
# 			row = cursor.fetchall()
# 		return row


# 	def fetchSerialNumber(self, part):
# 		supp = "SUPP-"+str(part)
# 		with connections['sterp'].cursor() as cursor:
# 			cursor.execute("""SELECT stock_production_lot.name, product_product.default_code FROM stock_production_lot INNER JOIN stock_move_lot ON stock_production_lot.id=stock_move_lot.production_lot FULL OUTER JOIN stock_move ON stock_move_lot.stock_move_id=stock_move.id INNER JOIN product_product ON stock_move.product_id=product_product.id WHERE stock_move.origin=\'%s\'"""%supp)
# 			row = cursor.fetchall()
# 		return row


# 	def getQuoteDetails(self, tool_quote):
# 		reportData = self.calculateQtyForReport()
# 		build_rate = self.getBuildRateDetails()
# 		leadtime = self.getPurchaseDetails()
# 		beampro = build_rate[0][0]
# 		beamplus = build_rate[1][0]
# 		final_data = {}

# 		for lead_data in leadtime:
# 			formula = ((float(lead_data[2]) if lead_data[2] is not None else 0*float(beamplus))+(float(lead_data[3]) if lead_data[3] is not None else 0*float(beampro)))*1.25
# 			part_number = str(lead_data[0]).strip()
# 			if part_number in reportData and reportData[part_number]['qty']<=formula*float(lead_data[1]):

# 				days = reportData[part_number]['qty']/formula if formula != 0.0 else 0
# 				today = datetime.date.today()
# 				date = self.addBusinessDays(today, days)
# 				stock_difference = tool_quote[part_number]['qty_to_order'] - math.floor(formula*float(lead_data[1]))
# 				if stock_difference >=0: # change to >0 when need to improve UI changes
# 					final_data[part_number] = {'pn':part_number,'qty':stock_difference,'needbydate':date}


# 		return final_data


# 	def addNewPart(self, new_part_data):
# 		with connections['default'].cursor() as cursor:
# 			try:
# 				cursor.execute("SELECT pn FROM purchase WHERE pn=\'%s\'"%new_part_data['pn'])
# 				part_exists = True if cursor.fetchall() else False
# 				if not part_exists:
# 					cursor.execute("INSERT INTO purchase VALUES(\'%s\',\'%s\')"%(new_part_data['pn'],new_part_data['lead_time']))
# 					return "Inserted"
# 				else:
# 					return "Part Already Exists"
# 			except Exception as e:
# 				return str(e)
# 				# return json.dumps(e, default=JSONEncoder)


# 	def JSONEncoder(e):
# 		if isinstance(e, ObjectId):
# 			return str(e)
