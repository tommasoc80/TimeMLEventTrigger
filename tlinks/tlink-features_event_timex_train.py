# -*- coding: UTF-8 -*- 
import sys
import collections
import os, os.path, re

#from KafNafParserPy import *


#################################
# Extract TRAINING features for TLINK EVENT-TIMEX - same sentence
# Author: Tommaso Caselli
#
# Generate training data for TLINK between event and timex in the same sentence only
##################################

def tsignal_read(tlinkf):
    signal_list = []

    with open(tlinkf) as f:
        for line in f:
            line_stripped = line.strip()
            entry = line_stripped.replace(' ', '_')
            signal_list.append(entry)

    return signal_list

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

def generate_pos_neg_instance(timex_features_dict, event_same_sentence, event_timex_link):


    positive_examples = {}
    negative_examples = {}

    same_sentence_event_timex = []
    for timex_id, timex_feat in timex_features_dict.items():
        sentence_id, timex_val, timex_, token_id  = timex_id

        if sentence_id in event_same_sentence:
            event_list_id = event_same_sentence[sentence_id]

            for elem in event_list_id:

                same_sentence_event_timex.append((elem, timex_,))


    for entry in event_timex_link:
        event, timex, tlink_val = entry
        match = (event, timex,)
        if match in same_sentence_event_timex:
            positive_examples[(event, timex,)] = tlink_val

    for entry in same_sentence_event_timex:
        if entry not in positive_examples:
            negative_examples[entry] = "O"


    return positive_examples, negative_examples


def add_distance(event_extent_data_dict,timex_features_dict,postive_examples_dict,negative_examples_dict):


    feature_merge = {}
    for k, v in event_extent_data_dict.items():
        file_name, sentence_id, id_per_sentence, token, lemma, pos_stanford, dependency_label, dependent_lemma, \
        dependent_pos, path2root1, path2root2, path2root3, path2root4, path2root5, ner_stanford, timex_extent_bio, verbnet_classes, \
        framenet_frames, wordnet_class, arguments, \
        timeml_tense, timeml_aspect, timeml_modality, timeml_polarity, \
        timeml_event_id, tieml_event_bio = v

        for timex_id, timex_feat in timex_features_dict.items():
            sentence_id, timex_val, timex_, token_id = timex_id

            match = (timeml_event_id, timex_,)
            if match in postive_examples_dict:
                distance = abs(k - int(token_id))
                feature_merge[match] = (str(k),) + v + timex_feat +(token_id,timex_val,distance,postive_examples_dict[match])
            if match in negative_examples_dict:
                distance = abs(k - int(token_id))
                feature_merge[match] = (str(k),) + v + timex_feat + (token_id,timex_val, distance, negative_examples_dict[match])

    return feature_merge


def add_shared_path(distance_feat_dict):

    for k, v in distance_feat_dict.items():
        event_token_id = int(v[0])
        timex_token_id = int(v[-4])
        event_token_path = v[12]
        timex_token_path = v[35]
        event_lemma = v[5]
        timex_lemma = v[28]


        #print(v[37])

        if event_token_id < timex_token_id:
            timex_token_path_split = timex_token_path.split("_")
            if event_lemma in timex_token_path_split:
                index_split = timex_token_path_split.index(event_lemma)
                pos_path = "_".join((v[34].split("_")[0:index_split]))
                dep_path = "_".join((v[36].split("_")[0:index_split]))
                dep_pos_path_list = list(zip(v[34].split("_")[0:index_split], v[36].split("_")[0:index_split]))
                dep_pos_path_string = '_'.join(map(str,["_".join(entry) for entry in dep_pos_path_list]))
                new_val = v + (pos_path,dep_path,dep_pos_path_string,"O", "O", "O","O", "O", "O")
                distance_feat_dict[k] = new_val
            else:
                reversed_timex_pos = "_".join(reversed(v[34].split("_")))
                reversed_timex_dep = "_".join(reversed(v[36].split("_")))
                pos_path_timex_list = list(zip(reversed(v[34].split("_")), reversed(v[36].split("_"))))
                pos_dep_path_string_tmx = '_'.join(map(str,["_".join(entry) for entry in pos_path_timex_list]))

                dep_pos_path_list_event = list(zip(v[11].split("_"), v[13].split("_")))
                dep_pos_path_string_event = '_'.join(map(str,["_".join(entry) for entry in dep_pos_path_list_event]))

                new_val = v + ("O", "O", "O",v[11],v[13],dep_pos_path_string_event,reversed_timex_pos,reversed_timex_dep,pos_dep_path_string_tmx)
                distance_feat_dict[k] = new_val

        if event_token_id > timex_token_id:
            event_token_path_split = event_token_path.split("_")
            if timex_lemma in event_token_path_split:
                index_split = event_token_path_split.index(event_lemma)
                pos_path = "_".join((v[11].split("_")[0:index_split]))
                dep_path = "_".join((v[13].split("_")[0:index_split]))
                dep_pos_path_list = list(zip(v[11].split("_")[0:index_split], v[13].split("_")[0:index_split]))
                dep_pos_path_string = '_'.join(map(str, ["_".join(entry) for entry in dep_pos_path_list]))
                new_val = v + (pos_path, dep_path, dep_pos_path_string, "O", "O", "O","O", "O", "O")
                distance_feat_dict[k] = new_val
            else:
                #reversed_event_pos = "_".join(reversed(v[11].split("_")))
                #reversed_event_dep = "_".join(reversed(v[13].split("_")))
                #pos_path_event_list = list(zip(reversed(v[11].split("_")), reversed(v[13].split("_"))))
                #pos_dep_path_string_event = '_'.join(map(str, ["_".join(entry) for entry in pos_path_event_list]))

                #dep_pos_path_list_tmx = list(zip(v[34].split("_"), v[36].split("_")))
                #dep_pos_path_string_tmx = '_'.join(map(str, ["_".join(entry) for entry in dep_pos_path_list_tmx]))

                reversed_timex_pos = "_".join(reversed(v[34].split("_")))
                reversed_timex_dep = "_".join(reversed(v[36].split("_")))
                pos_path_timex_list = list(zip(reversed(v[34].split("_")), reversed(v[36].split("_"))))
                pos_dep_path_string_tmx = '_'.join(map(str, ["_".join(entry) for entry in pos_path_timex_list]))

                dep_pos_path_list_event = list(zip(v[11].split("_"), v[13].split("_")))
                dep_pos_path_string_event = '_'.join(map(str, ["_".join(entry) for entry in dep_pos_path_list_event]))

                new_val = v + (
                "O", "O", "O", v[11],v[13],
                dep_pos_path_string_event, reversed_timex_pos, reversed_timex_dep, pos_dep_path_string_tmx,)
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
    sentence_start = {}
    for tlink_pairs, features in data_features_dict.items():
        sentence_id = features[2]

        if sentence_id in tlink_signals:
            for entry in tlink_signals[sentence_id]:
                token_id, sentence_token_id, lemma = entry
                if token_id > features[0] and token_id < features[-7]:
                    middle_signal[tlink_pairs].append(lemma)
                elif token_id < features[0] and token_id > features[-7]:
                    middle_signal[tlink_pairs].append(lemma)
                else:
                    if int(sentence_token_id) ==  1:
                        sentence_start[tlink_pairs] = lemma

    for tlink_pairs, features in data_features_dict.items():

        if tlink_pairs in middle_signal:
            string_signal = "_".join(middle_signal[tlink_pairs])
            new_val = features + (string_signal,)
            data_features_dict[tlink_pairs] = new_val
        else:
            new_val = features + ("O",)
            data_features_dict[tlink_pairs] = new_val


    for tlink_pairs, features in data_features_dict.items():

        if tlink_pairs in sentence_start:
            signal_lemma = sentence_start[tlink_pairs]
            new_val = features + (signal_lemma,)
            data_features_dict[tlink_pairs] = new_val
        else:
            new_val = features + ("O",)
            data_features_dict[tlink_pairs] = new_val

    return data_features_dict

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

def read_data(event_extentf, trainf, signal_list):

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

    timex_sentence = collections.defaultdict(list)
    timex_type = {}
    event_same_sentence = collections.defaultdict(list)
    event_timex_link = []

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


                ################
                # timex class
                ################

                if timexType.startswith("B-"):
                    timex_type[timexId] = timexType

                ##########################
                # timex per sentence
                ##########################
                if timexVal != "O":
                    timex_sentence[(sentence_id, timexVal, timexId,)].append(token_id)

                ##########################
                # event in the same sentence
                ##########################
                if event_id != "O":
                    event_same_sentence[sentence_id].append(event_id)

                """
                TLINK
                """

                if tLink != "O":
                    if "||" not in tLink:

                        tlink_elem = tLink.split(":")

                        source = tlink_elem[0]
                        target = tlink_elem[1]
                        rel_val = tlink_elem[2]

                        if source.startswith("t") and source != "tmx0" and target.startswith("e"):
                            new_rel_val = change_rel_val(rel_val)
                            event_timex_link.append((target, source, new_rel_val,))
                        if source.startswith("e") and target.startswith("t") and target != "tmx0":
                            event_timex_link.append((source, target, rel_val,))

                    else:
                        tlink_elem = tLink.split("||")
                        for i in tlink_elem:

                            source = i.split(":")[0]
                            target = i.split(":")[1]
                            rel_val = i.split(":")[2]

                            if source.startswith("e") and target.startswith("t") and target != "tmx0":
                                event_timex_link.append((source, target, rel_val,))

                            if source.startswith("t") and source != "tmx0" and target.startswith("e"):
                                new_rel_val = change_rel_val(rel_val)
                                event_timex_link.append((target, source, new_rel_val,))


    timex_features = get_timex_features(timex_sentence, timex_type, event_extent_data)
    postive_examples, negative_examples = generate_pos_neg_instance(timex_features, event_same_sentence, event_timex_link)
    distance_feat = add_distance(event_extent_data,timex_features,postive_examples,negative_examples)

    shared_path = add_shared_path(distance_feat)
    signal_tokens = add_signal_tokens(shared_path, signal_list, sentence_lemmas)

    return signal_tokens

def get_features(event_extent_dir, train_data_dir, tsignal_data, outdir):

    for f in os.listdir(event_extent_dir):
        if f.endswith(".features.extent-train"):

            train_f = train_data_dir + f.split(".txt.xml.features.extent-train")[0]
            dataset_ = read_data(event_extent_dir + f, train_f, tsignal_data)


            for k, v in dataset_.items():
                token_unique_id, file_name, sentence_id, id_per_sentence, token, lemma, pos_stanford, dependency_label, \
                dependent_lemma, dependent_pos, path2root1, path2root2, path2root3, path2root4, path2root5, ner_stanford,\
                timex_extent_bio, verbnet_classes, framenet_frames, wordnet_class, arguments, \
                timeml_tense, timeml_aspect, timeml_modality, timeml_polarity, \
                timeml_event_id, timel_event_class, timex_token, timex0_lemma, pos_tmx, dependency_label_tmx, dependent_lemma_tmx,\
                dependent_pos_tmx, path2root1_tmx, path2root2_tmx, path2root3_tmx, path2root4_tmx,\
                path2root5_tmx, ner_tmx, timeml_timex_bio, verbnet_classes_tmx, framenet_frames_tmx, wordnet_class_tmx,\
                arg_tmx, event_data_tmx_tense, event_data_tmx_aspect, event_data_tmx_modality, event_data_tmx_polarity, \
                event_data_tmx_id, event_data_tmx_class, timex_type, timex_0_token_unique,\
                timex_val, token_distance, tlink_val, shared_path1, shared_path2, shared_path3, source_path1, source_path2, source_path3, \
                target_path1, target_path2, target_path3, signal_middle_sentence, signal_sentence_begin = v

                outfile = outdir + file_name + ".tlink-event-timex-dect.train"
                outfile1 = outdir + file_name + ".tlink-event-timex-class.train"
                output = open(outfile, 'a')
                output1 = open(outfile1, 'a')

                ##################################################
                # event_timex_relation_features:
                # 0 file_id | 1 sentence-id | 2 unique-id-E1 | 3 sentence-token-Id-E1 | 4 token-E1 | 5 lemma-E1 | 6 pos-E1
                # | 7 dep-rel-E1 | 8 gov-lemma-E1 | 9 pos-gov-E1 |
                # 10 vn-class-E1 | 11 fn-class-E1 | 12 wn-class | 13 E1-tense | 14 E1-aspect | 15 E1-class | 16 token-timex |
                # 17 pos-timex | 18 dep-rel-timex | 19 gov-lemma-timex | 20 pos-gov-timex | 21 timex-class
                # |  22 vn-class-E2 | 23 fn-class-E2 | 24 wn-class-E2 | 25 token-distance-E1-E2
                # | 26 common-path pos | 27 common-path dep-rel | 28 common-path pos+dep-rel
                # | 29 path-source pos | 30 path-source dep-rel | 31 path-source pos+dep-rel
                # | 32 path-target pos | 33 path-target dep-rel | 34 path-target pos+dep-rel
                # | 35 token-signal-E1-E2 | 36 token-signal begin S |
                # 37 TLINK - TLINK Class
                #################################################

                if tlink_val != "O":
                    output.writelines(file_name + "\t" + sentence_id + "\t" + token_unique_id + "\t" + id_per_sentence + "\t" +
                                  token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                                  dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                                  framenet_frames + "\t" + wordnet_class + "\t" + timeml_tense + "\t" + timeml_aspect +
                                  "\t" + timel_event_class + "\t" + timex_token + "\t" + timex0_lemma + "\t" +
                                      pos_tmx + "\t" + dependency_label_tmx + "\t" + dependent_lemma_tmx + "\t" +
                                      dependent_pos_tmx + "\t" + timex_type + "\t" + verbnet_classes_tmx + "\t" +
                                      framenet_frames_tmx + "\t" + wordnet_class_tmx + "\t" + str(token_distance) + "\t" +
                                          shared_path1 + "\t" + shared_path2 + "\t" + shared_path3 + "\t" + source_path1 + "\t" +
                                      source_path2 + "\t" + source_path3 + "\t" + target_path1 + "\t" +
                                      target_path2 + "\t" + target_path3 + "\t" + signal_middle_sentence + "\t" + signal_sentence_begin + "\tB-TLINK" + "\n")

                    output1.writelines(file_name + "\t" + sentence_id + "\t" + token_unique_id + "\t" + id_per_sentence + "\t" +
                                  token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                                  dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                                  framenet_frames + "\t" + wordnet_class + "\t" + timeml_tense + "\t" + timeml_aspect +
                                  "\t" + timel_event_class + "\t" + timex_token + "\t" + timex0_lemma + "\t" +
                                      pos_tmx + "\t" + dependency_label_tmx + "\t" + dependent_lemma_tmx + "\t" +
                                      dependent_pos_tmx + "\t" + timex_type + "\t" + verbnet_classes_tmx + "\t" +
                                      framenet_frames_tmx + "\t" + wordnet_class_tmx + "\t" + str(token_distance) + "\t" +
                                          shared_path1 + "\t" + shared_path2 + "\t" + shared_path3 + "\t" + source_path1 + "\t" +
                                      source_path2 + "\t" + source_path3 + "\t" + target_path1 + "\t" +
                                      target_path2 + "\t" + target_path3 + "\t" + signal_middle_sentence + "\t" + signal_sentence_begin + "\t" + tlink_val + "\n")

                else:

                    output.writelines(
                        file_name + "\t" + sentence_id + "\t" + token_unique_id + "\t" + id_per_sentence + "\t" +
                        token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                        dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                        framenet_frames + "\t" + wordnet_class + "\t" + timeml_tense + "\t" + timeml_aspect +
                        "\t" + timel_event_class + "\t" + timex_token + "\t" + timex0_lemma + "\t" +
                        pos_tmx + "\t" + dependency_label_tmx + "\t" + dependent_lemma_tmx + "\t" +
                        dependent_pos_tmx + "\t" + timex_type + "\t" + verbnet_classes_tmx + "\t" +
                        framenet_frames_tmx + "\t" + wordnet_class_tmx + "\t" + str(token_distance) + "\t" +
                        shared_path1 + "\t" + shared_path2 + "\t" + shared_path3 + "\t" + source_path1 + "\t" +
                        source_path2 + "\t" + source_path3 + "\t" + target_path1 + "\t" +
                        target_path2 + "\t" + target_path3 + "\t" + signal_middle_sentence + "\t" + signal_sentence_begin + "\t" + tlink_val + "\n")

                output.close()
                output1.close()


        else:
            continue




def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 4:
        print('Usage: python3 tlink_features_event_timex_train.py [event_extent_train_features_dir] [annotated_data_colFormat_dir] tlink_signal_file outdir')
    else:
        tsignal_data = tsignal_read(argv[3])
        merge_data = get_features(argv[1], argv[2], tsignal_data, argv[4])

if __name__ == '__main__':
    main()