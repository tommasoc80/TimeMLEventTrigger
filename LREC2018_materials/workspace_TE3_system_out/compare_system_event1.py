import sys
import collections
import os, os.path, re
import io
from lxml import etree

"""
compare 2 system outputs
"""


def get_data(sys1_out, sys2_out, outdir):

    """
     sys1 data
    """

    doc_sys1 = etree.parse(sys1_out, etree.XMLParser(remove_blank_text=True))
    root_sys1 = doc_sys1.getroot()
    root_sys1.getchildren()

    doc_name = root_sys1.get('doc_name', 'null')

    dict_event_extent_sys1 = {}
    dict_event_class_sys1 = {}
    token_text = {}

    for elem in root_sys1.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys1[doc_name + "\t" + token_id] = event_id
            dict_event_class_sys1[doc_name + "\t" + token_id] = event_class


    for elem in root_sys1.findall('token'):
        token_id = elem.get('t_id', 'null')
        token = elem.text
        token_text[doc_name + "\t" + token_id] = token


    """
     sys2 data
    """


    doc_sys2 = etree.parse(sys2_out, etree.XMLParser(remove_blank_text=True))
    root_sys2 = doc_sys2.getroot()
    root_sys2.getchildren()

    doc_name2 = root_sys2.get('doc_name', 'null')

    dict_event_extent_sys2 = {}
    dict_event_class_sys2 = {}

    for elem in root_sys2.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys2[doc_name2 + "\t" + token_id] = event_id
            dict_event_class_sys2[doc_name2 + "\t" + token_id] = event_class


    """
    get common events and not in common
    """

    for k, v in dict_event_extent_sys1.iteritems():
        if k in dict_event_extent_sys2:
#            if k == k1:
            print k, token_text[k]

            text_file = io.open(outdir + "common_extent", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" +  token_text[k]) + "\n")
            text_file.close()

        if k not in dict_event_extent_sys2:
            text_file = io.open(outdir +  "different_extent", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" + token_text[k]) + "\n")
            text_file.close()

    """
    get same events - same class and same event - different class
    """


    for k, v in dict_event_class_sys1.iteritems():
        if k in dict_event_extent_sys2:
            if k in dict_event_class_sys2:
                if v == dict_event_class_sys2[k]:
#                    print k, token_text[k], v, dict_event_class_sys2[k]
                    text_file = io.open(outdir + "common_same_class", "a", encoding="utf-8")
                    text_file.write(unicode(k + "\t" + token_text[k]) + "\n")
                    text_file.close()

        if k in dict_event_class_sys2:
            if v != dict_event_class_sys2[k]:
                text_file = io.open(outdir + "common_different_class", "a", encoding="utf-8")
                text_file.write(unicode(k + "\t" + token_text[k]) + "\n")
                text_file.close()


def contingent_matrix_event(sys1dir, sys2dir, outdir):

    for f in os.listdir(sys1dir):
        sys2f = sys2dir + f

        if f.endswith(".xml"):
#            outfile = outdir + f
#            get_data(sys1dir + f, sys2f, outfile)
            get_data(sys1dir + f, sys2f, outdir)
        else:
            print("Error - missing data: ") + f


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 4:
        print 'Usage: python compare_system_event1.py sys1 sys2 outdir'
    else:
        contingent_matrix_event(argv[1], argv[2], argv[3])

if __name__ == '__main__':
    main()