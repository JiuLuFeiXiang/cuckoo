# Copyright (C) 2013 Claudio Guarnieri.
# Copyright (C) 2014-2017 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import json
import pymongo

from cuckoo.common.mongo import mongo
from cuckoo.processing import network

results_db = mongo.db
fs = mongo.grid

def pcapstream(request, task_id, proto, src, sport, dst, dport):
    sport, dport = int(sport), int(dport)

    conndata = results_db.analysis.find_one(
        {
            "info.id": int(task_id),
        },
        {
            "network.tcp": 1,
            "network.udp": 1,
            "network.sorted_pcap_id": 1,
        },
        sort=[("_id", pymongo.DESCENDING)])

    if not conndata:
        return request + "\nThe specified analysis does not exist"

    try:
        if proto == "udp":
            connlist = conndata["network"]["udp"]
        else:
            connlist = conndata["network"]["tcp"]

        conns = filter(lambda i: (i["sport"], i["dport"], i["src"], i["dst"]) == (sport, dport, src, dst), connlist)
        stream = conns[0]
        offset = stream["offset"]
    except:
        return request +  "\nCould not find the requested stream"

    try:
        fobj = fs.get(conndata["network"]["sorted_pcap_id"])
        setattr(fobj, "fileno", lambda: -1)
    except:
        return "The required sorted PCAP does not exist"

    packets = list(network.packets_for_stream(fobj, offset))
    return json.dumps(packets)
