# -*- coding: UTF-8 -*- 
import sys, os, os.path
import collections

#from KafNafParserPy import *


#################################
# Extract TRAINING features for TLINK EVENT-DCT
# Author: Tommaso Caselli 2018
#
# Generate training files for detections and classification of TLINK betweeb events and DCT
##################################

def generate_pos_instance(event_data, dct_data, event_dct_list):

    positive_example_event_dct = {}
    for k, v in event_data.items():

        file_name, sentence_id, id_per_sentence, token, lemma, pos_stanford, dependency_label, dependent_lemma, \
        dependent_pos, path2root1, path2root2, path2root3, path2root4, path2root5, ner_stanford, timex_extent_bio, verbnet_classes, \
        framenet_frames, wordnet_class, arguments, \
        timeml_tense, timeml_aspect, timeml_modality, timeml_polarity, \
        timeml_event_id, tieml_event_bio = v

        for entry in event_dct_list:
            event_id, dct_id, tlink_val = entry

            dct_timemlid, dct_token_id, dct_sentence, dct_token_sentence, dct_type, dct_val = dct_data

            if timeml_event_id == event_id:
                positive_example_event_dct[k] = v + (dct_type, tlink_val,)

    return positive_example_event_dct


def generate_neg_instance(event_data, positive_examples, dct_data):

    negative_example_event_dct = {}

    for k, v in event_data.items():
        file_name, sentence_id, id_per_sentence, token, lemma, pos_stanford, dependency_label, dependent_lemma, \
        dependent_pos, path2root1, path2root2, path2root3, path2root4, path2root5, ner_stanford, timex_extent_bio, verbnet_classes, \
        framenet_frames, wordnet_class, arguments, \
        timeml_tense, timeml_aspect, timeml_modality, timeml_polarity, \
        timeml_event_id, tieml_event_bio = v

        if k not in positive_examples:
            if timeml_event_id != "O":
                dct_timemlid, dct_token_id, dct_sentence, dct_token_sentence, dct_type, dct_val = dct_data

                negative_example_event_dct[k] = v + (dct_type, "O",)

    return negative_example_event_dct

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

def read_data(event_extentf, trainf):

    event_extent_data = {}
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

    event_dct_tlink = []
    dct = None
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


                """
                DCT info
                """

                if timexId == "tmx0":
                    if int(token_id) in event_extent_data:
                        dct = (timexId,token_id,event_extent_data[int(token_id)][1],event_extent_data[int(token_id)][2], timexType,timexVal,)
                """
                TLINK
                """

                if tLink != "O":
                    if "||" not in tLink:

                        tlink_elem = tLink.split(":")

                        source = tlink_elem[0]
                        target = tlink_elem[1]
                        rel_val = tlink_elem[2]

                        if source == "tmx0" and target.startswith("e"):
                            new_rel_val = change_rel_val(rel_val)
                            event_dct_tlink.append((target, source, new_rel_val,))
                        if source.startswith("e") and target == "tmx0":
                            event_dct_tlink.append((source, target, rel_val,))

                    else:
                        tlink_elem = tLink.split("||")
                        for i in tlink_elem:

                            source = i.split(":")[0]
                            target = i.split(":")[1]
                            rel_val = i.split(":")[2]

                            if source.startswith("e") and target == "tmx0":
                                event_dct_tlink.append((source, target, rel_val,))

                            if source == "tmx0" and target.startswith("e") :
                                new_rel_val = change_rel_val(rel_val)
                                event_dct_tlink.append((target, source, new_rel_val,))


    postive_examples_event_dtc = generate_pos_instance(event_extent_data, dct, event_dct_tlink)
    negative_examples_event_dtc = generate_neg_instance(event_extent_data, postive_examples_event_dtc, dct)

    return postive_examples_event_dtc, negative_examples_event_dtc


def get_features(event_extent_dir, train_data_dir, outdir):

    for f in os.listdir(event_extent_dir):
        if f.endswith(".features.extent-train"):

            train_f = train_data_dir + f.split(".txt.xml.features.extent-train")[0]
            dataset_pos_examples, dataset_neg_examples = read_data(event_extent_dir + f, train_f)
            out_data = dataset_pos_examples.copy()
            out_data.update(dataset_neg_examples)

            for k, v in out_data.items():

                file_name, sentence_id, id_per_sentence, token, lemma, pos_stanford, dependency_label, dependent_lemma, \
                dependent_pos, path2root1, path2root2, path2root3, path2root4, path2root5, ner_stanford, timex_extent_bio, verbnet_classes, \
                framenet_frames, wordnet_class, arguments, \
                timeml_tense, timeml_aspect, timeml_modality, timeml_polarity, \
                timeml_event_id, tieml_event_bio, dct_type, dct_tlink_val  = v

                outfile = outdir + file_name + ".tlink-event-DCT-dect.train"
                outfile1 = outdir + file_name + ".tlink-event-DCT-class.train"
                output = open(outfile, 'a')
                output1 = open(outfile1, 'a')

                ##################################################
                # event_dct_relation_features:
                # 0 file id / 1 sentence id /
                # 2 token id / 3 token_sentence id / 4 event_token / 5 event lemma /
                # 6 event pos / 7 event deprel / 8 event gove lemma / 9 event gov pos /
                # 10 VN class / 11 FN class / 12 WN class / 13 event-class /
                # 14 dct-type / 15 TLINK
                #################################################

                if dct_tlink_val != "O":
                    output.writelines(file_name + "\t" + sentence_id + "\t" + str(k) + "\t" + id_per_sentence + "\t" +
                                  token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                                  dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                                  framenet_frames + "\t" + wordnet_class + "\t" + timeml_tense + "\t" + timeml_aspect +
                                  "\t" + dct_type + "\tB-TLINK" + "\n")
                    output1.writelines(file_name + "\t" + sentence_id + "\t" + str(k) + "\t" + id_per_sentence + "\t" +
                                  token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                                  dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                                  framenet_frames + "\t" + wordnet_class + "\t" + timeml_tense + "\t" + timeml_aspect +
                                  "\t" + dct_type + "\t" + dct_tlink_val + "\n")

                else:
                    output.writelines(file_name + "\t" + sentence_id + "\t" + str(k) + "\t" + id_per_sentence + "\t" +
                                      token + "\t" + lemma + "\t" + pos_stanford + "\t" + dependency_label + "\t" +
                                      dependent_lemma + "\t" + dependent_pos + "\t" + verbnet_classes + "\t" +
                                      framenet_frames + "\t" + wordnet_class + "\t" + timeml_tense + "\t" + timeml_aspect +
                                      "\t" + dct_type + "\t" + dct_tlink_val + "\n")

                output.close()
                output1.close()

        else:
            continue




def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 4:
        print('Usage: python3 tlink_features_event_DCT_train.py [event_extent_train_features_dir] [annotated_data_colFormat_dir] outdir')
    else:
        merge_data = get_features(argv[1], argv[2], argv[3])

if __name__ == '__main__':
    main()