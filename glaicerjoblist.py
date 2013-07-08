#!/usr/bin/env python
import boto
import json
import sys
ACCESS_KEY_ID = "xxx"
SECRET_ACCESS_KEY = "xxx"

# boto.connect_glacier is a shortcut return a Layer2 instance 
glacier_connection = boto.connect_glacier(aws_access_key_id=ACCESS_KEY_ID,
                                    aws_secret_access_key=SECRET_ACCESS_KEY)


inventjobid = 0
inventaskedfor = 0
inventjobid =""
job_data = {'Type': 'inventory-retrieval'}

valutnname=str(sys.argv[1])

def requestinvent():
 job_id = glacier_connection.layer1.initiate_job(valutnname, job_data)
 print "Inventory has been asked for with jobid "+str(job_id['JobId'])

def delallarchives():
 vault = glacier_connection.create_vault(valutnname)
 job = vault.get_job(inventjobid)
 jobout = job.get_output()
 testlen = jobout['ArchiveList']
 numberofarchives =  len(testlen)
 for x in range (0, numberofarchives):
  result = jobout['ArchiveList'][x]['ArchiveId']
  vault.delete_archive(result)
  print "ArchiveID "+result+" deleted"


#try to delete valut
try:
 blah = glacier_connection.layer1.delete_vault(valutnname)
 print "Congratulations! "+valutnname+" no longer exists (or it never existed)!"
except:
 print "Tried to delete the vault but unable to so attempting to clear the vault"

 job_id = glacier_connection.layer1.list_jobs(valutnname)
 joblist = job_id["JobList"]
 numberofjobs =  len(joblist)
 for x in range (0, numberofjobs):
  if joblist[x]['Action']=="InventoryRetrieval":
   inventaskedfor = True
   if joblist[x]['Completed']:
    inventjobid = joblist[x]['JobId']
    print "Found valid inventory with job id "+inventjobid
    break



 if inventaskedfor and inventjobid:
  print "Inventory found and reterived. Now deleting all archives in valut."
  delallarchives()
  requestinvent()
  print "Archives have been deleted and new inventory asked for. You must wait until the new inventory has been created before you can delete the valut (a new inventory is created only once every 24 hours)."
 elif (inventaskedfor): 
  print "Please wait. Inventory job is still in reterival (usually takes 3-5 hours)."
 else:
  print "No inventory job has been run recently enough. Running..." 
  requestinvent()
 
 