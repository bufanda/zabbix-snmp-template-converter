#####
# Thorsten Liepert
# Feb 2025
#
#####

import yaml

with open("template.yml", "r") as inputf:
    input = yaml.safe_load(inputf)

for item in input["zabbix_export"]:
    if item == "version":
        if input["zabbix_export"][item] == "7.0":
            continue
        else:
            print("Not uspported")
            exit(-1)

for template in input["zabbix_export"]["templates"]:
    for item in template["items"]:
        if item["type"] == "SNMP_AGENT":
            item.update({"snmp_oid": "get[" + item["snmp_oid"] + "]"})
            print(item["snmp_oid"])

    for discovery in template["discovery_rules"]:
        item_prototypes = discovery["item_prototypes"]
        for prototype in item_prototypes:
            if prototype["type"] == "SNMP_AGENT":
                prototype.update({"snmp_oid": "get[" + prototype["snmp_oid"] +"]"})

print(input)
