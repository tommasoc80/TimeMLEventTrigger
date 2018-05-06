import sys
import collections
import os, os.path, re
import io
from lxml import etree

"""
compare all outputs of 2 systems for TLINK detection and classification
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
    dict_event_attribute_sys1 = {}

    for elem in root_sys1.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        event_tense = elem.get('tense', 'null')
        event_aspect = elem.get('aspect', 'null')
        event_pos = elem.get('pos', 'null')

        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys1[doc_name + "\t" + event_id] = token_id
            dict_event_attribute_sys1[doc_name + "\t" + event_id] = token_id + "\t" + event_class + "\t" + event_tense + "\t" + event_aspect + "\t" + event_pos

    """
    get article tokens
    """

    token_text_sys1 = {}

    for elem in root_sys1.findall('token'):
        token_id = elem.get('t_id', 'null')
        token = elem.text
        token_text_sys1[doc_name + "\t" + token_id] = token


    dict_timex_attribute_sys1_appo = {}
    dict_timex_attribute_sys1 = {}
    timex_extent_sys1 = collections.defaultdict(list)


    for elem in root_sys1.findall('Markables/TIMEX3'):
        timex_id = elem.get('m_id', 'null')
        timex_class = elem.get('type', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_timex_attribute_sys1_appo[doc_name + "\t" + timex_id] = timex_class
            timex_extent_sys1[doc_name + "\t" + timex_id].append(token_id)

    for k, v in timex_extent_sys1.iteritems():
        if k in dict_timex_attribute_sys1_appo:
            dict_timex_attribute_sys1[k] = str(v[0]) + "\t" + dict_timex_attribute_sys1_appo[k]


    """
    get sys1 TLINK
    """

    sys1_tlinks = {}
    sys1_tlinks_dct = {}

    for elem in root_sys1.findall('Relations/TLINK'):
        relation_id = elem.get('r_id', 'null')
        relation_values = elem.get('relType', 'null')
        source_element = elem.find('source').get('m_id', 'null')
        target_element = elem.find('target').get('m_id', 'null')

        match_timex_source = doc_name + "\t" + source_element
        match_event_target = doc_name + "\t" + target_element


        if match_timex_source in dict_timex_attribute_sys1 and match_event_target in dict_event_attribute_sys1:

            if  relation_values == "BEFORE":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element]  = "AFTER"

            if relation_values == "AFTER":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEFORE"

            if relation_values == "INCLUDES":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

            if relation_values == "IS_INCLUDED":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INCLUDES"

            if relation_values == "DURING":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INV_DURING"

            if relation_values == "INV_DURING":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "DURING"

            if relation_values == "BEGINS":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

            if relation_values == "BEGUN_BY":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGINS"

            if relation_values == "ENDS":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

            if relation_values == "ENDED_BY":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDS"

            if relation_values == "SIMULTANEOUS":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

            if relation_values == "IBEFORE":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IAFTER"

            if relation_values == "IAFTER":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IBEFORE"

            if relation_values == "IDENTITY":
                sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IDENTITY"

        if match_timex_source in dict_event_attribute_sys1 and match_event_target in dict_timex_attribute_sys1:
            sys1_tlinks[doc_name + "\t" + source_element + "\t" + target_element] = relation_values


        if match_timex_source in dict_event_attribute_sys1 and match_event_target in dict_event_attribute_sys1:

            if int(dict_event_extent_sys1[match_timex_source]) < int(dict_event_extent_sys1[match_event_target]):
                sys1_tlinks[doc_name + "\t" + source_element + "\t" + target_element] = relation_values


            if int(dict_event_extent_sys1[match_timex_source]) > int(dict_event_extent_sys1[match_event_target]):

                if relation_values == "BEFORE":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "AFTER"

                if relation_values == "AFTER":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEFORE"

                if relation_values == "INCLUDES":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

                if relation_values == "IS_INCLUDED":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INCLUDES"

                if relation_values == "DURING":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INV_DURING"

                if relation_values == "INV_DURING":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "DURING"

                if relation_values == "BEGINS":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

                if relation_values == "BEGUN_BY":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGINS"

                if relation_values == "ENDS":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

                if relation_values == "ENDED_BY":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDS"

                if relation_values == "SIMULTANEOUS":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

                if relation_values == "IBEFORE":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IAFTER"

                if relation_values == "IAFTER":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IBEFORE"

                if relation_values == "IDENTITY":
                    sys1_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IDENTITY"

        if int(target_element) == 0:
            sys1_tlinks_dct[doc_name + "\t" + source_element + "\t" + target_element] = relation_values

    """
    solve TLINK sys1
    """

#    dict_event_attribute_sys1
#    dict_timex_attribute_sys1

    sys1_tlinks_tokensId_final_event_event = {}
    sys1_tlinks_tokensId_final_event_timex = {}
    sys1_tlinks_dct_tokensId_final = {}



    for k, v in sys1_tlinks.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable
        match_target = filename + "\t" + target_markable

        if match_source in dict_event_attribute_sys1 and match_target in dict_event_attribute_sys1:
            sys1_tlinks_tokensId_final_event_event[filename + "\t" + dict_event_attribute_sys1[match_source].split("\t")[0] + "\t" + dict_event_attribute_sys1[match_target].split("\t")[0]] = v


    for k, v in sys1_tlinks_dct.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable

        if match_source in dict_event_attribute_sys1:
            sys1_tlinks_dct_tokensId_final[filename + "\t" + dict_event_attribute_sys1[match_source].split("\t")[0] + "\t" + target_markable] = v

    for k, v in sys1_tlinks.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        if target_markable != "0":
            match_source = filename + "\t" + source_markable
            match_target = filename + "\t" + target_markable

            if match_source in dict_event_attribute_sys1 and match_target in dict_timex_attribute_sys1:
                sys1_tlinks_tokensId_final_event_timex[filename + "\t" + dict_event_attribute_sys1[match_source].split("\t")[0] + "\t" + dict_timex_attribute_sys1[match_target].split("\t")[0]] = v

    """
     sys2 data
    """

    doc_sys2 = etree.parse(sys2_out, etree.XMLParser(remove_blank_text=True))
    root_sys2 = doc_sys2.getroot()
    root_sys2.getchildren()

    doc_name = root_sys2.get('doc_name', 'null')

    dict_event_extent_sys2 = {}
    dict_event_attribute_sys2 = {}

    for elem in root_sys2.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        event_tense = elem.get('tense', 'null')
        event_aspect = elem.get('aspect', 'null')
        event_pos = elem.get('pos', 'null')

        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys2[doc_name + "\t" + event_id] = token_id
            dict_event_attribute_sys2[doc_name + "\t" + event_id] = token_id + "\t" + event_class + "\t" + event_tense + "\t" + event_aspect + "\t" + event_pos

    """
    get article tokens sys2
    """

    token_text_sys2 = {}

    for elem in root_sys2.findall('token'):
        token_id = elem.get('t_id', 'null')
        token = elem.text
        token_text_sys2[doc_name + "\t" + token_id] = token


    dict_timex_attribute_sys2_appo = {}
    dict_timex_attribute_sys2 = {}
    timex_extent_sys2 = collections.defaultdict(list)


    for elem in root_sys2.findall('Markables/TIMEX3'):
        timex_id = elem.get('m_id', 'null')
        timex_class = elem.get('type', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_timex_attribute_sys2_appo[doc_name + "\t" + timex_id] = timex_class
            timex_extent_sys2[doc_name + "\t" + timex_id].append(token_id)

    for k, v in timex_extent_sys2.iteritems():
        if k in dict_timex_attribute_sys2_appo:
            dict_timex_attribute_sys2[k] = str(v[0]) + "\t" + dict_timex_attribute_sys2_appo[k]


    """
    get sys2 TLINK
    """

    sys2_tlinks = {}
    sys2_tlinks_dct = {}

    for elem in root_sys2.findall('Relations/TLINK'):
        relation_id = elem.get('r_id', 'null')
        relation_values = elem.get('relType', 'null')
        source_element = elem.find('source').get('m_id', 'null')
        target_element = elem.find('target').get('m_id', 'null')

        match_timex_source = doc_name + "\t" + source_element
        match_event_target = doc_name + "\t" + target_element


        if match_timex_source in dict_timex_attribute_sys2 and match_event_target in dict_event_attribute_sys2:

            if  relation_values == "BEFORE":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element]  = "AFTER"

            if relation_values == "AFTER":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEFORE"

            if relation_values == "INCLUDES":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

            if relation_values == "IS_INCLUDED":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INCLUDES"

            if relation_values == "DURING":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INV_DURING"

            if relation_values == "INV_DURING":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "DURING"

            if relation_values == "BEGINS":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

            if relation_values == "BEGUN_BY":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGINS"

            if relation_values == "ENDS":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

            if relation_values == "ENDED_BY":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDS"

            if relation_values == "SIMULTANEOUS":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

            if relation_values == "IBEFORE":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IAFTER"

            if relation_values == "IAFTER":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IBEFORE"

            if relation_values == "IDENTITY":
                sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IDENTITY"

        if match_timex_source in dict_event_attribute_sys2  and match_event_target in dict_timex_attribute_sys2:
            sys2_tlinks[doc_name + "\t" + source_element + "\t" + target_element] = relation_values


        if match_timex_source in dict_event_attribute_sys2 and match_event_target in dict_event_attribute_sys2:

            if int(dict_event_extent_sys2[match_timex_source]) < int(dict_event_extent_sys2[match_event_target]):
                sys2_tlinks[doc_name + "\t" + source_element + "\t" + target_element] = relation_values


            if int(dict_event_extent_sys2[match_timex_source]) > int(dict_event_extent_sys2[match_event_target]):

                if relation_values == "BEFORE":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "AFTER"

                if relation_values == "AFTER":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEFORE"

                if relation_values == "INCLUDES":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

                if relation_values == "IS_INCLUDED":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INCLUDES"

                if relation_values == "DURING":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INV_DURING"

                if relation_values == "INV_DURING":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "DURING"

                if relation_values == "BEGINS":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

                if relation_values == "BEGUN_BY":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGINS"

                if relation_values == "ENDS":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

                if relation_values == "ENDED_BY":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDS"

                if relation_values == "SIMULTANEOUS":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

                if relation_values == "IBEFORE":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IAFTER"

                if relation_values == "IAFTER":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IBEFORE"

                if relation_values == "IDENTITY":
                    sys2_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IDENTITY"

        if int(target_element) == 0:
            sys2_tlinks_dct[doc_name + "\t" + source_element + "\t" + target_element] = relation_values


    """
    solve TLINK sys2
    """

    #dict_event_attribute_sys2
    #dict_timex_attribute_sys2

    sys2_tlinks_tokensId_final_event_event = {}
    sys2_tlinks_tokensId_final_event_timex = {}
    sys2_tlinks_dct_tokensId_final = {}

    for k, v in sys2_tlinks.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable
        match_target = filename + "\t" + target_markable

        if match_source in dict_event_attribute_sys2 and match_target in dict_event_attribute_sys2:
            sys2_tlinks_tokensId_final_event_event[
                filename + "\t" + dict_event_attribute_sys2[match_source].split("\t")[0] + "\t" +
                dict_event_attribute_sys2[match_target].split("\t")[0]] = v

    for k, v in sys2_tlinks_dct.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable

        if match_source in dict_event_attribute_sys2:

            sys2_tlinks_dct_tokensId_final[
                filename + "\t" + dict_event_attribute_sys2[match_source].split("\t")[0] + "\t" + target_markable] = v

    for k, v in sys2_tlinks.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        if target_markable != "0":
            match_source = filename + "\t" + source_markable
            match_target = filename + "\t" + target_markable

            if match_source in dict_event_attribute_sys2 and match_target in dict_timex_attribute_sys2:
                sys2_tlinks_tokensId_final_event_timex[
                    filename + "\t" + dict_event_attribute_sys2[match_source].split("\t")[0] + "\t" +
                    dict_timex_attribute_sys2[match_target].split("\t")[0]] = v



    """
    get stats systems' overlap




    for k, v in sys1_tlinks_dct_tokensId_final.iteritems():


        if k in sys2_tlinks_dct_tokensId_final:
            if v == sys2_tlinks_dct_tokensId_final[k]:
                text_file = io.open(outdir + "common_dct_same_class", "a", encoding="utf-8")
                text_file.write(unicode(k + "\t" + v) + "\n")
                text_file.close()

            else:
                text_file = io.open(outdir + "common_dct_diff_class", "a", encoding="utf-8")
                text_file.write(unicode(k + "\t" + v + "\t" + sys2_tlinks_dct_tokensId_final[k]) + "\n")
                text_file.close()
        else:

            text_file = io.open(outdir + "different_dct_detc", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" + v) + "\n")
            text_file.close()


    for k, v in sys1_tlinks_tokensId_final_event_event.iteritems():
        if k in sys2_tlinks_tokensId_final_event_event:
            if v == sys2_tlinks_tokensId_final_event_event[k]:
                text_file = io.open(outdir + "common_event_same_class", "a", encoding="utf-8")
                text_file.write(unicode(k + "\t" + v) + "\n")
                text_file.close()

            else:
                text_file = io.open(outdir + "common_event_diff_class", "a", encoding="utf-8")
                text_file.write(unicode(k + "\t" + v + "\t" + sys2_tlinks_tokensId_final_event_event[k]) + "\n")
                text_file.close()
        else:

            text_file = io.open(outdir + "different_event_detc", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" + v) + "\n")
            text_file.close()


    for k, v in sys1_tlinks_tokensId_final_event_timex.iteritems():
        if k in sys2_tlinks_tokensId_final_event_timex:
            print k, v
            if v == sys2_tlinks_tokensId_final_event_timex[k]:
                text_file = io.open(outdir + "common_timex_same_class", "a", encoding="utf-8")
                text_file.write(unicode(k + "\t" + v) + "\n")
                text_file.close()

            else:
                text_file = io.open(outdir + "common_timex_diff_class", "a", encoding="utf-8")
                text_file.write(unicode(k + "\t" + v + "\t" + sys2_tlinks_tokensId_final_event_timex[k]) + "\n")
                text_file.close()
        else:

            text_file = io.open(outdir + "different_timex_detc", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" + v) + "\n")
            text_file.close()

    """


    """
    print to check correctness of false positives for sys2
    """


    for k, v in sys1_tlinks_dct_tokensId_final.iteritems():
        if k not in sys2_tlinks_dct_tokensId_final:
            text_file = io.open(outdir + "FP_dct", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" + v) + "\n")
            text_file.close()

    for k, v in sys1_tlinks_tokensId_final_event_timex.iteritems():
        if k not in sys2_tlinks_tokensId_final_event_timex:


            text_file = io.open(outdir + "FP_timex", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" + v) + "\n")
            text_file.close()


    for k, v in sys1_tlinks_tokensId_final_event_event.iteritems():
        if k not in sys2_tlinks_tokensId_final_event_event:
            text_file = io.open(outdir + "FP_event", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" + v) + "\n")
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
        print 'Usage: python compare_system_tlink1.py sys1 sys2 outdir'
    else:
        contingent_matrix_event(argv[1], argv[2], argv[3])

if __name__ == '__main__':
    main()