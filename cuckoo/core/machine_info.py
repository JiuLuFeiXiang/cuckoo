import os
import psutil
import datetime
import pymongo
import sched, time
import logging
from cuckoo.common.config import config

log = logging.getLogger(__name__)

user = ""
password = ""
hostname = ""
port = ""
database = ""
time_format = "%d/%m/%Y"

s = sched.scheduler(time.time, time.sleep)

client = pymongo.MongoClient(hostname, port)
db = client[database]    

if user and password:
    db.authenticate(user, password)
else:
    log.error("Wrong password")

status = db['machine_status']

def machine_status():
    # cpu
    cpu_percent = psutil.cpu_percent(interval=1)

    # memory
    m = psutil.virtual_memory()
    memory = {}
    # memory['total'] = m[0]
    memory['available'] = m[1]
    memory['used'] = m[3]
    memory['free'] = m[4]
    memory['active'] = m[5]
    memory['inactive'] = m[6]
    memory['buffers'] = m[7]
    memory['cached'] = m[8]
    memory['shared'] = m[9]

    memory_total = m[0]
    # disk_usage
    try:
        path = '/'
        d = psutil.disk_usage(path) # only get /dev/sda1
        disk = {}
        # disk['total'] = d[0]
        disk['used'] = d[1]
        disk['free'] = d[2]
        disk_total = d[0]
    except OSError:
        log.warning('Path %s not exist' % path)

    # network
    interface = {}
    io_counters = psutil.net_io_counters(pernic=True)
    for nic in io_counters.keys():
        if nic == 'lo':
            continue

        interface[nic] = {}
        io = io_counters[nic]
        interface[nic]['transfer'] = {
            'outgoing': io.bytes_sent,
            'incoming': io.bytes_recv,
        }
        interface[nic]['packet'] = {
            'packets_receive': io.packets_recv,
            'packets_sent': io.packets_sent
        }

    # last boot time
    last_boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

    return (cpu_percent, memory, disk, interface, last_boot_time, memory_total, disk_total)

def log_machine_status(sc): 
    print "Saving status to mongodb..."

	# do stuff
    currentTime = datetime.datetime.today()
    currentTimeFormated = currentTime.strftime(time_format)

    # filled data should be ready
    tmp = machine_status()
    status_inserted = {
        "cpu_percent": {
            currentTime.strftime("%H:%M"): tmp[0]
        },
        "memory": tmp[1],
        "disk": tmp[2],
        "network": tmp[3],
        "last_boot_time": tmp[4],
        "memory_total": tmp[5],
        "disk_total": tmp[6],
        "date": currentTimeFormated
    }
    
    status_updated = {
        "cpu_percent." + currentTime.strftime("%H:%M"): tmp[0],
        "memory": tmp[1],
        "disk": tmp[2],
        "network": tmp[3],
        "last_boot_time": tmp[4],
        "memory_total": tmp[5],
        "disk_total": tmp[6],
        "date": currentTimeFormated       
    }

    # create new document every new day
    latest_object_cursor = status.find({}, sort=[('date', pymongo.DESCENDING)]).limit(1)

    if not latest_object_cursor.count(True) or latest_object_cursor[0]['date'] != currentTimeFormated:
        status.insert_one(status_inserted)
    else:
        status.find_one_and_update(
        {
            '_id': latest_object_cursor[0]['_id']
        },
        {
            '$set': status_updated
        },
        upsert=True)

    # end do stuff
    
    s.enter(60, 1, log_machine_status, (sc,))

def Machine_info_main():
    
    # Set timezone
    os.environ['TZ'] = 'Asia/Ho_Chi_Minh'
    time.tzset()

    s.enter(0, 1, log_machine_status, (s,))
    s.run()