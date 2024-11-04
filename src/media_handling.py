import os
from urllib.parse import urlparse

scheme = ''
source_dir = ''
media_dir = ''
mount_point = '/mnt'

def mount_source(url):
    global schema, source_dir
    u = urlparse
    scheme = u.scheme
    if scheme == 'nfs':
        os.system(f"mount -o nolock {u.hostname}:{u.path} {mount_point}")
    elif scheme == 'smb':
        mopts = '-o ro'
        if u.username != None:
	    mopts = f"-o ro,user={u.username},password={u.password}"
	os.system(f"/sbin/mount.cifs '//{u.hostname}/{u.path}' {mount_point} {mopts}")
    else:
        print("Not supported scheme {scheme}")
	    
        
