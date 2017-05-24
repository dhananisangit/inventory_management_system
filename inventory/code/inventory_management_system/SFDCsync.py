import time
import simple_salesforce

class SFDC():
	def __init__(self, data):
		self.sfdc_username       = data[0][0]
		self.sfdc_pwd            = data[0][1]
		self.sfdc_security_token = data[0][2]
		self.sfdc_instance_url   = data[0][3]
		self.sfdc_is_sandbox     = data[0][4]
		try:
			self.sf = simple_salesforce.Salesforce(instance_url=self.sfdc_instance_url, username=self.sfdc_username, password=self.sfdc_pwd, security_token=self.sfdc_security_token, sandbox=self.sfdc_is_sandbox)
		except Exception as e:
			print "failed"
			
	def getProductTypes(self):
		return self.sf.query("SELECT ProductCode FROM PricebookEntry WHERE Pricebook2.Id = '01s1a000002SJHr'")

	def getAccountNames(self):
		return self.sf.query("SELECT Name, Id FROM Account")

	def createAsset(self, acc, code, serialNumber, suppNumber):
		products = self.sf.query("SELECT Id, name, UnitPrice FROM PricebookEntry WHERE Pricebook2.Id = '01s1a000002SJHr' AND ProductCode = \'%s\'"%code)
		pricebook = products['records'][0]['Id']
		UnitPrice = products['records'][0]['UnitPrice']
		pd = self.sf.Product2.get(self.sf.PricebookEntry.get(pricebook).get('Product2Id'))
		description = "SUPP-"+str(suppNumber)
		acc = self.sf.Asset.create({
			'Name':code +' '+pd['Name'],
			'AccountId':acc,
			'Product2Id':pd['Id'],
			'Price':UnitPrice,
			'SerialNumber':serialNumber,
			'Status':'Shipped',
			'Quantity':1,
			'Description':description
			})

		return "Success"


	def updateAsset(self, acc, serialNumber, supp):
		description = "SUPP-"+str(supp)
		asset = self.sf.query("SELECT Id, PurchaseDate, InstallDate, UsageEndDate FROM Asset WHERE SerialNumber=\'%s\' AND AccountId=\'%s\'"%(serialNumber,acc))
		if len(asset['records'])==0:
			return "NotFound"
		asset_id = asset['records'][0]['Id']
		PurchaseDate = asset['records'][0]['PurchaseDate']
		InstallDate = asset['records'][0]['InstallDate']
		UsageEndDate = asset['records'][0]['UsageEndDate']
		self.sf.Asset.update(asset_id,{
			'Returned__c':True
			})

		asset1 = self.sf.query("SELECT Id, Description FROM Asset WHERE AccountId=\'%s\'"%acc)
		for desc in asset1['records']:
			if desc['Description'] is not None and "SO-" not in desc['Description']:
				asset1_id = desc['Id']
				self.sf.Asset.update(asset1_id,{
					'PurchaseDate':PurchaseDate,
					'InstallDate':InstallDate,
					'UsageEndDate':UsageEndDate
					})
				break
		return asset1


	def fetchSerialNumberFromSFDC(self, acc, supp, pType):
		supp_ticket = 'SUPP-'+str(supp)+'%'
		serialNumbers = []
		assets = self.sf.query("SELECT SerialNumber, Name FROM Asset WHERE AccountId=\'%s\' "%(acc))
		for asset in assets['records']:
			if pType in asset['Name']:
				serialNumbers.append(asset['SerialNumber'])
		
		return serialNumbers









