import sys
import collections
import os, os.path, re
import io
from lxml import etree

"""
count tlink output of a system
"""

rel_type_dict = collections.defaultdict(list)


def get_data(sys1_out):

    """
     sys1 data
    """

    doc_sys1 = etree.parse(sys1_out, etree.XMLParser(remove_blank_text=True))
    root_sys1 = doc_sys1.getroot()
    root_sys1.getchildren()

#    doc_name = sys1_out.split("/")[-1]

    global rel_type_dict

    for elem in root_sys1.findall("TLINK"):
        tlink_type = elem.get('relType', 'null')

        if tlink_type == "BEFORE":
            rel_type_dict["BEFORE"].append(tlink_type)
        if tlink_type == "AFTER":
            rel_type_dict["AFTER"].append(tlink_type)
        if tlink_type == "BEGUN_BY":
            rel_type_dict["BEGUN_BY"].append(tlink_type)
        if tlink_type == "DURING":
            rel_type_dict["DURING"].append(tlink_type)
        if tlink_type == "IAFTER":
            rel_type_dict["IAFTER"].append(tlink_type)
        if tlink_type == "IBEFORE":
            rel_type_dict["IBEFORE"].append(tlink_type)
        if tlink_type == "IS_INCLUDED":
            rel_type_dict["IS_INCLUDED"].append(tlink_type)
        if tlink_type == "INCLUDES":
            rel_type_dict["INCLUDES"].append(tlink_type)
        if tlink_type == "SIMULTANEOUS":
            rel_type_dict["SIMLUTANEOUS"].append(tlink_type)
        if tlink_type == "DURING_INV":
            rel_type_dict["DURING_INV"].append(tlink_type)
        if tlink_type == "BEGINS":
            rel_type_dict["BEGINS"].append(tlink_type)
        if tlink_type == "ENDS":
            rel_type_dict["ENDS"].append(tlink_type)
        if tlink_type == "IDENTITY":
            rel_type_dict["IDENTITY"].append(tlink_type)


    for k, v in rel_type_dict.iteritems():
        print k, len(v)


def contingent_matrix_event(sys1dir):

    for f in os.listdir(sys1dir):

        if f.endswith(".tml"):
            get_data(sys1dir + f)
        else:
            print("Error - missing data: ") + f


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print 'Usage: python compare_system_tlink1.py sys1 '
    else:
        contingent_matrix_event(argv[1])

if __name__ == '__main__':
    main()