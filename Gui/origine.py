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
#print(import_result['topology']['_085E1F732997474DB28FAF265F73C643'].__dict__.keys())
#print(import_result['topology']['_5DDCA8884C7E4EC8965F9A4295976A5E'].__dict__['SvStatus'][1].__dict__["mRID"])
print(import_result['topology']['_46A3B0F6ED5E4146B99E10075C579C31'].__dict__["TopologicalNode"])
for v in import_result['topology']['_46A3B0F6ED5E4146B99E10075C579C31'].__dict__["TopologicalNode"]:

    print(v.__dict__)
#class_attributes_list=cimpy.cimexport._get_class_attributes_with_references(import_result,cgmesver)
#eq_classes_list = cimpy.cimexport._sort_classes_to_profile(class_attributes_list, ['EQ'])[0]['EQ']['classes']

        
# region add properties to input data otherwise it wont work in PF 
cimpy.sincal_Pf(import_result)
# endregion
# region export cim
# 'SSH','EQ',  'TP', 'SV', 'GL', 'DL','DY'
activeProfileList = ['EQ', 'TP', 'SV', 'DY', 'SSH']
for filename12 in glob.glob("./ExportedData/Ausgabe*"):
    os.remove(filename12)
#cimpy.cim_export(import_result, output_dir+"/output", "cgmes_v2_4_15", activeProfileList)