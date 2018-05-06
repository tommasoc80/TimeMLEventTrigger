# -*- coding: UTF-8 -*- 
import sys
import collections
from itertools import combinations
import os, os.path, re

#from KafNafParserPy import *


#################################
# Extract TEST features for TLINK EVENT-EVENT - same sentence
# Author: Tommaso Caselli
#
# Generate training data for TLINK between event and timex in the same sentence only
##################################

def change_rel_val(tlink_value):

    if tlink_value == "BEFORE":
        new_rel_val = "AFTER"
        return new_rel_val

    if tlink_value == "AFTER":
        new_rel_val = "BEFORE"
        return new_rel_val

    if tlink_value == "INCLUDES":
        new_rel_val = "IS_INCLUDED"
        return new_rel_val

    if tlink_value == "INCLUDES":
        new_rel_val = "IS_INCLUDED"
        return new_rel_val

    if tlink_value == "BEGINS":
        new_rel_val = "BEGUN_BY"
        return new_rel_val

    if tlink_value == "BEGUN_BY":
        new_rel_val = "BEGINS"
        return new_rel_val

    if tlink_value == "ENDS":
        new_rel_val = "ENDED_BY"
        return new_rel_val

    if tlink_value == "ENDED_BY":
        new_rel_val = "ENDS"
        return new_rel_val


    if tlink_value == "DURING":
        new_rel_val = "DURING"
        return new_rel_val

    if tlink_value == "SIMULTANEOUS":
        new_rel_val = "SIMULTANEOUS"
        return new_rel_val

    if tlink_value == "O":
        new_rel_val = "O"
        return new_rel_val

    if tlink_value == "IBEFORE":
        new_rel_val = "IAFTER"
        return new_rel_val

    if tlink_value == "IAFTER":
        new_rel_val = "IBEFORE"
        return new_rel_val


def tsignal_read(tlinkf):
    signal_list = []

    with open(tlinkf) as f:
        for line in f:
            line_stripped = line.strip()
            entry = line_stripped.replace(' ', '_')
            signal_list.append(entry)

    return signal_list


def caevo_read(caevof):
    caevo_data = {}

    with open(caevof) as f:
        for line in f:
            line_stripped = line.strip()
            line_splitted = line_stripped.split("\t")

            if line_splitted[3] != "v":
                if line_splitted[1].startswith("e") and line_splitted[2].startswith("e"):
                    caevo_data[(line_splitted[0], line_splitted[1], line_splitted[2],)] = line_splitted[3].replace('a', 'AFTER').replace('ii', 'IS_INCLUDED').replace('b','BEFORE').replace('i','INCLUDES')

    return caevo_data

def get_timex_features(timex_data, timex_type_dict, event_extent_train_data):

    timex_features = {}
    timex_tokens = collections.defaultdict(list)
    timex_features_final = {}


    for timex, timex_token_id in timex_data.items():
        sentence_id, timex_val, timex_id = timex

        timex_span_start = timex_token_id[0]
        if int(timex_span_start) in event_extent_train_data:
            timex_features[timex + (timex_token_id[0],)] = event_extent_train_data[int(timex_span_start)][4:]

        for i in timex_token_id:
            if int(i) in event_extent_train_data:
                timex_tokens[timex_id].append(event_extent_train_data[int(i)][3])

    for timex_feat, feats in timex_features.items():
        sentence_id, timex_val, timex_id, token_id = timex_feat
        if timex_id in timex_tokens:
            if timex_id in timex_type_dict:
                timex_features_final[timex_feat] = ("_".join(timex_tokens[timex_id]),) + feats + (timex_type_dict[timex_id],)

    return timex_features_final

def generate_pos_neg_instance(event_same_sentence, event_event_link):


    positive_examples = {}
    negative_examples = {}

    same_sent_full_pairs = []
    for sentence, event_id_list in event_same_sentence.items():
        if len(event_id_list) >= 2:
            same_sent_ = list(combinations(event_id_list, 2))
            for elem in same_sent_:
                same_sent_full_pairs.append(elem)


    for entry in event_event_link:
        event1, event2, tlink_val = entry
        match = (event1, event2,)
        if match in same_sent_full_pairs:
            positive_examples[(event1, event2,)] = tlink_val

    for entry in same_sent_full_pairs:
        if entry not in positive_examples:
            negative_examples[entry] = "O"

    return positive_examples, negative_examples


def add_distance(event_extent_data_dict,postive_examples_dict,negative_examples_dict):


    feature_merge = {}

    data_full = postive_examples_dict.copy()
    data_full.update(negative_examples_dict)


    for event_pair, tlink in data_full.items():
        source, target = event_pair
        for k, v in event_extent_data_dict.items():
            file_name, sentence_id, id_per_sentence, token, lemma, pos_stanford, dependency_label, dependent_lemma, \
            dependent_pos, path2root1, path2root2, path2root3, path2root4, path2root5, ner_stanford, timex_extent_bio, verbnet_classes, \
            framenet_frames, wordnet_class, arguments, \
            timeml_tense, timeml_aspect, timeml_modality, timeml_polarity, \
            timeml_event_id, tieml_event_bio = v

            for k1, v1 in event_extent_data_dict.items():
                file_name1, sentence_id1, id_per_sentence1, token1, lemma1, pos_stanford1, dependency_label1, dependent_lemma1, \
                dependent_pos1, path2root11, path2root21, path2root31, path2root41, path2root51, ner_stanford1, timex_extent_bio1, verbnet_classes1, \
                framenet_frames1, wordnet_class1, arguments1, \
                timeml_tense1, timeml_aspect1, timeml_modality1, timeml_polarity1, \
                timeml_event_id1, tieml_event_bio1 = v1

                if source == timeml_event_id:
                    if target == timeml_event_id1:
                        distance = abs(k - k1)
                        feature_merge[event_pair] = (k,) + v + (k1,) + v1 + (str(distance),tlink)

    return feature_merge


def add_shared_path(distance_feat_dict):

    for k, v in distance_feat_dict.items():
        event_token_source = int(v[0])
        event_token_target = int(v[27])

        source_lemma = v[5]
        target_lemma = v[32]
        source_token_path = v[12]
        target_token_path = v[39]


        if event_token_source < event_token_target:
            target_token_path_split = target_token_path.split("_")
            if source_lemma in target_token_path_split:
                index_split = target_token_path_split.index(source_lemma)
                pos_path = "_".join((v[38].split("_")[0:index_split]))
                dep_path = "_".join((v[40].split("_")[0:index_split]))
                dep_pos_path_list = list(zip(v[38].split("_")[0:index_split], v[40].split("_")[0:index_split]))
                dep_pos_path_string = '_'.join(map(str,["_".join(entry) for entry in dep_pos_path_list]))
                new_val = v + (pos_path,dep_path,dep_pos_path_string,"O", "O", "O","O", "O", "O", v[-1],)
                distance_feat_dict[k] = new_val
            else:
                reversed_target_pos = "_".join(reversed(v[38].split("_")))
                reversed_target_dep = "_".join(reversed(v[40].split("_")))
                pos_path_target_list = list(zip(reversed(v[38].split("_")), reversed(v[40].split("_"))))
                pos_dep_path_string_target = '_'.join(map(str,["_".join(entry) for entry in pos_path_target_list]))

                dep_pos_path_list_source = list(zip(v[11].split("_"), v[13].split("_")))
                dep_pos_path_string_source = '_'.join(map(str,["_".join(entry) for entry in dep_pos_path_list_source]))

                new_val = v + ("O", "O", "O",v[11],v[13],dep_pos_path_string_source,reversed_target_pos,reversed_target_dep,pos_dep_path_string_target, v[-1],)
                distance_feat_dict[k] = new_val

        if event_token_source > event_token_target:
            source_token_path_split = source_token_path.split("_")
            if target_lemma in source_token_path_split:
                index_split = source_token_path_split.index(target_lemma)
                pos_path = "_".join((v[11].split("_")[0:index_split]))
                dep_path = "_".join((v[13].split("_")[0:index_split]))
                dep_pos_path_list = list(zip(v[11].split("_")[0:index_split], v[13].split("_")[0:index_split]))
                dep_pos_path_string = '_'.join(map(str, ["_".join(entry) for entry in dep_pos_path_list]))

                tlink_invert = change_rel_val(v[-1])
                new_val = v + (pos_path, dep_path, dep_pos_path_string, "O", "O", "O","O", "O", "O", tlink_invert,)
                distance_feat_dict[k] = new_val
            else:
                reversed_event_pos_source = "_".join(reversed(v[11].split("_")))
                reversed_event_dep_source = "_".join(reversed(v[13].split("_")))
                pos_path_event_source_list = list(zip(reversed(v[11].split("_")), reversed(v[13].split("_"))))
                pos_dep_path_string_event_source = '_'.join(map(str, ["_".join(entry) for entry in pos_path_event_source_list]))

                dep_pos_path_list_target = list(zip(v[38].split("_"), v[40].split("_")))
                dep_pos_path_string_target = '_'.join(map(str, ["_".join(entry) for entry in dep_pos_path_list_target]))

                #reversed_timex_pos = "_".join(reversed(v[34].split("_")))
                #reversed_timex_dep = "_".join(reversed(v[36].split("_")))
                #pos_path_timex_list = list(zip(reversed(v[34].split("_")), reversed(v[36].split("_"))))
                #pos_dep_path_string_tmx = '_'.join(map(str, ["_".join(entry) for entry in pos_path_timex_list]))

                #dep_pos_path_list_event = list(zip(v[11].split("_"), v[13].split("_")))
                #dep_pos_path_string_event = '_'.join(map(str, ["_".join(entry) for entry in dep_pos_path_list_event]))
                tlink_invert = change_rel_val(v[-1])

                new_val = v + (
                "O", "O", "O", v[38],v[40],
                dep_pos_path_string_target, reversed_event_pos_source, reversed_event_dep_source, pos_dep_path_string_event_source,tlink_invert,)
                distance_feat_dict[k] = new_val

    return distance_feat_dict



def add_signal_tokens(data_features_dict, signalList, sentence_lemmas_dict):

    tlink_signals = collections.defaultdict(list)
    for sentence_id, lemma_list in sentence_lemmas_dict.items():
        for elem in lemma_list:
            token_id, sentence_token_id, lemma = elem
            if lemma in  signalList:
                tlink_signals[sentence_id].append((token_id, sentence_token_id, lemma))

    middle_signal = collections.defaultdict(list)
    before_source = collections.defaultdict(list)
    for event_pairs, features in data_features_dict.items():

        sentence_id = features[2]

        if sentence_id in tlink_signals:
            for entry in tlink_signals[sentence_id]:
                token_id, sentence_token_id, lemma = entry
                if int(token_id) > int(features[0]) and int(token_id) < int(features[27]):
                    middle_signal[event_pairs].append(lemma)
                if int(token_id) < int(features[0]) and int(token_id) > int(features[27]):
                    middle_signal[event_pairs].append(lemma)

                if int(features[0]) < int(features[27]):
                    if int(token_id) < int(features[0]):
                        before_source[event_pairs].append(lemma)
                else:
                    if int(token_id) < int(features[27]):
                        before_source[event_pairs].append(lemma)

    for tlink_pairs, features in data_features_dict.items():

        if tlink_pairs in middle_signal:
            string_signal = "_".join(middle_signal[tlink_pairs])
            new_val = features + (string_signal,)
            data_features_dict[tlink_pairs] = new_val
        else:
            new_val = features + ("O",)
            data_features_dict[tlink_pairs] = new_val


    for tlink_pairs, features in data_features_dict.items():

        if tlink_pairs in before_source:
            signal_lemma = "_".join(before_source[tlink_pairs])
            new_val = features + (signal_lemma,)
            data_features_dict[tlink_pairs] = new_val
        else:
            new_val = features + ("O",)
            data_features_dict[tlink_pairs] = new_val

    return data_features_dict


def check_extra_event(data_features_dict, event_dict):

    for event_pair, features in data_features_dict.items():
        source = features[0]
        target = features[27]
        sentence  = features[2]

        if sentence in event_dict:
            event_list = event_dict[sentence]

            if source < target:
                for elem in event_list:
                    if source < int(elem) and target > int(elem):
                        new_val = features + ("YES",)
                        data_features_dict[event_pair] = new_val
                    else:
                        new_val = features + ("NO",)
                        data_features_dict[event_pair] = new_val

            if source > target:
                for elem in event_list:
                    if source > int(elem) and target < int(elem):
                        new_val = features + ("YES",)
                        data_features_dict[event_pair] = new_val
                    else:
                        new_val = features + ("NO",)
                        data_features_dict[event_pair] = new_val

    return data_features_dict


def read_data(event_extentf, trainf, signal_list, caevo_dict):

    event_extent_data = {}
    sentence_lemmas = collections.defaultdict(list)
    with open(event_extentf) as f:
        for line in f:
            line_stripped = line.strip()
            line_splitted =  line_stripped.split("\t")

            if len(line_splitted) > 1:
                file_name = line_splitted[0]
                unique_id = line_splitted[1]
                sentence_id = line_splitted[2]
                id_per_sentence = line_splitted[3]
                token = line_splitted[4]
                lemma = line_splitted[5]
                pos_stanford = line_splitted[6]
                dependency_label = line_splitted[7]
                dependent_lemma = line_splitted[8]
                dependent_pos = line_splitted[9]
                path2root1 = line_splitted[10]
                path2root2 = line_splitted[11]
                path2root3 = line_splitted[12]
                path2root4 = line_splitted[13]
                path2root5 = line_splitted[14]
                ner_stanford = line_splitted[15]
                timex_extent_bio = line_splitted[16]
                verbnet_classes = line_splitted[17]
                framenet_frames = line_splitted[18]
                wordnet_class = line_splitted[19]
                arguments = line_splitted[20]
                timeml_tense = line_splitted[21]
                timeml_aspect = line_splitted[22]
                timeml_modality = line_splitted[23]
                timeml_polarity = line_splitted[24]
                timeml_event_id = line_splitted[25]
                tieml_event_bio = line_splitted[26]

                event_extent_data[int(unique_id)] = (file_name,sentence_id,id_per_sentence,token,lemma,pos_stanford,dependency_label,
                                                dependent_lemma,dependent_pos,path2root1,path2root2,path2root3,path2root4, path2root5, ner_stanford,
                                                timex_extent_bio,verbnet_classes,framenet_frames,wordnet_class,arguments,timeml_tense,
                                                timeml_aspect,timeml_modality,timeml_polarity,timeml_event_id,tieml_event_bio)

                sentence_lemmas[sentence_id].append((unique_id, id_per_sentence, lemma,))

    event_same_sentence = collections.defaultdict(list)
    event_event_link = []
    event_tokens = collections.defaultdict(list)

    with open(trainf) as f:

        for line in f:
            line_stripped = line.strip()
            line_splitted = line_stripped.split("\t")

            if len(line_splitted) > 1:
                token = line_splitted[0]
                token_id = line_splitted[1].replace('-99', '0')
                sentence_id = line_splitted[2]

                event_id = line_splitted[3]
                event_class = line_splitted[4]
                stem = line_splitted[5]
                tense = line_splitted[6]
                aspect = line_splitted[7]
                polarity = line_splitted[8]
                modality = line_splitted[9]
                timeMLPOS = line_splitted[10]

                timexId = line_splitted[11]
                timexType = line_splitted[12]
                timexVal = line_splitted[13]
                timeAnchorId = line_splitted[14]
                timexFunction = line_splitted[15]
                functionInDoc = line_splitted[16]

                tLink = line_splitted[17]
                sLink = line_splitted[18]
                aLink = line_splitted[19]
                cLink = line_splitted[20]

                signalIdTlink = line_splitted[21]
                sinalIdClink = line_splitted[22]


                #################
                # event class
                #################

                for k, v in event_extent_data.items():
                    if k == int(token_id):
                        new_val = v[:-1] + (event_class,)
                        event_extent_data[k] = new_val


                ##########################
                # event in the same sentence
                ##########################
                if event_id != "O":
                    event_same_sentence[sentence_id].append(event_id)
                    event_tokens[sentence_id].append(token_id)

                """
                TLINK
                """

                if tLink != "O":
                    if "||" not in tLink:

                        tlink_elem = tLink.split(":")

                        source = tlink_elem[0]
                        target = tlink_elem[1]
                        rel_val = tlink_elem[2]

                        if source.startswith("e") and target.startswith("e"):
                            event_event_link.append((target, source, rel_val,))

                    else:
                        tlink_elem = tLink.split("||")
                        for i in tlink_elem:

                            source = i.split(":")[0]
                            target = i.split(":")[1]
                            rel_val = i.split(":")[2]

                            if source.startswith("e") and target.startswith("e"):
                                event_event_link.append((target, source, rel_val,))


    ############
    # extend with caevo data
    ###########

    for k, v in event_extent_data.items():
        file_id = v[0].split(".col.txt.xml")[0]
        for data, extra_link in caevo_dict.items():
            file_name, source, target = data
            if file_id == file_name:
                extra_link = (source,target,extra_link,)
                event_event_link.append(extra_link)


    postive_examples, negative_examples = generate_pos_neg_instance(event_same_sentence, event_event_link)
    distance_feat = add_distance(event_extent_data,postive_examples,negative_examples)
    shared_path = add_shared_path(distance_feat)
    signal_tokens = add_signal_tokens(shared_path, signal_list, sentence_lemmas)
    extra_event = check_extra_event(signal_tokens,event_tokens)

    return extra_event

def get_features(event_extent_dir, train_data_dir, tsignal_data, caevo_tlink_dict, outdir):

    for f in os.listdir(event_extent_dir):
        if f.endswith(".features.extent-train"):

            train_f = train_data_dir + f.split(".txt.xml.features.extent-train")[0]
            dataset_ = read_data(event_extent_dir + f, train_f, tsignal_data, caevo_tlink_dict)



            for k, v in dataset_.items():
                token_unique_id, file_name, sentence_id, id_per_sentence, token, lemma, pos_stanford, dependency_label, \
                dependent_lemma, dependent_pos, path2root1, path2root2, path2root3, path2root4, path2root5, ner_stanford,\
                timex_extent_bio, verbnet_classes, framenet_frames, wordnet_class, arguments, \
                timeml_tense, timeml_aspect, timeml_modality, timeml_polarity, \
                timeml_event_id, timel_event_class, \
                token_unique_id_target, file_name1, sentence_id1, id_per_sentence1, token_target, lemma_target, pos_stanford_target, dependency_label_target, \
                dependent_lemma_target, dependent_pos_target, path2root1_target, path2root2_target, path2root3_target, path2root4_target, path2root5_target, ner_stanford_target, \
                timex_extent_bio_target, verbnet_classes_target, framenet_frames_target, wordnet_class_tagret, arguments_target, \
                timeml_tense_target, timeml_aspect_target, timeml_modality_target, timeml_polarity_target, \
                timeml_event_id_target, timel_event_class_target, token_distance, tlink_val_original, shared_path1, shared_path2, shared_path3, source_path1, source_path2, source_path3, \
                target_path1, target_path2, target_path3, tlink_val_actual, signal_middle_sentence, signal_before_source, extra_events = v

                outfile = outdir + file_name + ".tlink-event-event-dect.train"
                outfile1 = outdir + file_name + ".tlink-event-event-class.train"
                output = open(outfile, 'a')
                output1 = open(outfile1, 'a')

                ##################################################
                # event_event_relation_features:
                # 0 file_id | 1 sentence-id | 2 unique-id-E1 | 3 sentence-token-Id-E1 | 4 token-E1 | 5 lemma-E1 | 6 pos-E1 |
                #  7 dep-rel-E1 | 8 gov-lemma-E1 | 9 pos-gov-E1 |
                # 10 vn-class-E1 | 11 fn-class-E1 | 12 wn-class | 13 E1-extent | 14 E1-class | 15 E1-tense
                # | 16 E1-aspect | 17 unique-id-E2 | 18 sentence-Id-E2 | 19 token-E2 |
                # 20 lemma-E2 | 21 pos-E2 | 22 dep-rel-E2 | 23 gov-lemma-E2 | 24 pos-gov-E2
                # | 25 vn-class-E2 | 26 fn-class-E2 | 27 wn-class-E2 | 28 E2-extent | 29 E2-class | 30 E2-tense
                # 31 E-aspect | 32 token-distance-E1-E2
                # | 33 common-path pos | 34 common-path dep-rel | 35 common-path pos+dep-rel
                # | 36 path-source pos | 37 path-source dep-rel | 38 path-source pos+dep-rel | 39 path-target pos |
                #  40 path-target dep-rel | 41 path-target pos+dep-rel | 42 token-signal-E1-E2 |
                # 43 token-signa before E1 | 44 other-events between E1-E2 |
                # 45 TLINK-existence
                #################################################

                if token_unique_id < token_unique_id_target:

                    if tlink_val_actual != "O":
                        output.writelines(file_name + "\t" + sentence_id + "\t" + str(token_unique_id) + "\t" + id_per_sentence + "\t" +
                                  token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                                  dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                                  framenet_frames + "\t" + wordnet_class + "\tB-EVENT\t" + timel_event_class + "\t" + timeml_tense + "\t" + timeml_aspect +
                                  "\t" + str(token_unique_id_target) + "\t" + sentence_id + "\t" + token_target + "\t" + lemma_target + "\t" +
                                      pos_stanford_target + "\t" + dependency_label_target + "\t" + dependent_lemma_target + "\t" +
                                      dependent_pos_target + "\t" + verbnet_classes_target + "\t" +
                                      framenet_frames_target + "\t" + wordnet_class_tagret + "\tB-EVENT\t" + timel_event_class_target + "\t" + timeml_tense_target +
                                          "\t" + timeml_aspect_target + "\t" + str(token_distance) + "\t" +
                                          shared_path1 + "\t" + shared_path2 + "\t" + shared_path3 + "\t" + source_path1 + "\t" +
                                      source_path2 + "\t" + source_path3 + "\t" + target_path1 + "\t" +
                                      target_path2 + "\t" + target_path3 + "\t" + signal_middle_sentence + "\t" + signal_before_source + "\t" + extra_events + "\tB-TLINK" + "\n")

                        output1.writelines(file_name + "\t" + sentence_id + "\t" + str(token_unique_id) + "\t" + id_per_sentence + "\t" +
                                  token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                                  dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                                  framenet_frames + "\t" + wordnet_class + "\tB-EVENT\t" + timel_event_class + "\t" + timeml_tense + "\t" + timeml_aspect +
                                  "\t" + str(token_unique_id_target) + "\t" + sentence_id + "\t" + token_target + "\t" + lemma_target + "\t" +
                                      pos_stanford_target + "\t" + dependency_label_target + "\t" + dependent_lemma_target + "\t" +
                                      dependent_pos_target + "\t" + verbnet_classes_target + "\t" +
                                      framenet_frames_target + "\t" + wordnet_class_tagret + "\tB-EVENT\t" + timel_event_class_target + "\t" + timeml_tense_target +
                                          "\t" + timeml_aspect_target + "\t" + str(token_distance) + "\t" +
                                          shared_path1 + "\t" + shared_path2 + "\t" + shared_path3 + "\t" + source_path1 + "\t" +
                                      source_path2 + "\t" + source_path3 + "\t" + target_path1 + "\t" +
                                      target_path2 + "\t" + target_path3 + "\t" + signal_middle_sentence + "\t" + signal_before_source + "\t" + extra_events + "\t" + tlink_val_actual + "\n")

                    else:

                        output.writelines(
                            file_name + "\t" + sentence_id + "\t" + str(token_unique_id) + "\t" + id_per_sentence + "\t" +
                            token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                            dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                            framenet_frames + "\t" + wordnet_class + "\tB-EVENT\t" + timel_event_class + "\t" + timeml_tense + "\t" + timeml_aspect +
                            "\t" + str(token_unique_id_target) + "\t" + sentence_id + "\t" + token_target + "\t" + lemma_target + "\t" +
                            pos_stanford_target + "\t" + dependency_label_target + "\t" + dependent_lemma_target + "\t" +
                            dependent_pos_target + "\t" + verbnet_classes_target + "\t" +
                            framenet_frames_target + "\t" + wordnet_class_tagret + "\tB-EVENT\t" + timel_event_class_target + "\t" + timeml_tense_target +
                            "\t" + timeml_aspect_target + "\t" + str(token_distance) + "\t" +
                            shared_path1 + "\t" + shared_path2 + "\t" + shared_path3 + "\t" + source_path1 + "\t" +
                            source_path2 + "\t" + source_path3 + "\t" + target_path1 + "\t" +
                            target_path2 + "\t" + target_path3 + "\t" + signal_middle_sentence + "\t" + signal_before_source + "\t" + extra_events + "\t" + tlink_val_actual + "\n"
                        )

                if token_unique_id > token_unique_id_target:

                    if tlink_val_actual != "O":
                        output.writelines(
                            file_name + "\t" + sentence_id + "\t" + str(token_unique_id_target) + "\t" + id_per_sentence1 + "\t" + token_target
                            + "\t" + lemma_target + "\t" + pos_stanford_target + "\t" + dependency_label_target + "\t"
                            + dependent_lemma_target + "\t" + dependent_pos_target + "\t" + verbnet_classes_target + "\t" +
                            framenet_frames_target + "\t" + wordnet_class_tagret + "\tB-EVENT\t" + timel_event_class_target + "\t" + timeml_tense_target +
                            "\t" + timeml_aspect_target + "\t" + str(token_unique_id) + "\t" + sentence_id + "\t" + token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                            dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                            framenet_frames + "\t" + wordnet_class + "\tB-EVENT\t" + timel_event_class + "\t" + timeml_tense + "\t" + timeml_aspect +
                            "\t" + str(token_distance) + "\t" +
                            shared_path1 + "\t" + shared_path2 + "\t" + shared_path3 + "\t" + source_path1 + "\t" +
                            source_path2 + "\t" + source_path3 + "\t" + target_path1 + "\t" +
                            target_path2 + "\t" + target_path3 + "\t" + signal_middle_sentence + "\t" + signal_before_source + "\t" + extra_events + "\tB-TLINK" + "\n")

                        output1.writelines(file_name + "\t" + sentence_id + "\t" + str(token_unique_id_target) + "\t" + id_per_sentence1 + "\t" + token_target
                            + "\t" + lemma_target + "\t" + pos_stanford_target + "\t" + dependency_label_target + "\t"
                            + dependent_lemma_target + "\t" + dependent_pos_target + "\t" + verbnet_classes_target + "\t" +
                            framenet_frames_target + "\t" + wordnet_class_tagret + "\tB-EVENT\t" + timel_event_class_target + "\t" + timeml_tense_target +
                            "\t" + timeml_aspect_target + "\t" + str(token_unique_id) + "\t" + sentence_id + "\t" + token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                            dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                            framenet_frames + "\t" + wordnet_class + "\tB-EVENT\t" + timel_event_class + timeml_tense + "\t" + timeml_aspect +
                            "\t" + str(token_distance) + "\t" + shared_path1 + "\t" + shared_path2 + "\t" + shared_path3 + "\t" + source_path1 + "\t" +
                            source_path2 + "\t" + source_path3 + "\t" + target_path1 + "\t" +
                            target_path2 + "\t" + target_path3 + "\t" + signal_middle_sentence + "\t" + signal_before_source + "\t" + extra_events + "\t" + tlink_val_actual + "\n")

                    else:

                        output.writelines(
                            file_name + "\t" + sentence_id + "\t" + str(token_unique_id_target) + "\t" + id_per_sentence1 + "\t" + token_target
                            + "\t" + lemma_target + "\t" + pos_stanford_target + "\t" + dependency_label_target + "\t"
                            + dependent_lemma_target + "\t" + dependent_pos_target + "\t" + verbnet_classes_target + "\t" +
                            framenet_frames_target + "\t" + wordnet_class_tagret + "\tB-EVENT\t" + timel_event_class_target + "\t" + timeml_tense_target +
                            "\t" + timeml_aspect_target + "\t" + str(token_unique_id) + "\t" + sentence_id + "\t" + token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                            dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                            framenet_frames + "\t" + wordnet_class + "\tB-EVENT\t" + timel_event_class + timeml_tense + "\t" + timeml_aspect +
                            "\t" + str(token_distance) + "\t" + shared_path1 + "\t" + shared_path2 + "\t" + shared_path3 + "\t" + source_path1 + "\t" +
                            source_path2 + "\t" + source_path3 + "\t" + target_path1 + "\t" +
                            target_path2 + "\t" + target_path3 + "\t" + signal_middle_sentence + "\t" + signal_before_source + "\t" + extra_events + "\t" + tlink_val_actual + "\n")

                output.close()
                output1.close()


        else:
            continue




def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 4:
        print('Usage: python3 tlink_features_event_timex_train.py [event_extent_train_features_dir] [annotated_data_colFormat_dir] tlink_signal_file caevo_tlink_file outdir')
    else:
        tsignal_data = tsignal_read(argv[3])
        caevo_tlink = caevo_read(argv[4])
        merge_data = get_features(argv[1], argv[2], tsignal_data, caevo_tlink, argv[5])

if __name__ == '__main__':
    main()