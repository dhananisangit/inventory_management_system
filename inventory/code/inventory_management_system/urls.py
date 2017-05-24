from django.http import HttpResponse
from inventory_management_system import views
from django.conf.urls import include, url
from django.contrib import admin



urlpatterns = [
    url(r'^accounts/', include('auth_odoo.urls')),
    url(r'^admin/', admin.site.urls),
    # url(r'^', include('auth_odoo.urls')),
    url(r'^home$', views.home, name='home'),
    url(r'^track$', views.track, name='track'),
    url(r'^purchasing$', views.purchasing, name='purchasing'),
    # url(r'^purchasing/[0-9]{4}$', views.purchasing, name='purchasing'),
    url(r'^addpart$', views.addpart, name='addpart'),
    url(r'^sfdc$', views.sfdc, name='sfdc'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^inventory$', views.inventory, name='inventory'),
    url(r'v1/login$', views.login),
    url(r'v1/getpartsname$', views.parts_name),
    url(r'v1/getpartinfo$', views.part_info),
    url(r'v1/changepartlocation$', views.move_part),
    url(r'v1/getbuildings$', views.get_buildings),
    url(r'v1/getlocations$', views.get_locations),
    url(r'v1/gethistory$', views.get_history),
    url(r'v1/getinventorylist$', views.get_inventory),
    url(r'v1/getpartcount$', views.get_part_count),
    url(r'v1/getinventorypartdetails$', views.get_inventory_details),
    url(r'v1/getpurchasingdetails$', views.get_purchase_details),
    url(r'v1/getbuildratedetails$', views.get_build_rate_details),
    url(r'v1/saveinventorydetails$', views.save_inventory_details),
    url(r'v1/savebuildrate$', views.save_build_rate),
    # url(r'v1/deletepart$', views.delete_part),
    url(r'v1/getreportdata$', views.get_report_data),
    # url(r'v1/getsfdcdata$', views.getSFDCData),
    # url(r'v1/shippart$', views.shipPart),
    # url(r'v1/receivepart$', views.receivePart),
    # url(r'v1/fetchserialnumber$', views.fetchSerialNumber),
    # url(r'v1/fetchserialnumberfromsfdc$', views.fetchSerialNumberFromSFDC),
    # url(r'v1/getquotedetails$', views.getQuoteDetails),
    # url(r'v1/addnewpart$', views.addNewPart),
]
