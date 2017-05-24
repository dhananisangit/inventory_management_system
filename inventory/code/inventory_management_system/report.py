from django.db.models import Sum, Avg
from django.db import connections
import datetime
import math
from .models import Purchase, Product_rate, Parts, Inventory_details, Building, Location
from .serializers import (InventorySerializer, PartsSerializer,MoveLogSerializer,
                                                    ProductRateSerializer,PurchaseSerializer,
                                                    BuildingSerializer, LocationSerializer)



class GenerateReport():
    def get_quote_details(self):
        inventory = Inventory_details.objects.all()
        reportData = {}
        for part in inventory:
            p = str(part)
            if str(part) in reportData:
                reportData[p]['qty'] += part.quantity
            else:
                reportData[p] = {'part_id':part.part_number_id,'qty':part.quantity, 'pn':p, 'desc':part.get_parts_description(part.part_number)}
        build_rate = Product_rate.objects.all()
        beamplus = build_rate[0].build_rate
        beampro = build_rate[1].build_rate
        purchase_details = Purchase.objects.all()
        final_data = {}
        for data in purchase_details:
            part = str(data.part_number)

            formula = ((data.qty_beamplus*beamplus)+(data.qty_beampro*beampro))*1.25
            if part in reportData and reportData[part]['qty']<=formula*data.lead_time:
                days = reportData[part]['qty']/formula if formula!=0.0 else 0
                today = datetime.date.today()
                need_by_date = self.addBusinessDays(today, days)
                if math.floor(formula*data.lead_time)>0:
                    final_data[reportData[part]['part_id']] = {'pn':reportData[part]['pn'], 'qty':reportData[part]['qty'], 'minqty':math.floor(formula*data.lead_time), 'needbydate':need_by_date, 'desc':reportData[part]['desc']}
        return final_data


    def addBusinessDays(self, startingDate, daysToAdjust):
    	business_days_to_add = daysToAdjust
    	current_date = startingDate
    	while business_days_to_add > 0:
    		current_date += datetime.timedelta(days=1)
    		weekday = current_date.weekday()
    		if weekday >= 5: # sunday = 6 and saturday = 5
    			continue
    		business_days_to_add -= 1
    	return '%s/%s/%s'%(current_date.month,current_date.day,current_date.year)

    # def init_report(self):
    # 	inventory_details = Inventory_details.objects.annotate(Sum('quantity'))
    # 	existing_quote_mapping, incoming_orders = self.getPurchaseQuoteMapping()
    # 	new_quote = self.getPurchaseReportFigures(existing_quote_mapping, inventory_details, incoming_orders)
    # 	return new_quote

    # def getPurchaseQuoteMapping(self):
    # 	with connections['sterp'].cursor() as cursor:
    # 		cursor.execute("SELECT product_product.default_code, purchase_order.name, purchase_order.state,\
    #                         purchase_order_line.product_qty, purchase_order_line.date_planned, res_partner.name,\
    #                         purchase_order_line.price_unit, purchase_order.id FROM purchase_order INNER JOIN\
    #                         purchase_order_line ON purchase_order.id=purchase_order_line.order_id INNER JOIN\
    #                         product_product ON purchase_order_line.product_id=product_product.id FULL OUTER JOIN\
    #                         res_partner ON purchase_order.partner_id=res_partner.id WHERE (purchase_order.state='draft'\
    #                         OR purchase_order.state='sent' OR purchase_order.state='approved') AND\
    #                         product_product.default_code LIKE '83-0%'")
    #
    # 		existing_quote_mapping = cursor.fetchall()
    #
    # 		cursor.execute("SELECT stock_picking.min_date, purchase_order_line.product_qty, purchase_order.id\
    #                         FROM stock_picking INNER JOIN purchase_order ON stock_picking.purchase_id=purchase_order.id\
    #                         INNER JOIN purchase_order_line ON purchase_order.id=purchase_order_line.order_id WHERE\
    #                         stock_picking.type='in' AND stock_picking.state='assigned'")
    # 		incoming_orders = cursor.fetchall()
    #
    # 	return (existing_quote_mapping, incoming_orders)




    # def getPurchaseReportFigures(self, existing_quote_mapping, reportData, incoming_orders):
    # 	new_quote = {}
    # 	for quote in existing_quote_mapping:
    # 		if quote[0][4:8] in reportData and reportData[quote[0][4:8]]['pn']==quote[0][4:8]:
    # 			if quote[2]=='draft' or quote[2]=='sent':
    # 				data = {quote[0][4:8]:{'pn':quote[0][4:8],'qty_on_quote':quote[3],'qty_to_be_delivered':'0','deliver_date':quote[4],'po_number':quote[1], 'qty_in_stock':reportData[quote[0][4:8]]['qty']}}
    # 				new_quote.update(data)
    # 			elif quote[2]=='approved':
    # 				for item in incoming_orders:
    # 					if quote[7]==item[2]:
    # 						data = {quote[0][4:8]:{'pn':quote[0][4:8],'qty_on_quote':'0','qty_to_be_delivered':item[1],'deliver_date':quote[4],'po_number':quote[1], 'qty_in_stock':reportData[quote[0][4:8]]['qty']}}
    # 						new_quote.update(data)
    # 	return new_quote
