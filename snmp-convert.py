#####
# Thorsten Liepert
# Feb 2025
#
#####

import ruamel.yaml as YAML
import uuid
import argparse
import sys

yaml = YAML.YAML()

ARG_PARSER = argparse.ArgumentParser(description="default parser")
ARG_PARSER.add_argument("-t", "--template", type=str, required=True, help="Esported Template to convert" )
ARG_PARSER.add_argument("-o", "--output", type=str, required=False, help="Output file name")
ARG_PARSER.add_argument("-d", "--dryrun", action="store_true", required=False, help="Only output to shell do not safe file")

if len(sys.argv) < 1:
    ARG_PARSER.print_help()
    sys.exit(1)
else:
    args = ARG_PARSER.parse_args()

input_file = args.template
output_file = args.output
dryrun = args.dryrun

with open(input_file, "r") as inputf:
    # input = yaml.safe_load(inputf)
    input = yaml.load(inputf)


for item in input["zabbix_export"]:
    if item == "version":
        if input["zabbix_export"][item] == "7.0":
            continue
        else:
            print("Not uspported")
            exit(-1)

for template in input["zabbix_export"]["templates"]:

    old_name = template["name"]
    template["name"] = f"{template['name']} asynchron"
    template["template"] = f"{template['template']} asynchron"
    template["uuid"] = uuid.uuid4().hex
    if "items" in template:
        for item in template["items"]:
            if item["type"] == "SNMP_AGENT":
                if "get[" not in item["snmp_oid"]:
                    item.update({"snmp_oid": "get[" + item["snmp_oid"] + "]"})
            if "triggers" in item:
                for triggers in item["triggers"]:
                    if old_name in triggers["expression"]:
                        triggers["expression"] = triggers["expression"].replace(old_name, template["template"])
                    triggers["uuid"] = uuid.uuid4().hex
                if "dependencies" in triggers:
                    for dependency in triggers["dependencies"]:
                        # dependency["uuid"] = uuid.uuid4().hex
                        if old_name in dependency["expression"]:
                            dependency["expression"]  = dependency["expression"].replace(old_name, template["template"])

            item["uuid"] = uuid.uuid4().hex

    if "triggers" in template:
        for triggers in template["triggers"]:
            if old_name in triggers["expression"]:
                triggers["expression"]  = triggers["expression"].replace(old_name, template["template"])
            triggers["uuid"] = uuid.uuid4().hex
            if "dependencies" in triggers:
                for dependency in triggers["dependencies"]:
                    if old_name in dependency["expression"]:
                        dependency["expression"] = dependency["expression"].replace(old_name, template["template"])

    if "discovery_rules" in template:
        for discovery in template["discovery_rules"]:
            item_prototypes = discovery["item_prototypes"]
            for prototype in item_prototypes:
                if prototype["type"] == "SNMP_AGENT":
                    if "get[" not in prototype["snmp_oid"]:
                        prototype.update({"snmp_oid": "get[" + prototype["snmp_oid"] +"]"})
                prototype["uuid"] = uuid.uuid4().hex
                if "trigger_prototypes" in prototype:
                    for triggers in prototype["trigger_prototypes"]:
                        if old_name in triggers["expression"]:
                            triggers["expression"]  = triggers["expression"].replace(old_name, template["template"])
                        triggers["uuid"] = uuid.uuid4().hex
                        if "dependencies" in triggers:
                            for dependency in triggers["dependencies"]:
                                if old_name in dependency["expression"]:
                                    dependency["expression"] = dependency["expression"].replace(old_name, template["template"])

            discovery["uuid"] = uuid.uuid4().hex

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

    if "valuemaps" in template:
        for valuemap in template["valuemaps"]:
            valuemap["uuid"] = uuid.uuid4().hex

if not dryrun:
    if not output_file:
        output_file = "converted_template.yml"
    with open(output_file, "w", encoding=sys.getfilesystemencoding()) as output:
        yaml.dump(input,output)
else:
    yaml.dump(input, sys.stdout)
