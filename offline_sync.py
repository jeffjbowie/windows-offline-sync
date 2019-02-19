#! /usr/bin/env python3 

""" 

Pings an internal address to see if faster, local servers are available
GET request to URL to create ZIPs using an NTLM-authenticated Session
Unzip archives to %USERPROFILE%\\Offline

"""

import requests
from requests_ntlm import HttpNtlmAuth
import zipfile
import os
from clint.textui import progress

# makes zipfile lib extract to folders 
os.path.altsep = '\\'

OFFLINE_FOLDER = os.environ['USERPROFILE']+ "\\Offline"
INTERNAL_HOST = "192.168.1.100"
EXTERNAL_HOST = 'external.host'
NTLM_ACCOUNT = 'administrator'
NTLM_PASSWORD = 'Password1'

def download_file(session, url):
    local_filename = url.split('/')[-1]
    head = session.head(url)
    file_size_bytes = int(head.headers['Content-Length'])
    
    print("\n\t> {0} - {1} MB:".format( local_filename, int(file_size_bytes/(1024 * 1024))))

    with session.get(url, stream=True) as r:
        if r.status_code == 200:
            with open(local_filename, 'wb') as f:
                # 512 byte chunks
                for chunk in progress.bar(r.iter_content(chunk_size=512), expected_size=(file_size_bytes/512) + 1): 
                    if chunk:
                        f.write(chunk)
            return local_filename
        else:
            assert("!!! Failed to download {0}".format(url))

print("\n*** Offline Sync")

# Remove old zip.
if os.path.isfile('data.zip'): os.remove('data.zip')

# for Windows 
ping_response = os.system("ping -n 1 -w 2 " + INTERNAL_HOST + " > NUL")

#0 means success
if ping_response == 0:
	host = INTERNAL_HOST
	protocol = 'http'
	port = 80
	print("*** Network: Internal")
else:
	host = EXTERNAL_HOST
	protocol = 'https'
	port = 443
	print("*** Network: External")

session = requests.Session()
session.auth = HttpNtlmAuth(NTLM_ACCOUNT, NTLM_PASSWORD)

print("*** Creating new recordset...")

response = session.get('{0}://{1}:{2}/offline_export'.format(protocol,host,port))
if response.status_code == 200:

	print("*** Downloading...")

	data_zip_dl =  download_file(session, '{0}://{1}:{2}/data.zip'.format(protocol,host,port))

	if os.path.isfile(data_zip_dl):
		print("\n*** Extracting files...")
		data_zip = zipfile.ZipFile(data_zip_dl)
		data_zip.extractall(OFFLINE_FOLDER)
		
	print("*** Synchronization complete.")


