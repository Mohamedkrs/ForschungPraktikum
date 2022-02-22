import importlib
import os, glob
import logging
import cimpy
from pathlib import Path


logging.basicConfig(filename='importCIGREMV.log', level=logging.INFO, filemode='w')
#### Parse importedXml Files ###

example = Path(".\importedData").resolve()
xml_files = []
for file in example.glob('*.xml'):
    xml_files.append(str(file.absolute()))

cgmesver = "cgmes_v2_4_15"
import_result = cimpy.cim_import(xml_files, cgmesver)
#if "EQ" in import_result['meta_info']['profiles'].keys():
#    print("yay")
#class_attributes_list = cimpy.cimexport._get_class_attributes_with_references(import_result, cgmesver)
#test = cimpy.cimexport._sort_classes_to_profile(class_attributes_list, ['EQ'])
print(import_result['meta_info'])

#print(import_result['topology'])
for key, val in import_result["topology"].items():
    if "EnergySource"  == import_result["topology"][key].__class__.__name__:
        elemMrid=key
        EquipmentContainer = import_result["topology"][key].__dict__["EquipmentContainer"]
        name = import_result["topology"][key].__dict__["name"]
        shortName = import_result["topology"][key].__dict__["shortName"]
        description = import_result["topology"][key].__dict__["description"]
        externalGrid_module = importlib.import_module('cimpy.cgmes_v2_4_15.'+'ExternalNetworkInjection')
        externalGrid_class = getattr(externalGrid_module,'ExternalNetworkInjection')
        externalGrid_class.serializationProfile = {
        'class':'EQ', 'p':'SSH', 'q':'SSH',
        'referencePriority':'SSH', 'controlEnabled':'SSH',
        'EquipmentContainer':'EQ', 'governorSCD':'EQ',
        'maxP':'EQ','maxQ':'EQ',
        'maxR0ToX0Ratio':'EQ','maxR1ToX1Ratio':'EQ',
        'maxZ0ToZ1Ratio':'EQ', 'minInitialSymShCCurrent':'EQ',
        'minP':'EQ', 'minQ':'EQ', 'minR0ToX0Ratio':'EQ',
        'minR1ToX1Ratio':'EQ', 'minZ0ToZ1Ratio':'EQ',
        'name':'EQ','RegulatingControl':'EQ' }
        import_result["topology"][key] = externalGrid_class(mRID=elemMrid,
                                                            name=name,
                                                            EquipmentContainer=EquipmentContainer, shortName=shortName, description=description,
                                                            maxP = 10.0, maxQ = 20.0)
        #print(name)
#print(import_result['topology']["_1D6B7D84BCC44B589D479560B2514A0E"].__dict__)
#for v in import_result['topology']['_46A3B0F6ED5E4146B99E10075C579C31'].__dict__["TopologicalNode"]:
externalGrid_module = importlib.import_module('cimpy.cgmes_v2_4_15.'+'ExternalNetworkInjection')
externalGrid_class = getattr(externalGrid_module,'ExternalNetworkInjection')
import_result["topology"]["hello"] = externalGrid_class(mRID="elemMrid",
                                                    maxP = 10.0, maxQ = 20.0)
#print(import_result['topology']["hello"].__dict__)
 #   print(v.__class__.__name__)
#class_attributes_list=cimpy.cimexport._get_class_attributes_with_references(import_result,cgmesver)
#eq_classes_list = cimpy.cimexport._sort_classes_to_profile(class_attributes_list, ['EQ'])[0]['EQ']['classes']

        
# region add properties to input data otherwise it wont work in PF 
#cimpy.sincal_Pf(import_result)
# endregion
# region export cim
# 'SSH','EQ',  'TP', 'SV', 'GL', 'DL','DY'
activeProfileList = ['EQ', 'TP', 'SV', 'DY', 'SSH']
for filename12 in glob.glob("./ExportedData/*"):
    os.remove(filename12)
cimpy.cim_export(import_result, "./ExportedData/", "cgmes_v2_4_15", activeProfileList)