import sys
import collections
import os, os.path, re
import io
from lxml import etree

"""
compare in-house system output vs. others cleaned with gold for false positives
"""



def get_data(gold_data, sys1_out, sys2_out, sys3_out, sys4_out, sys5_out, outdir):

    """
    gold data
    """

    doc_gold = etree.parse(gold_data, etree.XMLParser(remove_blank_text=True))
    root_gold = doc_gold.getroot()
    root_gold.getchildren()

    doc_gold = root_gold.get('doc_name', 'null')

    dict_event_extent_gold = {}
    dict_event_attribute_gold = {}
    token_text = {}


    for elem in root_gold.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        event_tense = elem.get('tense', 'null')
        event_aspect = elem.get('aspect', 'null')
        event_pos = elem.get('pos', 'null')

        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_gold[doc_gold + "\t" + event_id] = token_id
            dict_event_attribute_gold[doc_gold + "\t" + event_id] = token_id + "\t" + event_class + "\t" + event_tense + "\t" + event_aspect + "\t" + event_pos

    """
    get article tokens
    """

    for elem in root_gold.findall('token'):
        token_id = elem.get('t_id', 'null')
        token = elem.text
        token_text[doc_gold + "\t" + token_id] = token


    dict_timex_attribute_gold_appo = {}
    dict_timex_attribute_gold = {}
    timex_extent_gold = collections.defaultdict(list)


    for elem in root_gold.findall('Markables/TIMEX3'):
        timex_id = elem.get('m_id', 'null')
        timex_class = elem.get('type', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_timex_attribute_gold_appo[doc_gold + "\t" + timex_id] = timex_class
            timex_extent_gold[doc_gold + "\t" + timex_id].append(token_id)

    for k, v in timex_extent_gold.iteritems():
        if k in dict_timex_attribute_gold_appo:
            dict_timex_attribute_gold[k] = str(v[0]) + "\t" + dict_timex_attribute_gold_appo[k]


    """
    get gold TLINK
    """

    gold_tlinks_event_timex = {}
    gold_tlinks_event_event = {}
    gold_tlinks_event_dct = {}


    for elem in root_gold.findall('Relations/TLINK'):
        relation_id = elem.get('r_id', 'null')
        relation_values = elem.get('relType', 'null')
        source_element = elem.find('source').get('m_id', 'null')
        target_element = elem.find('target').get('m_id', 'null')

        match_timex_source = doc_gold + "\t" + source_element
        match_event_target = doc_gold + "\t" + target_element


        if match_timex_source in dict_timex_attribute_gold and match_event_target in dict_event_attribute_gold:

            if  relation_values == "BEFORE":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element]  = "AFTER"

            if relation_values == "AFTER":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "BEFORE"

            if relation_values == "INCLUDES":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

            if relation_values == "IS_INCLUDED":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "INCLUDES"

            if relation_values == "DURING":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "INV_DURING"

            if relation_values == "INV_DURING":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "DURING"

            if relation_values == "BEGINS":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

            if relation_values == "BEGUN_BY":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "BEGINS"

            if relation_values == "ENDS":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

            if relation_values == "ENDED_BY":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "ENDS"

            if relation_values == "SIMULTANEOUS":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

            if relation_values == "IBEFORE":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "IAFTER"

            if relation_values == "IAFTER":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "IBEFORE"

            if relation_values == "IDENTITY":
                gold_tlinks_event_timex[doc_gold + "\t" + target_element + "\t" + source_element] = "IDENTITY"


        if match_timex_source in dict_event_attribute_gold and match_event_target in dict_timex_attribute_gold:
            gold_tlinks_event_timex[doc_gold + "\t" + source_element + "\t" + target_element] = relation_values


        if match_timex_source in dict_event_attribute_gold and match_event_target in dict_event_attribute_gold:

            if int(dict_event_extent_gold[match_timex_source]) < int(dict_event_extent_gold[match_event_target]):
                gold_tlinks_event_event[doc_gold + "\t" + source_element + "\t" + target_element] = relation_values


            if int(dict_event_extent_gold[match_timex_source]) > int(dict_event_extent_gold[match_event_target]):

                if relation_values == "BEFORE":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "AFTER"

                if relation_values == "AFTER":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "BEFORE"

                if relation_values == "INCLUDES":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

                if relation_values == "IS_INCLUDED":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "INCLUDES"

                if relation_values == "DURING":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "INV_DURING"

                if relation_values == "INV_DURING":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "DURING"

                if relation_values == "BEGINS":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

                if relation_values == "BEGUN_BY":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "BEGINS"

                if relation_values == "ENDS":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

                if relation_values == "ENDED_BY":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "ENDS"

                if relation_values == "SIMULTANEOUS":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

                if relation_values == "IBEFORE":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "IAFTER"

                if relation_values == "IAFTER":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "IBEFORE"

                if relation_values == "IDENTITY":
                    gold_tlinks_event_event[doc_gold + "\t" + target_element + "\t" + source_element] = "IDENTITY"

        if int(target_element) == 0:
            gold_tlinks_event_dct[doc_gold + "\t" + source_element + "\t" + target_element] = relation_values
    """
    solve gold TLINK
    """

    merge_markables = dict_event_attribute_gold.copy()
    merge_markables.update(dict_timex_attribute_gold)

    gold_tlinks_tokensId_event_timex_final = {}
    gold_tlinks_tokensId_event_event_final = {}
    gold_tlinks_tokensId_event_dct_final = {}

    """
    gold TLINK event-timex
    """

    for k, v in gold_tlinks_event_timex.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable
        match_target = filename + "\t" + target_markable

        if match_source in merge_markables and match_target in merge_markables:
            gold_tlinks_tokensId_event_timex_final[filename + "\t" + merge_markables[match_source].split("\t")[0] + "\t" + merge_markables[match_target].split("\t")[0]] = v


    """
    gold TLINK event-event
    """


    for k, v in gold_tlinks_event_event.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable
        match_target = filename + "\t" + target_markable

        if match_source in merge_markables and match_target in merge_markables:
            gold_tlinks_tokensId_event_event_final[filename + "\t" + merge_markables[match_source].split("\t")[0] + "\t" + merge_markables[match_target].split("\t")[0]] = v


    """
    gold TLINK event-dct
    """

    for k, v in gold_tlinks_event_dct.iteritems():
    #    print k, v
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable

        if match_source in merge_markables:
            gold_tlinks_tokensId_event_dct_final[filename + "\t" + merge_markables[match_source].split("\t")[0] + "\t" + k_splitted[2]] = v

#    print gold_tlinks_tokensId_event_dct_final

    """
     mysystem data
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
    get mysystem TLINK
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
    solve TLINK mysystem
    """

    merge_markables_sys1 = dict_event_attribute_sys1.copy()
    merge_markables_sys1.update(dict_timex_attribute_sys1)

    sys1_tlinks_tokensId_final = {}
    sys1_tlinks_dct_tokensId_final = {}



    for k, v in sys1_tlinks.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable
        match_target = filename + "\t" + target_markable

        if match_source in merge_markables_sys1 and match_target in merge_markables_sys1:
            sys1_tlinks_tokensId_final[filename + "\t" + merge_markables_sys1[match_source].split("\t")[0] + "\t" + merge_markables_sys1[match_target].split("\t")[0]] = v


    for k, v in sys1_tlinks_dct.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable

        if match_source in merge_markables_sys1:
            sys1_tlinks_dct_tokensId_final[filename + "\t" + merge_markables_sys1[match_source].split("\t")[0] + "\t" + target_markable] = v

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

    merge_markables_sys2 = dict_event_attribute_sys2.copy()
    merge_markables_sys2.update(dict_timex_attribute_sys2)

    sys2_tlinks_tokensId_final = {}
    sys2_tlinks_dct_tokensId_final = {}

    for k, v in sys2_tlinks.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable
        match_target = filename + "\t" + target_markable

        if match_source in merge_markables_sys2 and match_target in merge_markables_sys2:
            sys2_tlinks_tokensId_final[filename + "\t" + merge_markables_sys2[match_source].split("\t")[0] + "\t" + merge_markables_sys2[match_target].split("\t")[0]] = v

    for k, v in sys2_tlinks_dct.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable

        if match_source in merge_markables_sys2:
            sys2_tlinks_dct_tokensId_final[filename + "\t" + merge_markables_sys2[match_source].split("\t")[0] + "\t" + target_markable] = v


    """
     sys3 data
    """

    doc_sys3 = etree.parse(sys3_out, etree.XMLParser(remove_blank_text=True))
    root_sys3 = doc_sys3.getroot()
    root_sys3.getchildren()

    doc_name = root_sys3.get('doc_name', 'null')

    dict_event_extent_sys3 = {}
    dict_event_attribute_sys3 = {}

    for elem in root_sys3.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        event_tense = elem.get('tense', 'null')
        event_aspect = elem.get('aspect', 'null')
        event_pos = elem.get('pos', 'null')

        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys3[doc_name + "\t" + event_id] = token_id
            dict_event_attribute_sys3[doc_name + "\t" + event_id] = token_id + "\t" + event_class + "\t" + event_tense + "\t" + event_aspect + "\t" + event_pos

    """
    get article tokens
    """

    token_text_sys3 = {}

    for elem in root_sys3.findall('token'):
        token_id = elem.get('t_id', 'null')
        token = elem.text
        token_text_sys3[doc_name + "\t" + token_id] = token


    dict_timex_attribute_sys3_appo = {}
    dict_timex_attribute_sys3 = {}
    timex_extent_sys3 = collections.defaultdict(list)


    for elem in root_sys3.findall('Markables/TIMEX3'):
        timex_id = elem.get('m_id', 'null')
        timex_class = elem.get('type', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_timex_attribute_sys3_appo[doc_name + "\t" + timex_id] = timex_class
            timex_extent_sys3[doc_name + "\t" + timex_id].append(token_id)

    for k, v in timex_extent_sys3.iteritems():
        if k in dict_timex_attribute_sys3_appo:
            dict_timex_attribute_sys3[k] = str(v[0]) + "\t" + dict_timex_attribute_sys3_appo[k]


    """
    get sys3 TLINK
    """

    sys3_tlinks = {}
    sys3_tlinks_dct = {}

    for elem in root_sys3.findall('Relations/TLINK'):
        relation_id = elem.get('r_id', 'null')
        relation_values = elem.get('relType', 'null')
        source_element = elem.find('source').get('m_id', 'null')
        target_element = elem.find('target').get('m_id', 'null')

        match_timex_source = doc_name + "\t" + source_element
        match_event_target = doc_name + "\t" + target_element


        if match_timex_source in dict_timex_attribute_sys3 and match_event_target in dict_event_attribute_sys3:

            if  relation_values == "BEFORE":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element]  = "AFTER"

            if relation_values == "AFTER":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEFORE"

            if relation_values == "INCLUDES":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

            if relation_values == "IS_INCLUDED":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INCLUDES"

            if relation_values == "DURING":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INV_DURING"

            if relation_values == "INV_DURING":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "DURING"

            if relation_values == "BEGINS":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

            if relation_values == "BEGUN_BY":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGINS"

            if relation_values == "ENDS":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

            if relation_values == "ENDED_BY":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDS"

            if relation_values == "SIMULTANEOUS":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

            if relation_values == "IBEFORE":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IAFTER"

            if relation_values == "IAFTER":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IBEFORE"

            if relation_values == "IDENTITY":
                sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IDENTITY"

        if match_timex_source in dict_event_attribute_sys3  and match_event_target in dict_timex_attribute_sys3:
            sys3_tlinks[doc_name + "\t" + source_element + "\t" + target_element] = relation_values

        if match_timex_source in dict_event_attribute_sys3 and match_event_target in dict_event_attribute_sys3:

            if int(dict_event_extent_sys3[match_timex_source]) < int(dict_event_extent_sys3[match_event_target]):
                sys3_tlinks[doc_name + "\t" + source_element + "\t" + target_element] = relation_values


            if int(dict_event_extent_sys3[match_timex_source]) > int(dict_event_extent_sys3[match_event_target]):

                if relation_values == "BEFORE":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "AFTER"

                if relation_values == "AFTER":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEFORE"

                if relation_values == "INCLUDES":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

                if relation_values == "IS_INCLUDED":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INCLUDES"

                if relation_values == "DURING":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INV_DURING"

                if relation_values == "INV_DURING":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "DURING"

                if relation_values == "BEGINS":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

                if relation_values == "BEGUN_BY":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGINS"

                if relation_values == "ENDS":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

                if relation_values == "ENDED_BY":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDS"

                if relation_values == "SIMULTANEOUS":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

                if relation_values == "IBEFORE":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IAFTER"

                if relation_values == "IAFTER":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IBEFORE"

                if relation_values == "IDENTITY":
                    sys3_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IDENTITY"

        if int(target_element) == 0:
            sys3_tlinks_dct[doc_name + "\t" + source_element + "\t" + target_element] = relation_values

    """
    solve TLINK sys3
    """

    merge_markables_sys3 = dict_event_attribute_sys3.copy()
    merge_markables_sys3.update(dict_timex_attribute_sys3)

    sys3_tlinks_tokensId_final = {}
    sys3_tlinks_dct_tokensId_final = {}


    for k, v in sys3_tlinks.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable
        match_target = filename + "\t" + target_markable

        if match_source in merge_markables_sys3 and match_target in merge_markables_sys3:
            sys3_tlinks_tokensId_final[filename + "\t" + merge_markables_sys3[match_source].split("\t")[0] + "\t" + merge_markables_sys3[match_target].split("\t")[0]] = v



    for k, v in sys3_tlinks_dct.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable

        if match_source in merge_markables_sys3:
            sys3_tlinks_dct_tokensId_final[filename + "\t" + merge_markables_sys3[match_source].split("\t")[0] + "\t" + target_markable] = v



    """
     sys4 data
    """

    doc_sys4 = etree.parse(sys4_out, etree.XMLParser(remove_blank_text=True))
    root_sys4 = doc_sys4.getroot()
    root_sys4.getchildren()

    doc_name = root_sys4.get('doc_name', 'null')

    dict_event_extent_sys4 = {}
    dict_event_attribute_sys4 = {}

    for elem in root_sys4.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        event_tense = elem.get('tense', 'null')
        event_aspect = elem.get('aspect', 'null')
        event_pos = elem.get('pos', 'null')

        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys4[doc_name + "\t" + event_id] = token_id
            dict_event_attribute_sys4[doc_name + "\t" + event_id] = token_id + "\t" + event_class + "\t" + event_tense + "\t" + event_aspect + "\t" + event_pos

    """
    get article tokens
    """

    token_text_sys4 = {}

    for elem in root_sys4.findall('token'):
        token_id = elem.get('t_id', 'null')
        token = elem.text
        token_text_sys4[doc_name + "\t" + token_id] = token


    dict_timex_attribute_sys4_appo = {}
    dict_timex_attribute_sys4 = {}
    timex_extent_sys4 = collections.defaultdict(list)


    for elem in root_sys4.findall('Markables/TIMEX3'):
        timex_id = elem.get('m_id', 'null')
        timex_class = elem.get('type', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_timex_attribute_sys4_appo[doc_name + "\t" + timex_id] = timex_class
            timex_extent_sys4[doc_name + "\t" + timex_id].append(token_id)

    for k, v in timex_extent_sys4.iteritems():
        if k in dict_timex_attribute_sys4_appo:
            dict_timex_attribute_sys4[k] = str(v[0]) + "\t" + dict_timex_attribute_sys4_appo[k]


    """
    get sys4 TLINK
    """

    sys4_tlinks = {}
    sys4_tlinks_dct = {}

    for elem in root_sys4.findall('Relations/TLINK'):
        relation_id = elem.get('r_id', 'null')
        relation_values = elem.get('relType', 'null')
        source_element = elem.find('source').get('m_id', 'null')
        target_element = elem.find('target').get('m_id', 'null')

        match_timex_source = doc_name + "\t" + source_element
        match_event_target = doc_name + "\t" + target_element


        if match_timex_source in dict_timex_attribute_sys4 and match_event_target in dict_event_attribute_sys4:

            if  relation_values == "BEFORE":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element]  = "AFTER"

            if relation_values == "AFTER":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEFORE"

            if relation_values == "INCLUDES":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

            if relation_values == "IS_INCLUDED":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INCLUDES"

            if relation_values == "DURING":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INV_DURING"

            if relation_values == "INV_DURING":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "DURING"

            if relation_values == "BEGINS":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

            if relation_values == "BEGUN_BY":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGINS"

            if relation_values == "ENDS":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

            if relation_values == "ENDED_BY":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDS"

            if relation_values == "SIMULTANEOUS":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

            if relation_values == "IBEFORE":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IAFTER"

            if relation_values == "IAFTER":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IBEFORE"

            if relation_values == "IDENTITY":
                sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IDENTITY"


        if match_timex_source in dict_event_attribute_sys4  and match_event_target in dict_timex_attribute_sys4:
            sys4_tlinks[doc_name + "\t" + source_element + "\t" + target_element] = relation_values

        if match_timex_source in dict_event_attribute_sys4 and match_event_target in dict_event_attribute_sys4:

            if int(dict_event_extent_sys4[match_timex_source]) < int(dict_event_extent_sys4[match_event_target]):
                sys4_tlinks[doc_name + "\t" + source_element + "\t" + target_element] = relation_values


            if int(dict_event_extent_sys4[match_timex_source]) > int(dict_event_extent_sys4[match_event_target]):

                if relation_values == "BEFORE":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "AFTER"

                if relation_values == "AFTER":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEFORE"

                if relation_values == "INCLUDES":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

                if relation_values == "IS_INCLUDED":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INCLUDES"

                if relation_values == "DURING":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INV_DURING"

                if relation_values == "INV_DURING":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "DURING"

                if relation_values == "BEGINS":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

                if relation_values == "BEGUN_BY":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGINS"

                if relation_values == "ENDS":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

                if relation_values == "ENDED_BY":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDS"

                if relation_values == "SIMULTANEOUS":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

                if relation_values == "IBEFORE":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IAFTER"

                if relation_values == "IAFTER":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IBEFORE"

                if relation_values == "IDENTITY":
                    sys4_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IDENTITY"

        if int(target_element) == 0:
            sys4_tlinks_dct[doc_name + "\t" + source_element + "\t" + target_element] = relation_values

    """
    solve TLINK sys4
    """

    merge_markables_sys4 = dict_event_attribute_sys4.copy()
    merge_markables_sys4.update(dict_timex_attribute_sys4)

    sys4_tlinks_tokensId_final = {}
    sys4_tlinks_dct_tokensId_final = {}


    for k, v in sys4_tlinks.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable
        match_target = filename + "\t" + target_markable

        if match_source in merge_markables_sys4 and match_target in merge_markables_sys4:
            sys4_tlinks_tokensId_final[filename + "\t" + merge_markables_sys4[match_source].split("\t")[0] + "\t" + merge_markables_sys4[match_target].split("\t")[0]] = v


    for k, v in sys4_tlinks_dct.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable

        if match_source in merge_markables_sys4:
            sys4_tlinks_dct_tokensId_final[filename + "\t" + merge_markables_sys4[match_source].split("\t")[0] + "\t" + target_markable] = v


    """
     sys5 data
    """

    doc_sys5 = etree.parse(sys5_out, etree.XMLParser(remove_blank_text=True))
    root_sys5 = doc_sys5.getroot()
    root_sys5.getchildren()

    doc_name = root_sys5.get('doc_name', 'null')

    dict_event_extent_sys5 = {}
    dict_event_attribute_sys5 = {}

    for elem in root_sys5.findall('Markables/EVENT'):
        event_id = elem.get('m_id', 'null')
        event_class = elem.get('class', 'null')
        event_tense = elem.get('tense', 'null')
        event_aspect = elem.get('aspect', 'null')
        event_pos = elem.get('pos', 'null')

        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_event_extent_sys5[doc_name + "\t" + event_id] = token_id
            dict_event_attribute_sys5[doc_name + "\t" + event_id] = token_id + "\t" + event_class + "\t" + event_tense + "\t" + event_aspect + "\t" + event_pos

    """
    get article tokens
    """

    token_text_sys5 = {}

    for elem in root_sys5.findall('token'):
        token_id = elem.get('t_id', 'null')
        token = elem.text
        token_text_sys5[doc_name + "\t" + token_id] = token


    dict_timex_attribute_sys5_appo = {}
    dict_timex_attribute_sys5 = {}
    timex_extent_sys5 = collections.defaultdict(list)


    for elem in root_sys5.findall('Markables/TIMEX3'):
        timex_id = elem.get('m_id', 'null')
        timex_class = elem.get('type', 'null')
        for tokens in elem.findall('token_anchor'):
            token_id = tokens.get('t_id', 'null')

            dict_timex_attribute_sys5_appo[doc_name + "\t" + timex_id] = timex_class
            timex_extent_sys5[doc_name + "\t" + timex_id].append(token_id)

    for k, v in timex_extent_sys5.iteritems():
        if k in dict_timex_attribute_sys5_appo:
            dict_timex_attribute_sys5[k] = str(v[0]) + "\t" + dict_timex_attribute_sys5_appo[k]


    """
    get sys5 TLINK
    """

    sys5_tlinks = {}
    sys5_tlinks_dct = {}

    for elem in root_sys5.findall('Relations/TLINK'):
        relation_id = elem.get('r_id', 'null')
        relation_values = elem.get('relType', 'null')
        source_element = elem.find('source').get('m_id', 'null')
        target_element = elem.find('target').get('m_id', 'null')

        match_timex_source = doc_name + "\t" + source_element
        match_event_target = doc_name + "\t" + target_element


        if match_timex_source in dict_timex_attribute_sys5 and match_event_target in dict_event_attribute_sys5:

            if  relation_values == "BEFORE":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element]  = "AFTER"

            if relation_values == "AFTER":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEFORE"

            if relation_values == "INCLUDES":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

            if relation_values == "IS_INCLUDED":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INCLUDES"

            if relation_values == "DURING":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INV_DURING"

            if relation_values == "INV_DURING":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "DURING"

            if relation_values == "BEGINS":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

            if relation_values == "BEGUN_BY":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGINS"

            if relation_values == "ENDS":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

            if relation_values == "ENDED_BY":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDS"

            if relation_values == "SIMULTANEOUS":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

            if relation_values == "IBEFORE":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IAFTER"

            if relation_values == "IAFTER":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IBEFORE"

            if relation_values == "IDENTITY":
                sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IDENTITY"

        if match_timex_source in dict_event_attribute_sys5  and match_event_target in dict_timex_attribute_sys5:
            sys5_tlinks[doc_name + "\t" + source_element + "\t" + target_element] = relation_values


        if match_timex_source in dict_event_attribute_sys5 and match_event_target in dict_event_attribute_sys5:

            if int(dict_event_extent_sys5[match_timex_source]) < int(dict_event_extent_sys5[match_event_target]):
                sys5_tlinks[doc_name + "\t" + source_element + "\t" + target_element] = relation_values


            if int(dict_event_extent_sys5[match_timex_source]) > int(dict_event_extent_sys5[match_event_target]):

                if relation_values == "BEFORE":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "AFTER"

                if relation_values == "AFTER":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEFORE"

                if relation_values == "INCLUDES":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IS_INCLUDED"

                if relation_values == "IS_INCLUDED":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INCLUDES"

                if relation_values == "DURING":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "INV_DURING"

                if relation_values == "INV_DURING":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "DURING"

                if relation_values == "BEGINS":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGUN_BY"

                if relation_values == "BEGUN_BY":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "BEGINS"

                if relation_values == "ENDS":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDED_BY"

                if relation_values == "ENDED_BY":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "ENDS"

                if relation_values == "SIMULTANEOUS":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "SIMULTANEOUS"

                if relation_values == "IBEFORE":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IAFTER"

                if relation_values == "IAFTER":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IBEFORE"

                if relation_values == "IDENTITY":
                    sys5_tlinks[doc_name + "\t" + target_element + "\t" + source_element] = "IDENTITY"

        if int(target_element) == 0:
            sys5_tlinks_dct[doc_name + "\t" + source_element + "\t" + target_element] = relation_values


    """
    solve TLINK sys5
    """

    merge_markables_sys5 = dict_event_attribute_sys5.copy()
    merge_markables_sys5.update(dict_timex_attribute_sys5)

    sys5_tlinks_tokensId_final = {}
    sys5_tlinks_dct_tokensId_final = {}

    for k, v in sys5_tlinks.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable
        match_target = filename + "\t" + target_markable

        if match_source in merge_markables_sys5 and match_target in merge_markables_sys5:
            sys5_tlinks_tokensId_final[filename + "\t" + merge_markables_sys5[match_source].split("\t")[0] + "\t" + merge_markables_sys5[match_target].split("\t")[0]] = v

    for k, v in sys5_tlinks_dct.iteritems():
        k_splitted = k.split("\t")
        filename = k_splitted[0]
        source_markable = k_splitted[1]
        target_markable = k_splitted[2]

        match_source = filename + "\t" + source_markable

        if match_source in merge_markables_sys5:
            sys5_tlinks_dct_tokensId_final[filename + "\t" + merge_markables_sys5[match_source].split("\t")[0] + "\t" + target_markable] = v


    """
    tlink stats - mysystem vs others - clean with gold
    EVENT - EVENT (detc + value)
    """

    tlink_classification_values = collections.defaultdict(list)


    for k, v in sys1_tlinks_tokensId_final.iteritems():

        if k in sys2_tlinks_tokensId_final:
            if v == sys2_tlinks_tokensId_final[k]:
                tlink_classification_values[k + "\t" + v].append(int(1))
            else:
                tlink_classification_values[k + "\t" + v].append(int(0))

        if k in sys3_tlinks_tokensId_final:
            if v == sys3_tlinks_tokensId_final[k]:
                tlink_classification_values[k + "\t" + v].append(int(1))

            else:
                tlink_classification_values[k + "\t" + v].append(int(0))

        if k in sys4_tlinks_tokensId_final:
            if v == sys4_tlinks_tokensId_final[k]:
                tlink_classification_values[k + "\t" + v].append(int(1))

            else:
                tlink_classification_values[k + "\t" + v].append(int(0))

        if k in sys5_tlinks_tokensId_final:
            if v == sys5_tlinks_tokensId_final[k]:
                tlink_classification_values[k + "\t" + v].append(int(1))

            else:
                tlink_classification_values[k + "\t" + v].append(int(0))




    for k, v in gold_tlinks_tokensId_event_event_final.iteritems():
        match = k + "\t" + v
        if match in  tlink_classification_values:
            system_freq = sum(tlink_classification_values[match])

            text_file = io.open(outdir + "event_event_class", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" + v + "\t" + str(system_freq)) + "\n")
            text_file.close()

    """
    check tlink value
    EVENT - TIMEX
    """
    tlink_classification_timex_values = collections.defaultdict(list)



    for k, v in sys1_tlinks_tokensId_final.iteritems():

        if k in sys2_tlinks_tokensId_final:
            if v == sys2_tlinks_tokensId_final[k]:
                tlink_classification_timex_values[k + "\t" + v].append(int(1))
            else:
                tlink_classification_timex_values[k + "\t" + v].append(int(0))

        if k in sys3_tlinks_tokensId_final:
            if v == sys3_tlinks_tokensId_final[k]:
                tlink_classification_timex_values[k + "\t" + v].append(int(1))

            else:
                tlink_classification_timex_values[k + "\t" + v].append(int(0))

        if k in sys4_tlinks_tokensId_final:
            if v == sys4_tlinks_tokensId_final[k]:
                tlink_classification_timex_values[k + "\t" + v].append(int(1))
            else:
                tlink_classification_timex_values[k + "\t" + v].append(int(0))

        if k in sys5_tlinks_tokensId_final:
            if v == sys5_tlinks_tokensId_final[k]:
                tlink_classification_timex_values[k + "\t" + v].append(int(1))
            else:
                tlink_classification_timex_values[k + "\t" + v].append(int(0))

        if k in sys5_tlinks_tokensId_final:
            if v == sys5_tlinks_tokensId_final[k]:
                tlink_classification_timex_values[k + "\t" + v].append(int(1))
            else:
                tlink_classification_timex_values[k + "\t" + v].append(int(0))



    for k, v in gold_tlinks_tokensId_event_timex_final.iteritems():
        match_timex = k + "\t" + v
        if match_timex in tlink_classification_timex_values:

            system_freq = sum(tlink_classification_timex_values[match])

            text_file = io.open(outdir + "event_timex_class", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" + v + "\t" + str(system_freq)) + "\n")
            text_file.close()


    """
    check tlink value
    EVENT - DCT
    """

    tlink_classification_dct_values = collections.defaultdict(list)

    for k, v in sys1_tlinks_dct_tokensId_final.iteritems():

        if k in sys2_tlinks_dct_tokensId_final:
            if v == sys2_tlinks_dct_tokensId_final[k]:
                tlink_classification_dct_values[k + "\t" + v].append(int(1))
            else:
                tlink_classification_dct_values[k + "\t" + v].append(int(0))

        if k in sys3_tlinks_dct_tokensId_final:
            if v == sys3_tlinks_dct_tokensId_final[k]:
                tlink_classification_dct_values[k + "\t" + v].append(int(1))
            else:
                tlink_classification_dct_values[k + "\t" + v].append(int(0))

        if k in sys4_tlinks_dct_tokensId_final:
            if v == sys4_tlinks_dct_tokensId_final[k]:
                tlink_classification_dct_values[k + "\t" + v].append(int(1))

            else:
                tlink_classification_dct_values[k + "\t" + v].append(int(0))

        if k in sys5_tlinks_dct_tokensId_final:
            if v == sys5_tlinks_dct_tokensId_final[k]:
                tlink_classification_dct_values[k + "\t" + v].append(int(1))
            else:
                tlink_classification_dct_values[k + "\t" + v].append(int(0))




    for k, v in gold_tlinks_tokensId_event_dct_final.iteritems():
        match_dct = k + "\t" + v
        if match_dct in tlink_classification_dct_values:
            system_freq = sum(tlink_classification_dct_values[match_dct])

            text_file = io.open(outdir + "event_dct_class", "a", encoding="utf-8")
            text_file.write(unicode(k + "\t" + v + "\t" + str(system_freq)) + "\n")
            text_file.close()


def contingent_matrix_event(gold_dir, sys1dir, sys2dir, sys3dir, sys4dir, sys5dir, outdir):

    for f in os.listdir(gold_dir):
        sys1f = sys1dir + f
        sys2f = sys2dir + f
        sys3f = sys3dir + f
        sys4f = sys4dir + f
        sys5f = sys5dir + f

        if f.endswith(".xml"):
            get_data(gold_dir + f, sys1f, sys2f, sys3f, sys4f, sys5f, outdir)
        else:
            print("Error - missing data: ") + f


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 8:
        print 'Usage: python compare_mysystems_tlinks+gold.py gold mysystem sys2 sys3 sys4 sys5 outdir'
    else:
        contingent_matrix_event(argv[1], argv[2], argv[3], argv[4], argv[5], argv[6], argv[7])

if __name__ == '__main__':
    main()