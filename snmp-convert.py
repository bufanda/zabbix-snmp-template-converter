#####
# Thorsten Liepert
# Feb 2025
#
#####

import ruamel.yaml as YAML

yaml = YAML.YAML()

with open("template.yml", "r") as inputf:
    input = yaml.load(inputf)

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
            if "get[" not in item["snmp_oid"]:
                item.update({"snmp_oid": "get[" + item["snmp_oid"] + "]"})

    for discovery in template["discovery_rules"]:
        item_prototypes = discovery["item_prototypes"]
        for prototype in item_prototypes:
            if prototype["type"] == "SNMP_AGENT":
                if "get[" not in prototype["snmp_oid"]:
                    prototype.update({"snmp_oid": "get[" + prototype["snmp_oid"] +"]"})

    for rule in template["discovery_rules"]:
        macros = []
        oids = []
        preprocessing = []
        if rule["type"] == "SNMP_AGENT":
            if "discovery[" in rule["snmp_oid"]:
                oids_macros = rule["snmp_oid"][len("discovery["):-1]
                oids_macros = str.split(oids_macros, ",")

                for index,value in enumerate(oids_macros):
                    if index%2 == 0:
                        macros.append(value)
                    else:
                        oids.append(value)
                rule["snmp_oid"] = "walk[" + str.join(",", oids) + "]"
                pp = {
                    "type": "SNMP_WALK_TO_JSON",
                    "parameters": []
                }
                for index,value in enumerate(macros):
                    pp["parameters"].append(value)
                    pp["parameters"].append(oids[index])
                    pp["parameters"].append('0')
                preprocessing.append(pp)
            if "preprocessing" in rule:
                rule["preprocessing"] = rule["preprocessing"] + preprocessing
            else:
                rule.update({"preprocessing": preprocessing})


with open("converted_template.yml", "w") as output:
    yaml.dump(input,output)
