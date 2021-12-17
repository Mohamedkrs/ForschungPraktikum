from collections import Counter

import cimpy


class ManageElements:
    cgmesver = "cgmes_v2_4_15"
    #elems={}
    def __init__(self):
        self.elements = {}
        self.profile_elements = {}
        self.data = []

    def import_eq_data(self, profile):

        if self.elements:
            self.elements.clear()
        try:
            class_attributes_list = cimpy.cimexport._get_class_attributes_with_references(self.data, self.cgmesver)
            eq_classes_list = cimpy.cimexport._sort_classes_to_profile(class_attributes_list, [profile])[0][profile][
                'classes']
        except:
            eq_classes_list = self.data
            
        for _class in eq_classes_list:
            if _class['mRID'] not in self.elements.values():
                if _class['name'] not in self.elements.keys():
                    self.elements[_class['name']] = _class['mRID']
                    i = 1
                else:
                    self.elements[_class['name'] + " " + str(i)] = _class['mRID']
                    i += 1
        self.profile_elements[profile] = dict(self.elements)
        return self.elements.keys()

    def filter_data(self, elemName='', elemProp='', detail='', elem_andor_prop='', prop_andor_elem=''):
        filtered_elements = {}
        elem_name_dict = {}
        prop_dict = {}
        detail_dict = {}
        for key, val in self.elements.items():
            if elemName != '':
                if elemName.lower() in key.lower():
                    elem_name_dict[key] = val
            if elemProp != '':
                for k in self.data["topology"][val].__dict__.keys():
                    if elemProp.lower() in k.lower():
                        prop_dict[key] = val
                        break
            if detail != '':
                for v in self.data["topology"][val].__dict__.values():
                    if isinstance(v, (str, int, float, bool)):
                        if detail.lower() in str(v).lower():
                            detail_dict[key] = val
                            break

        if elem_andor_prop == "and" and prop_andor_elem == "and":
            if set(elem_name_dict.keys()) & set(prop_dict.keys()) & set(detail_dict.keys()):
                for item in set(detail_dict.keys()) & set(prop_dict.keys()):
                    filtered_elements[item] = self.elements[item]
        elif elem_andor_prop == "and":
            if set(elem_name_dict.keys()) & set(prop_dict.keys()):
                for item in set(elem_name_dict.keys()) & set(prop_dict.keys()):
                    filtered_elements[item] = self.elements[item]
        elif prop_andor_elem == "and":
            if set(detail_dict.keys()) & set(prop_dict.keys()):
                for item in set(detail_dict.keys()) & set(prop_dict.keys()):
                    filtered_elements[item] = self.elements[item]
        else:
            filtered_elements = {**elem_name_dict, **prop_dict, **detail_dict}
        return filtered_elements.keys()
