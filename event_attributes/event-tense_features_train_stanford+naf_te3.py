import sys
import os, os.path
import collections
from lxml import etree


def previous_and_next(l,n=2):
    empty = ["O|O|O"] * n #changed field separator from # to |
    l2 = empty + l + empty
    for i in range(n,len(l)+n):
        yield l2[i-n:i+n+1]
    return l2


parents = dict()
def get_path2root(parents, key):
    path_to_root = []
    continue_path = True

    while continue_path:
        if key in parents:
            parent = parents[key]
            path_to_root.append(key)
            key = parent
        else:
            continue_path = False
    return path_to_root


def predicate_verb_vn(predicateMatrix):
    vn = {}

    fileObject = open(predicateMatrix)
    for line in fileObject:
        line_stripped = line.strip()
        line_splitted = line_stripped.split("\t")

        VN_CLASS = line_splitted[0].replace('vn:', '')
        VN_LEMMA = line_splitted[4].replace('vn:', '')

        if VN_CLASS != "NULL" :
            if VN_LEMMA in vn:
                list_value_type = vn[VN_LEMMA]
                if VN_CLASS not in list_value_type:
                    list_value_type.append(VN_CLASS)
            else:
                list_value_type = []
                list_value_type.append(VN_CLASS)
            vn[VN_LEMMA] = sorted(list_value_type)

    fileObject.close()
    return vn

def predicate_verb_fn(predicateMatrix):
    fn = {}

    fileObject = open(predicateMatrix)
    for line in fileObject:
        line_stripped = line.strip()
        line_splitted = line_stripped.split("\t")

        VN_LEMMA = line_splitted[4].replace('vn:', '')
        FN_FRAME = line_splitted[8].replace('fn:', '')

        if FN_FRAME != "NULL":
            if VN_LEMMA in fn:
                list_value_type = fn[VN_LEMMA]
                if FN_FRAME not in list_value_type:
                    list_value_type.append(FN_FRAME)
            else:
                list_value_type = []
                list_value_type.append(FN_FRAME)
            fn[VN_LEMMA] = sorted(list_value_type)

    fileObject.close()
    return fn


def predicate_verb_wn(predicateMatrix):
    wn_verb = {}

    fileObject = open(predicateMatrix)
    for line in fileObject:
        line_stripped = line.strip()
        line_splitted = line_stripped.split("\t")

        MCR_LEXNAME = line_splitted[17].replace('mcr:', '')
        VN_LEMMA = line_splitted[4].replace('vn:', '')

        if MCR_LEXNAME != "NULL":
            if VN_LEMMA in wn_verb:
                list_value_type = wn_verb[VN_LEMMA]
                if MCR_LEXNAME not in list_value_type:
                    list_value_type.append(MCR_LEXNAME)
            else:
                list_value_type = []
                list_value_type.append(MCR_LEXNAME)
            wn_verb[VN_LEMMA] = sorted(list_value_type)

    fileObject.close()
    return wn_verb



def wn_supersense(wn_supersenses):
    wn = {}

    fileObject = open(wn_supersenses)
    for line in fileObject:
        line_stripped = line.strip()
        line_splitted = line_stripped.split("\t")

        word = line_splitted[0].lower()
        supersense = line_splitted[3]

        if word in wn:
            list_value_type = wn[word]
            if supersense not in list_value_type:
                list_value_type.append(supersense)
        else:
            list_value_type = []
            list_value_type.append(supersense)
        wn[word] = sorted(list_value_type)

    fileObject.close()
    return wn


def process_train(train_f):
    train_data = {}

    fileObject = open(train_f)
    for line in fileObject:
        line_stripped = line.strip()
        line_splitted = line_stripped.split("\t")

        if len(line_splitted) > 1:
            token = line_splitted[0]
            token_id = line_splitted[1]
            sentence_id = line_splitted[2]

            event_id = line_splitted[3]
#            event_class = line_splitted[4].replace('B-OCCURRENCE', 'B-EVENT').replace('B-I_ACTION', 'B-EVENT').replace('B-STATE', 'B-EVENT').replace('B-ASPECTUAL', 'B-EVENT').replace('B-I_STATE', 'B-EVENT').replace('B-REPORTING', 'B-EVENT').replace('B-PERCEPTION', 'B-EVENT')
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


            token_id_align = int(token_id)

            if token_id_align == -99:
                train_data[0] = (tense, aspect, modality, polarity, event_id, tense)
            else:
                train_data[token_id_align] = (tense, aspect, modality, polarity, event_id, tense)


    fileObject.close()
    return train_data



def process_feature_naf(naf_f):

    doc = etree.parse(naf_f, etree.XMLParser(remove_blank_text=True))
    root = doc.getroot()
    root.getchildren()


    predicate_term = {}
    predicate_roles =  collections.defaultdict(list)

    for elem in root.iter("srl"):
        for srl in elem.findall("predicate"):
            predicate_id = srl.attrib.get("id", "null")
            for term in srl.findall("span"):
                for term_id in term.findall("target"):
                    predicte_term = term_id.attrib.get("id", "null").replace('t', '')
                    predicate_term[predicate_id] = predicte_term

            for role in srl.findall("role"):
                role_id = role.attrib.get("id", "null")
                role_type = role.attrib.get("semRole", "null")
                for role_span in  role.findall("span"):
                    for role_term in role_span.findall("target"):
                        role_span_id = role_term.attrib.get("id", "null").replace('t', '')
                        predicate_roles[predicate_id + "\t" + role_type + "\t" + role_id].append(role_span_id)

    predicate_argument_final = {}
    for k,v in predicate_roles.items():
        k_splitted = k.split("\t")
        if k_splitted[0] in predicate_term:
            new_val = tuple(v)
            predicate_argument_final[predicate_term[k_splitted[0]] + "\t" + "\t".join(k_splitted[1:])] = new_val

    return predicate_argument_final



def process_features_stanford(stanfordf, naf_f,  train_f, predicateMatrix, wn_supersenses, outfile):

    doc = etree.parse(stanfordf, etree.XMLParser(remove_blank_text=True))
    root = doc.getroot()
    root.getchildren()

    """
    sentence, token, lemma, pos, NER
    """

    word_token = {}
    dependency_dict = {}
    timex_dict = collections.defaultdict(list)
    token_list_sentence = collections.defaultdict(list)
    counter = 0


    for sent in root.iter('sentence'):

        for token in sent.iter('token'):
            counter += 1
            sentence_id = sent.attrib.get("id", "null")
            token_sentence_id = token.attrib.get("id", "null")

            token_list_sentence[sentence_id].append(str(counter) + "|" + token.getchildren()[1].text + "|" + token.getchildren()[4].text)


            if token.getchildren()[5].text == "O":
                word_token[sentence_id + "\t" + token_sentence_id] = (
                str(counter), token.getchildren()[0].text, token.getchildren()[1].text, token.getchildren()[4].text,
                token.getchildren()[5].text, token.getchildren()[5].text)

            elif token.getchildren()[5].text == "DATE":
                word_token[sentence_id + "\t" + token_sentence_id] = (
                str(counter), token.getchildren()[0].text, token.getchildren()[1].text, token.getchildren()[4].text,
                "O", token.getchildren()[5].text)

            elif token.getchildren()[5].text == "DURATION":
                word_token[sentence_id + "\t" + token_sentence_id] = (
                str(counter), token.getchildren()[0].text, token.getchildren()[1].text, token.getchildren()[4].text,
                "O", token.getchildren()[5].text)

            elif token.getchildren()[5].text == "TIME":
                word_token[sentence_id + "\t" + token_sentence_id] = (
                str(counter), token.getchildren()[0].text, token.getchildren()[1].text, token.getchildren()[4].text,
                "O", token.getchildren()[5].text)

            elif token.getchildren()[5].text == "SET":
                word_token[sentence_id + "\t" + token_sentence_id] = (
                str(counter), token.getchildren()[0].text, token.getchildren()[1].text, token.getchildren()[4].text,
                "O", token.getchildren()[5].text)

            else:
                word_token[sentence_id + "\t" + token_sentence_id] = (
                str(counter), token.getchildren()[0].text, token.getchildren()[1].text, token.getchildren()[4].text,
                token.getchildren()[5].text, "O")



            for timex in token.findall("Timex"):
                timex_id = timex.attrib.get("tid", "null")
                timex_dict[timex_id].append(sentence_id + "\t" + token_sentence_id)


        #########################
        ## - dependencies
        #########################

        for dep in sent.iter('dependencies'):
            if dep.attrib.get("type","null") == "basic-dependencies":
                for deprel in dep.iter('dep'):
                    for gov in deprel.iter('governor'):
                        for dep in deprel.iter('dependent'):
                            key = sentence_id + "\t" + dep.attrib.get("idx", "null") + "\t" + deprel.attrib.get("type", "null")
                            values = gov.attrib.get("idx", "null")
                            dependency_dict[key] = values

#########################
## - add dependency to token and POS
#########################

    token_dependency = {}

    for k, v in word_token.items():
        for k1, v1 in dependency_dict.items():
            k1_splitted = k1.split("\t")
            key_dep = k1_splitted[0] + "\t" + k1_splitted[1]
            if key_dep == k:
                new_v = v + (k1_splitted[2], v1,)
                token_dependency[k] = new_v


    for k, v in word_token.items():
        if k not in token_dependency:
            new_v = v + ("_", "_",)
            token_dependency[k] = new_v


#########################
## - solve timex to BIO-format
#########################

    for k, v in token_dependency.items():

        for k1, v1 in timex_dict.items():
            if len(v1) > 1:
                if k == v1[0]:
                    new_val = v[:5] + ("B-TIMEX",) + v[6:]
                    token_dependency[k] = new_val

                for i in range(1, len(v1)):
                    val = v1[i]
                    if val == k:
                        new_val = v[:5] + ("I-TIMEX",) + v[6:]
                        token_dependency[k] = new_val

            else:
                if k in v1:
                    new_val = v[:5] + ("B-TIMEX",) + v[6:]
                    token_dependency[k] = new_val



######################
## -  path2root - dependencies
######################

    path = {}

    for k, v in token_dependency.items():
        k_splitted = k.split("\t")
        sentence_id = k_splitted[0]
        token_per_sentence = k_splitted[1]

        if v[7] != "_":
            path[sentence_id + "#" + token_per_sentence] = sentence_id + "#" + v[7]

    path2root = {}
    path2root_solved = {}

    for k, v in path.items():
        path2root[k] = get_path2root(path, k)

    for k, v in path2root.items():
        k_splitted = k.split("#")
        sentence_id_path = k_splitted[0]

        for k1, v1 in token_dependency.items():
            k1_splitted = k1.split("\t")
            match = k1_splitted[0] + "#" + k1_splitted[1]

            if str(sentence_id_path) == str(k1_splitted[0]):
                for n, i in enumerate(v):
                    if str(i) == str(match):
                        match_full = v1[2] + "|" + v1[3] + "|" + v1[6]
                        v[n] = match_full
                        path2root_solved[k] = tuple(v)

    for k, v in path2root_solved.items():
        lemma_path = tuple(["_".join([item.split('|')[0] for item in v])])

        pos_path = tuple(["_".join([item.split('|')[1] for item in v])])

        dep_path = tuple(["_".join([item.split('|')[2] for item in v])])

        dep_pos_path = [item.split('|')[1:] for item in v]

        path_dep_pos_reverse = [sublist[::-1] for sublist in dep_pos_path]

        dep_pos_path_flat = tuple(["_".join([item for sublist in path_dep_pos_reverse for item in sublist])])

#        full_path = tuple(["_".join(v)])
        full_path_partial = [item.split('|') for item in v]
        full_path = tuple(["_".join([item for sublist in full_path_partial for item in sublist])])

        new_val = full_path + pos_path + lemma_path + dep_path + dep_pos_path_flat
        path2root_solved[k] = new_val

################
## merge data VN
################

    vn_verb = predicate_verb_vn(predicateMatrix)
    for k, v in token_dependency.items():
        if v[3].startswith('V'):
            if v[2] in vn_verb:
                vn_values = "_".join(vn_verb[v[2]])
                new_val = v + (vn_values,)
                token_dependency[k] = new_val
            else:
                new_val = v + ("O",)
                token_dependency[k] = new_val
        else:
            new_val = v + ("O",)
            token_dependency[k] = new_val



################
## merge data FN
################

    fn_verb = predicate_verb_fn(predicateMatrix)
    for k, v in token_dependency.items():
        if v[3].startswith('V'):
            if v[2] in fn_verb:
                fn_values = "_".join(fn_verb[v[2]])
                new_val = v + (fn_values,)
                token_dependency[k] = new_val
            else:
                new_val = v + ("O",)
                token_dependency[k] = new_val

        else:
            new_val = v + ("O",)
            token_dependency[k] = new_val

################
## merge supersenses
################

    wn_data = {}
    noun_supersense = wn_supersense(wn_supersenses)

    for k, v in token_dependency.items():

        if v[3].startswith('N'):
            if v[2] in noun_supersense:
                wn_values = "_".join(noun_supersense[v[2]])
                new_val = v + (wn_values,)
                wn_data[k] = new_val

    verb_supersense = predicate_verb_wn(predicateMatrix)
    for k, v in token_dependency.items():
        if v[3].startswith('V'):
            if v[2] in verb_supersense:
                wn_values = "_".join(verb_supersense[v[2]])
                new_val = v + (wn_values,)
                wn_data[k] = new_val


####################
## add supersense - stanford data
#####################

    for k, v in token_dependency.items():

        if k in wn_data:

            new_val = wn_data[k]
            token_dependency[k] = new_val
        else:
            new_val = v + ("O",)
            token_dependency[k] = new_val


####################
## add path2root - stanford data
####################

    for k, v in token_dependency.items():
        new_key = k.replace("\t", "#")
        if new_key in path2root_solved:
            new_val = v + path2root_solved[new_key]
            token_dependency[k] = new_val
        else:
            new_val = v + ("O", "O", "O", "O", "O",)
            token_dependency[k] = new_val

####################
## solve governor lemma and POS - stanford data
####################

    token_dependency_copy = token_dependency.copy()

    for k, v in token_dependency.items():
        k_splitted = k.split("\t")
        gov_key = k_splitted[0] + "\t" + v[7]
        if gov_key in token_dependency_copy:
            new_val = v[:7] + (token_dependency_copy[gov_key][2], token_dependency_copy[gov_key][3],) + v[8:]
            token_dependency[k] = new_val
        else:
            new_val = v[:7] + ("O", "O",) + v[8:]
            token_dependency[k] = new_val


#################
# semantic roles and predicates
#################


    sem_roles_naf = process_feature_naf(naf_f)
    sem_roles_token = {}

    for k, v in token_dependency.items():
        for k1, v1 in sem_roles_naf.items():
            k1_splitted = k1.split("\t")
            if v[0] in v1:
                sem_role = k1_splitted[1]

                if v[0] in sem_roles_token:
                    list_value_type = sem_roles_token[v[0]]
                    if sem_role not in list_value_type:
                        list_value_type.append(sem_role)
                else:
                    list_value_type = []
                    list_value_type.append(sem_role)
                sem_roles_token[v[0]] = sorted(list_value_type)


    for k, v in token_dependency.items():
        if v[0] in sem_roles_token:
            new_val = v + tuple(["_".join(sem_roles_token[v[0]])])
            token_dependency[k] =  new_val
        else:
            new_val = v + ("O",)
            token_dependency[k] =  new_val


####################
# context windows
####################

    training = process_train(train_f)

    seven_context_window = {}

    for k, v in token_list_sentence.items():
        for i in previous_and_next(v, 7):
            seven_context_window[k + "\t" + i[7].split("|")[0]] = i


    for k, v in seven_context_window.items():
        k_splitted = k.split("\t")
        if int(k_splitted[1]) in training:
            new_val = tuple(v) + training[int(k_splitted[1])]
            seven_context_window[k] = new_val


#################
# event class only
#################

    event_arguments = collections.defaultdict(list)
    for k, v in token_dependency.items():

        for k1, v1 in sem_roles_naf.items():
            k1_splitted = k1.split("\t")
            pred_id = k1_splitted[0]
            role_type = k1_splitted[1]

            for i in v1:
                if i == v[0]:
                    new_val = int(i) -1
                    if new_val in training:
                        if training[new_val][0] != "O":
                            event_argument_label_pos_lemma =  v[2] + "|" + role_type + "|" + v[3]
                            event_arguments[pred_id].append(event_argument_label_pos_lemma)


    for k, v in token_dependency.items():

            if v[0] in event_arguments:
                values = event_arguments[v[0]]

                arg_label = tuple(["_".join([item.split('|')[1] for item in values])])

                label_lemma = [item.split('|')[0:2] for item in values]
                label_lemma_flat = tuple(["_".join([item for sublist in label_lemma for item in sublist])])

                label_lemma_pos = [item.split('|') for item in values]
                label_lemma_pos_flat = tuple(["_".join([item for sublist in label_lemma_pos for item in sublist])])

                new_val = v + label_lemma_pos_flat + label_lemma_flat + arg_label
                token_dependency[k] = new_val

            else:
                new_val = v + ("O", "O","O",)
                token_dependency[k] = new_val


###################
# train data
###################


    final_class = {}
    for k, v in token_dependency.items():
        k_splitted =  k.split("\t")
        new_unique_token_id = int(v[0]) -1

        new_sent_id = int(k_splitted[0]) -2
        f = stanfordf.split("/")[-1]

        final_val_class = (f,) + (str(new_sent_id),) + (k_splitted[1],) + v[1:]

        final_class[new_unique_token_id] = final_val_class

    final = {}

    for k, v in final_class.items():
        if k in training:
            if training[k][-1] != "O":

                new_val = v + ("B-EVENT",) + (training[k][-1],)
                final[k] = new_val

    for k, v in final.items():
        if int(k) == 0 and int(v[2]) == 1:
            output = open(outfile, 'a')
            output.writelines(v[0] + "\t" + str(k) + "\t" + '\t'.join(v[1:6]) + "\t" + "\t".join(v[8:11]) + "\t" + "\t".join(v[14:19]) + "\t" + v[6] + "\t" + v[7] + "\t" + "\t".join(v[11:14]) + "\t" + "\t".join(v[19:]) +  "\n")
            output.close()

        elif int(k) != 0 and int(v[2]) == 1:
            output = open(outfile, 'a')
            output.writelines("\n" + v[0] + "\t" + str(k) + "\t" + '\t'.join(v[1:6]) + "\t" + "\t".join(v[8:11]) + "\t" + "\t".join(v[14:19]) + "\t" + v[6] + "\t" + v[7] + "\t" + "\t".join(v[11:14]) + "\t" + "\t".join(v[19:]) +  "\n")
            output.close()

        else:
            output = open(outfile, 'a')
            output.writelines(v[0] + "\t" + str(k) + "\t" + '\t'.join(v[1:6]) + "\t" + "\t".join(v[8:11]) + "\t" + "\t".join(v[14:19]) + "\t" + v[6] + "\t" + v[7] + "\t" + "\t".join(v[11:14]) + "\t" + "\t".join(v[19:]) +  "\n")
            output.close()


    return final_class


def stanford_features(stanfordir, nafdir, traindir, predicateMatrix, wn_supersenses, outdir):

    for f in os.listdir(stanfordir):
        if f.endswith(".xml"):

            outfile = outdir + f + ".features.tense-train"

            train_f = traindir + f.split(".txt.xml")[0]
            process_train(train_f)

            naf_f = nafdir + f.split(".txt.xml")[0] + ".features.naf"
            process_feature_naf (naf_f)

            process_features_stanford(stanfordir + f, naf_f, train_f, predicateMatrix, wn_supersenses, outfile)


        else:
            print("File not processed: " + f)






def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 7:
        print('Usage: python3 event-tense_features_train_stanford+naf_te3.py [stanford_folder] [naf_folder] [train_dir] predicateMatrix wordnet30_noun_supersenses outdir')
    else:
        stanford_features(argv[1], argv[2], argv[3], argv[4], argv[5], argv[6])
        predicate_verb_vn(argv[4])
        predicate_verb_fn(argv[4])
        predicate_verb_wn(argv[4])
        wn_supersense(argv[5])

if __name__ == '__main__':
    main()