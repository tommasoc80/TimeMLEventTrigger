import sys
import collections
import os, os.path, re
import io
from lxml import etree

"""
compare outputs for event detection and classifcation of all systems againts the gold
"""


def get_data(gold_data, sys1_out, sys2_out, sys3_out, sys4_out, sys5_out, sys6_out, sys7_out, outdir):

    """
    gold data
    """

    doc_gold = etree.parse(gold_data, etree.XMLParser(remove_blank_text=True))
    root_gold = doc_gold.getroot()
    root_gold.getchildren()

    doc_gold = root_gold.get('doc_name', 'null')

    dict_event_extent_gold = {}
    dict_event_class_gold = {}
    token_text = {}


    for elem in root_gold.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_gold[doc_gold + "\t" + token_id] = event_id
            dict_event_class_gold[doc_gold + "\t" + token_id] = event_class

    for elem in root_gold.findall('token'):
        token_id = elem.get('t_id', 'null')
        token = elem.text
        token_text[doc_gold + "\t" + token_id] = token

#    for k, v in dict_event_class_gold.iteritems():
#        print k, v

    """
     sys1 data
    """

    doc_sys1 = etree.parse(sys1_out, etree.XMLParser(remove_blank_text=True))
    root_sys1 = doc_sys1.getroot()
    root_sys1.getchildren()

    doc_name = root_sys1.get('doc_name', 'null')

    dict_event_extent_sys1 = {}
    dict_event_class_sys1 = {}

    for elem in root_sys1.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys1[doc_name + "\t" + token_id] = event_id
            dict_event_class_sys1[doc_name + "\t" + token_id] = event_class

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
     sys3 data
    """

    doc_sys3 = etree.parse(sys3_out, etree.XMLParser(remove_blank_text=True))
    root_sys3 = doc_sys3.getroot()
    root_sys3.getchildren()

    doc_name3 = root_sys3.get('doc_name', 'null')

    dict_event_extent_sys3 = {}
    dict_event_class_sys3 = {}

    for elem in root_sys3.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys3[doc_name3 + "\t" + token_id] = event_id
            dict_event_class_sys3[doc_name3 + "\t" + token_id] = event_class

    """
     sys4 data
    """

    doc_sys4 = etree.parse(sys4_out, etree.XMLParser(remove_blank_text=True))
    root_sys4 = doc_sys4.getroot()
    root_sys4.getchildren()

    doc_name4 = root_sys4.get('doc_name', 'null')

    dict_event_extent_sys4 = {}
    dict_event_class_sys4 = {}

    for elem in root_sys4.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys4[doc_name4 + "\t" + token_id] = event_id
            dict_event_class_sys4[doc_name4 + "\t" + token_id] = event_class

    """
     sys5 data
    """

    doc_sys5 = etree.parse(sys5_out, etree.XMLParser(remove_blank_text=True))
    root_sys5 = doc_sys5.getroot()
    root_sys5.getchildren()

    doc_name5 = root_sys5.get('doc_name', 'null')

    dict_event_extent_sys5 = {}
    dict_event_class_sys5 = {}

    for elem in root_sys5.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys5[doc_name5 + "\t" + token_id] = event_id
            dict_event_class_sys5[doc_name5 + "\t" + token_id] = event_class

    """
     sys6 data
    """

    doc_sys6 = etree.parse(sys6_out, etree.XMLParser(remove_blank_text=True))
    root_sys6 = doc_sys6.getroot()
    root_sys6.getchildren()

    doc_name6 = root_sys6.get('doc_name', 'null')

    dict_event_extent_sys6 = {}
    dict_event_class_sys6 = {}

    for elem in root_sys6.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys6[doc_name6 + "\t" + token_id] = event_id
            dict_event_class_sys6[doc_name6 + "\t" + token_id] = event_class

    """
     sys7 data
    """

    doc_sys7 = etree.parse(sys7_out, etree.XMLParser(remove_blank_text=True))
    root_sys7 = doc_sys7.getroot()
    root_sys7.getchildren()

    doc_name7 = root_sys7.get('doc_name', 'null')

    dict_event_extent_sys7 = {}
    dict_event_class_sys7 = {}

    for elem in root_sys7.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys7[doc_name7 + "\t" + token_id] = event_id
            dict_event_class_sys7[doc_name7 + "\t" + token_id] = event_class

    """
    events extents per system
    """

    event_extent = collections.defaultdict(list)

    for k, v in dict_event_extent_gold.iteritems():

        if k in dict_event_extent_sys1:
            event_extent[k].append(int(1))
        else:
            event_extent[k].append(int(0))

        if k in dict_event_extent_sys2:
            event_extent[k].append(int(1))
        else:
            event_extent[k].append(int(0))

        if k in dict_event_extent_sys3:
            event_extent[k].append(int(1))
        else:
            event_extent[k].append(int(0))

        if k in dict_event_extent_sys4:
            event_extent[k].append(int(1))
        else:
            event_extent[k].append(int(0))

        if k in dict_event_extent_sys5:
            event_extent[k].append(int(1))
        else:
            event_extent[k].append(int(0))

        if k in dict_event_extent_sys6:
            event_extent[k].append(int(1))
        else:
            event_extent[k].append(int(0))

        if k in dict_event_extent_sys7:
            event_extent[k].append(int(1))
        else:
            event_extent[k].append(int(0))

    event_extent_tokens_gold_systems = {}

    for k, v in event_extent.iteritems():
        if k in token_text:
            event_extent_tokens_gold_systems[k + "\t" + token_text[k]] = sum(v)


    """
    event class per event per system
    """


    event_class = collections.defaultdict(list)

    for k, v in dict_event_class_gold.iteritems():

        if k in dict_event_class_sys1:
            if dict_event_class_sys1[k] == v:
                event_class[k + "\t" + v].append(int(1))
            else:
                event_class[k + "\t" + v].append(int(0))

        if k in dict_event_class_sys2:
            if dict_event_class_sys2[k] == v:
                event_class[k + "\t" + v].append(int(1))
            else:
                event_class[k + "\t" + v].append(int(0))

        if k in dict_event_class_sys3:
            if dict_event_class_sys3[k] == v:
                event_class[k + "\t" + v].append(int(1))
            else:
                event_class[k + "\t" + v].append(int(0))

        if k in dict_event_class_sys4:
            if dict_event_class_sys4[k] == v:
                event_class[k + "\t" + v].append(int(1))
            else:
                event_class[k + "\t" + v].append(int(0))

        if k in dict_event_class_sys5:
            if dict_event_class_sys5[k] == v:
                event_class[k + "\t" + v].append(int(1))
            else:
                event_class[k + "\t" + v].append(int(0))

        if k in dict_event_class_sys6:
            if dict_event_class_sys6[k] == v:
                event_class[k + "\t" + v].append(int(1))
            else:
                event_class[k + "\t" + v].append(int(0))

        if k in dict_event_class_sys7:
            if dict_event_class_sys7[k] == v:
                event_class[k + "\t" + v].append(int(1))
            else:
                event_class[k + "\t" + v].append(int(0))

    event_class_tokens_gold_systems = {}

    for k, v in event_class.iteritems():
        print k, v
        k_splitted = k.split("\t")
        match = k_splitted[0] + "\t" + k_splitted[1]
        if match in token_text:
            event_class_tokens_gold_systems[k + "\t" + token_text[match]] = sum(v)


    for k, v in event_extent_tokens_gold_systems.iteritems():

        text_file = io.open(outdir + "extent_gold_systems", "a", encoding="utf-8")
        text_file.write(unicode(k + "\t" + str(v)) + "\n")
        text_file.close()

    for k, v in event_class_tokens_gold_systems.iteritems():

        text_file = io.open(outdir + "class_gold_systems", "a", encoding="utf-8")
        text_file.write(unicode(k + "\t" + str(v)) + "\n")
        text_file.close()

def contingent_matrix_event(gold_dir, sys1dir, sys2dir, sys3dir, sys4dir, sys5dir, sys6dir, sys7dir, outdir):

    for f in os.listdir(gold_dir):
        sys1f = sys1dir + f
        sys2f = sys2dir + f
        sys3f = sys3dir + f
        sys4f = sys4dir + f
        sys5f = sys5dir + f
        sys6f = sys6dir + f
        sys7f = sys7dir + f

        if f.endswith(".xml"):
#            outfile = outdir + f
#            get_data(sys1dir + f, sys2f, outfile)
            get_data(gold_dir + f, sys1f, sys2f, sys3f, sys4f, sys5f, sys6f, sys7f, outdir)
        else:
            print("Error - missing data: ") + f


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 10:
        print 'Usage: python compare_system_event2+Gold.py gold sys1 sys2 sys3 sys4 sys5 sys6 sys7 outdir'
    else:
        contingent_matrix_event(argv[1], argv[2], argv[3], argv[4], argv[5], argv[6], argv[7], argv[8], argv[9])

if __name__ == '__main__':
    main()