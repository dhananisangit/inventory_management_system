
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from inventory_management_system.models import (Parts, Location, Building, Inventory_details,
                                                Move_log, Product_rate, Purchase)
from inventory_management_system.serializers import (InventorySerializer, PartsSerializer,
                                                    MoveLogSerializer, ProductRateSerializer,
                                                    PurchaseSerializer, BuildingSerializer,
                                                    LocationSerializer)
from .SFDCsync import SFDC
from django.contrib.auth import authenticate, login

import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets
from .report import GenerateReport
from inventory_management_system.serializers import (InventorySerializer, PartsSerializer,
                                                    MoveLogSerializer, ProductRateSerializer,
                                                    PurchaseSerializer, BuildingSerializer,
                                                    LocationSerializer)



def group_check(user):
    groups = {'shipping'    : False,
              'purchasing'  : False,
             }

    if is_member(user, 'Shipping'):
        groups['shipping'] = True
    if is_member(user, 'Purchasing'):
        groups['purchasing'] = True

    return groups

def is_member(user, groupname):
    return user.groups.filter(name=groupname).exists()



@ensure_csrf_cookie
@login_required
def home(request):
    groups = group_check(request.user)
    context = {'title'         : 'IMS :: Home',
             'username'      : request.user,
             'controller_id' : 'move_page_ctrl',
             'shipping'      : groups['shipping'],
             'purchasing'    : groups['purchasing'],
             'admin'         : True,
            }

    return render(request, "index.html", context)


@ensure_csrf_cookie
@login_required
def track(request):
    groups = group_check(request.user)
    context = {'title'         : 'IMS :: Home',
               'username'      : request.user,
               'controller_id' : 'track_page_ctrl',
               'shipping'      : groups['shipping'],
               'purchasing'    : groups['purchasing'],
               'admin'         : True,
              }
    return render(request, "track.html", context)

@ensure_csrf_cookie
@login_required
def inventory(request):
    groups = group_check(request.user)
    context = {'title'         : 'IMS :: Home',
               'username'      : request.user,
               'controller_id' : 'inventory_page_ctrl',
               'shipping'      : groups['shipping'],
               'purchasing'    : groups['purchasing'],
               'admin'         : True,
              }
    return render(request, "inventory.html", context)

@ensure_csrf_cookie
@login_required
def purchasing(request):
    groups = group_check(request.user)
    context = {'title'         : 'IMS :: Home',
               'username'      : request.user,
               'controller_id' : 'purchasing_page_ctrl',
               'shipping'      : groups['shipping'],
               'purchasing'    : groups['purchasing'],
               'admin'         : True,
              }
    return render(request, "purchasing.html", context)


@ensure_csrf_cookie
@login_required
def addpart(request):
    groups = group_check(request.user)
    context = {'title'         : 'IMS :: Home',
               'username'      : request.user,
               'controller_id' : 'add_part_ctrl',
               'shipping'      : groups['shipping'],
               'purchasing'    : groups['purchasing'],
               'admin'         : True,
              }
    return render(request, "addpart.html", context)


@ensure_csrf_cookie
@login_required
def sfdc(request):
    groups = group_check(request.user)
    context = {'title'         : 'IMS :: Home',
               'username'      : request.user,
               'controller_id' : 'sfdc_ctrl',
               'shipping'      : groups['shipping'],
               'purchasing'    : groups['purchasing'],
               'admin'         : True,
              }
    return render(request, "sfdc.html", context)


def logout(request):
    request.session.flush()
    return render(request, "index.html")

#authenticate user
def authenticateUser(request):
    if 'user' in request.session:
        return True
    else:
        return False


@ensure_csrf_cookie
@login_required
@api_view(['GET'])
def parts_name(request):
  if request.method == 'GET':
      parts = Parts.objects.values_list('id', 'name').order_by('id')
      return Response(parts)


@ensure_csrf_cookie
@login_required
@api_view(['POST'])
def part_info(request):
  if request.method == 'POST':
      part = Inventory_details.objects.filter(part_number = request.data)
      part_info_serializer = InventorySerializer(part, many=True)

      supplier = {
                    "building":list(Building.objects.filter(name="Supplier").values_list('id')),
                    "location":list(Location.objects.filter(name="Incoming/Outgoing").values_list('id'))
                  }

      scrap = list(Location.objects.filter(name="Scrap").values_list('id'))
      production = list(Location.objects.filter(name="Production").values_list('id'))

      return Response({"part_info":part_info_serializer.data, "supplier":supplier,
                       "scrap":scrap,"production":production})


@ensure_csrf_cookie
@login_required
@api_view(['POST'])
def move_part(request):
  if request.method == 'POST':
    data = request.data
    try:
        part = Parts.objects.get(pk=data['partName'])
        to_location = Location.objects.get(pk=data['toL'])
        to_building = Building.objects.get(pk=data['toB'])
        from_location = Location.objects.get(pk=data['fromL'])
        from_building = Building.objects.get(pk=data['fromB'])

        if 'fromS' not in data and 'toS' not in data:
            if str(to_location) != "Scrap" and str(to_location) != "Production":
                to_inventory = increase_to_quantity(part, data, to_location, to_building)
            if str(from_location) != "Scrap" and str(from_location) != "Production":
                from_inventory = decrease_from_quantity(part, data, from_location, from_building)
            from_place = str(from_building) + " " + str(from_location)
            to_place = str(to_building) + " " + str(to_location)
            generate_log(part, data, from_place , to_place, request.user)

        elif 'fromS' in data:
            from_place = data['fromS']
            to_place = str(to_building) + " " + str(to_location)
            to_inventory = increase_to_quantity(part, data, to_location, to_building)
            generate_log(part, data, from_place, to_place, request.user)

        elif 'toS' in data:
            from_place = str(from_building) + " " + str(from_location)
            to_place = data['toS']
            from_inventory = decrease_from_quantity(part,data, from_location, from_building)
            generate_log(part, data, from_place, to_place, request.user)

        return Response({"status":200})
    except Exception as e:

        return Response({"status":304})


def increase_to_quantity(part, data, to_location, to_building):
    to_inventory = check_inventory(part, to_location, to_building)
    if to_inventory is None:
        Inventory_details.objects.create(part_number=part, quantity=data['qty'], location_id=to_location
                                         , building_id=to_building)
    else:
        to_inventory.quantity += int(data['qty'])
        to_inventory.save()
    return to_inventory


def decrease_from_quantity(part, data, from_location, from_building):
    from_inventory = check_inventory(part, from_location, from_building)
    from_inventory.quantity -= int(data['qty'])
    from_inventory.save()
    return from_inventory

def check_inventory(part, to_location, to_building):
    try:
        inventory = Inventory_details.objects.get(part_number=part, location_id=to_location, building_id=to_building)
        return inventory
    except:
        return None

def generate_log(part, data, from_place, to_place, user):
        Move_log.objects.create(part_number=part, quantity=data['qty'], from_inventory=from_place, to_inventory=to_place
                                        , user_id=user, reason=data['why'])



@ensure_csrf_cookie
@login_required
@api_view(['GET'])
def get_buildings(request):
  if request.method == 'GET':
      buildings = Building.objects.values_list('id', 'name')
      return Response(buildings)


@ensure_csrf_cookie
@login_required
@api_view(['POST'])
def get_locations(request):
  request.enforce_csrf_checks = True
  if request.method == 'POST':
      locations = Location.objects.filter(building_id=request.data).values_list('id', 'name', 'building_id')
      return Response(locations)

@ensure_csrf_cookie
@login_required
@api_view(['POST'])
def get_part_count(request):
  request.enforce_csrf_checks = True
  if request.method == 'POST':
      part_qty = Inventory_details.objects.filter(part_number=request.data).aggregate(qty=Sum('quantity'))
      return Response(part_qty)


@ensure_csrf_cookie
@login_required
@api_view(['GET'])
def get_history(request):
    if request.method == 'GET':
        move_log = Move_log.objects.all()
        history = MoveLogSerializer(move_log, many=True)
        return Response(history.data)


@ensure_csrf_cookie
@login_required
@api_view(['GET'])
def get_inventory(request):
  request.enforce_csrf_checks = True
  if request.method == 'GET':
    # part_details = PartsSerializer(Parts.objects.all(), many=True)
    inventory = InventorySerializer(Inventory_details.objects.all(), many=True)
    # for inv in inventory.data:
    #     for part in part_details.data:
    #         if part['name'] == inv['part_name']:
    #             inv['desc'] = part['description']
    return Response(inventory.data)


@ensure_csrf_cookie
@login_required
@api_view(['POST'])
def get_inventory_details(request):
    request.enforce_csrf_checks = True
    if request.method == 'POST':
        inventory = InventorySerializer(Inventory_details.objects.filter(part_number = request.data, quantity__gt=0), many=True)
        return Response(inventory.data)

@ensure_csrf_cookie
@login_required
@api_view(['GET'])
def get_purchase_details(request):
    request.enforce_csrf_checks = True
    if request.method == 'GET':
        purchase_details = PurchaseSerializer(Purchase.objects.all(), many=True)
        return Response(purchase_details.data)


@ensure_csrf_cookie
@login_required
@api_view(['GET'])
def get_build_rate_details(request):
    request.enforce_csrf_checks = True
    if request.method == 'GET':
        build_rate = ProductRateSerializer(Product_rate.objects.all(), many=True)
        return Response(build_rate.data)

@ensure_csrf_cookie
@login_required
@api_view(['GET'])
def get_report_data(request):
    request.enforce_csrf_checks = True
    if request.method == 'GET':
        reportData = GenerateReport()
        r = reportData.get_quote_details()
        return Response(r)



@ensure_csrf_cookie
@login_required
@api_view(['POST'])
def save_inventory_details(request):
    request.enforce_csrf_checks = True
    if request.method == 'POST':
        try:

            product = Purchase.objects.get(part_number=request.data['part'])
            product.lead_time = request.data['leadtime']
            product.qty_beamplus=request.data['beamplus']
            product.qty_beampro=request.data['beampro']
            product.save()
            return Response({"status":200})
        except Exception as e:
            return Response({"status":304})


@ensure_csrf_cookie
@login_required
@api_view(['POST'])
def save_build_rate(request):
    request.enforce_csrf_checks = True
    if request.method == 'POST':
        beamplus = Product_rate.objects.get(product='beamplus')
        beamplus.build_rate = build_rate=request.data['beamplus']
        beamplus.save()
        beampro = Product_rate.objects.get(product='beampro')
        beampro.build_rate = build_rate=request.data['beampro']
        beampro.save()
        return Response(status=200)


#
#
# @api_view(['GET'])
# def getSFDCData(request):
#     database= Database()
#     supportNumbers = database.getSuppNumbers()
#     creds = database.getSFDCKeyChainValues()
#     sfdcObject = SFDC(creds)
#     productNumbers = sfdcObject.getProductTypes()
#     accountNames = sfdcObject.getAccountNames()
#     return Response({'acc':accountNames,'prd':productNumbers,'supp':supportNumbers})
#
# @ensure_csrf_cookie
# @api_view(['POST'])
# def shipPart(request):
#     database= Database()
#     creds = database.getSFDCKeyChainValues()
#     sfdcObject = SFDC(creds)
#     id =  request.data['first']+request.data['second']
#     code = request.data['ProductCode']
#     serialNumber = request.data['serialNumber']
#     suppNumber = request.data['suppNumber']
#     assetDetails = sfdcObject.createAsset(id, code, serialNumber, suppNumber)
#     return Response(assetDetails)
#
#
# @ensure_csrf_cookie
# @api_view(['POST'])
# def receivePart(request):
#     database= Database()
#     creds = database.getSFDCKeyChainValues()
#     sfdcObject = SFDC(creds)
#     id =  request.data['first']+request.data['second']
#     serialNumber = request.data['serialNumber']
#     supp = request.data['supp']
#     updatedAssetDetails = sfdcObject.updateAsset(id, serialNumber, supp)
#     return Response(updatedAssetDetails)
#
# @ensure_csrf_cookie
# @api_view(['POST'])
# def fetchSerialNumber(request):
#     database= Database()
#     serialNumber = database.fetchSerialNumber(request.data)
#     return Response(serialNumber)
#
# @ensure_csrf_cookie
# @api_view(['POST'])
# def fetchSerialNumberFromSFDC(request):
#     database= Database()
#     creds = database.getSFDCKeyChainValues()
#     sfdcObject = SFDC(creds)
#     id =  request.data['first']+request.data['second']
#     supp = request.data['supp']
#     pType = request.data['pType']
#     serialNumber = sfdcObject.fetchSerialNumberFromSFDC(id, supp, pType)
#     return Response(serialNumber)
#
#
# @ensure_csrf_cookie
# @api_view(['POST'])
# def getQuoteDetails(request):
#     database= Database()
#     quote_details = database.getQuoteDetails(request.data)
#     return Response(quote_details)
#
#
# @ensure_csrf_cookie
# @api_view(['POST'])
# def addNewPart(request):
#     database= Database()
#     part_details = database.addNewPart(request.data)
#     return Response(part_details)
