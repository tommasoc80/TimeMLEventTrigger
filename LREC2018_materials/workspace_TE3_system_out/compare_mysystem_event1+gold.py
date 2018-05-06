import sys
import collections
import os, os.path, re
import io
from lxml import etree


"""
compare system output for event detection and classification against the gold
"""


def get_data(sys1_out, gold_data, outdir):

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
    gold data
    """

    doc_gold = etree.parse(gold_data, etree.XMLParser(remove_blank_text=True))
    root_gold = doc_gold.getroot()
    root_gold.getchildren()

    doc_gold = root_gold.get('doc_name', 'null')

    dict_event_extent_gold = {}
    dict_event_class_gold = {}

    for elem in root_gold.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_gold[doc_gold + "\t" + token_id] = event_id
            dict_event_class_gold[doc_gold + "\t" + token_id] = event_class

    """
    get common events and not in common
    """

#    for k, v in token_text.iteritems():
#        print k, v

    for k, v in dict_event_extent_gold.iteritems():
#        print k, v

        if k in dict_event_extent_sys1:
            text_file = io.open(outdir + "common_gold_extent", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" +  token_text[k]) + "\n")
            text_file.close()

        if not k in dict_event_extent_sys1:
            text_file = io.open(outdir +  "missing_common_extent", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" + token_text[k]) + "\n")
            text_file.close()

    """
    get same events - same class and same event - different class
    """


    for k, v in dict_event_class_gold.iteritems():

        if k in dict_event_class_sys1:
            if v == dict_event_class_sys1[k]:
                text_file = io.open(outdir + "common_gold_class", "a", encoding="utf-8")
                text_file.write(unicode(k + "\t" + token_text[k] + "\t" + v + "\t" + dict_event_class_sys1[k]) + "\n")
                text_file.close()

        if k in dict_event_class_sys1:
            if v != dict_event_class_sys1[k]:
                text_file = io.open(outdir + "common_different_class", "a", encoding="utf-8")
                text_file.write(unicode(k + "\t" + token_text[k] + "\t" + v + "\t" + dict_event_class_sys1[k]) + "\n")
                text_file.close()


def contingent_matrix_event(sys1dir, gold_dir, outdir):

    for f in os.listdir(sys1dir):
        goldf = gold_dir + f

        if f.endswith(".xml"):
#            outfile = outdir + f
#            get_data(sys1dir + f, sys2f, outfile)
            get_data(sys1dir + f, goldf, outdir)
        else:
            print("Error - missing data: ") + f


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 5:
        print 'Usage: python compare_system_event1.py sys1 gold outdir'
    else:
        contingent_matrix_event(argv[1], argv[2], argv[3], argv[4])

if __name__ == '__main__':
    main()