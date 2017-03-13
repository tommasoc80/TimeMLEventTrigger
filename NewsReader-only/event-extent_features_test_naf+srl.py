import sys
import os, os.path
import collections
from lxml import etree

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


def process_features_naf(naff, predicateMatrix, wn_supersenses, outfile):

    doc = etree.parse(naff, etree.XMLParser(remove_blank_text=True))
    root = doc.getroot()
    root.getchildren()


    """
    sentence, token, lemma, pos, NER
    """

    token_per_sentence = collections.defaultdict(list)
    token_sentence_id = {}
    entity_dict = {}
    timex_dict = collections.defaultdict(list)
    dependency_dict = {}
    token_dependency = {}

    counter = 0
    for token in root.iter("wf"):
        token_id = token.attrib.get("id", "null")
        sentence_id = token.attrib.get("sent", "null")
        token_word = token.text

        token_per_sentence[sentence_id].append(token_id)
        token_dependency[token_id.replace('w', 't')] = (token_id, sentence_id, token_word)


    for k, v in token_per_sentence.items():
        for i in v:
            new_index = int(v.index(i)) + 1
            key = i.replace('w', 't')
            token_sentence_id[key] = str(new_index)


    for k, v in token_dependency.items():
        if k in token_sentence_id:
            new_val = v[:-1] + (token_sentence_id[k],) + (v[2],)
            token_dependency[k] = new_val


    for terms in root.iter("terms"):
        for term in terms.iter("term"):

            lemma_id = term.attrib.get("id", "null")
            lemma_token = term.attrib.get("lemma", "null")
            lemma_pos = term.attrib.get("morphofeat", "null")

            if lemma_id in token_dependency:
                new_val = token_dependency[lemma_id] + (lemma_token, lemma_pos,)
                token_dependency[lemma_id] = new_val


    for entities in root.iter("entities"):
        for entity in entities.iter("entity"):
            entity_type = entity.attrib.get("type", "null")
            for reference in entity.iter("references"):
                for token_span in reference.iter("span"):
                    for token_id in token_span.iter("target"):
                        token_match = token_id.attrib.get("id", "null")
                        entity_dict[token_match] = entity_type


    for k, v in token_dependency.items():
        if k in entity_dict:
            new_val = v + (entity_dict[k], "O",)
            token_dependency[k] = new_val
        else:
            new_val = v + ("O", "O",)
            token_dependency[k] = new_val



    for timexpression in root.iter("timeExpressions"):
        for timex in timexpression.iter("timex3"):
            timex_id = timex.attrib.get("id", "null")
            for timex_span in timex.iter("span"):
                for token_id in timex_span.iter("target"):
                    tokens = token_id.attrib.get("id", "null").replace('w', 't')
                    timex_dict[timex_id].append(tokens)


    for k, v in token_dependency.items():

        for k1, v1 in timex_dict.items():
            if len(v1) > 1 :
                if k == v1[0]:
                    new_val = v[:-1] + ("B-TIMEX",)
                    token_dependency[k] = new_val

                for i in range(1, len(v1)):
                    val = v1[i]
                    if val == k:
                        new_val = v[:-1] + ("I-TIMEX",)
                        token_dependency[k] = new_val

            else:
                if k in v1:
                    new_val = v[:-1] + ("B-TIMEX",)
                    token_dependency[k] = new_val


    for dependecies in root.iter("deps"):
        for dep in dependecies.iter("dep"):
            governor =  dep.attrib.get("from", "null")
            dependent =  dep.attrib.get("to", "null")
            dep_rel = dep.attrib.get("rfunc", "null")
            dependency_dict[dependent] = (dep_rel, governor)

    for k, v in token_dependency.items():
        if k in dependency_dict:
            new_val = v + dependency_dict[k]
            token_dependency[k] = new_val
        else:
            new_val = v + ("_", "_",)
            token_dependency[k] = new_val

#########################
# SRL naf
#########################

    predicate_term = {}
    predicate_roles = collections.defaultdict(list)

    for elem in root.iter("srl"):
        for srl in elem.findall("predicate"):
            predicate_id = srl.attrib.get("id", "null")
            for term in srl.findall("span"):
                for term_id in term.findall("target"):
                    predicte_term = term_id.attrib.get("id", "null")
                    predicate_term[predicate_id] = predicte_term

            for role in srl.findall("role"):
                role_id = role.attrib.get("id", "null")
                role_type = role.attrib.get("semRole", "null")
                for role_span in role.findall("span"):
                    for role_term in role_span.findall("target"):
                        role_span_id = role_term.attrib.get("id", "null")
                        predicate_roles[predicate_id + "\t" + role_type + "\t" + role_id].append(role_span_id)

    predicate_argument_final = {}
    for k, v in predicate_roles.items():
        k_splitted = k.split("\t")
        if k_splitted[0] in predicate_term:
            new_val = tuple(v)
            predicate_argument_final[predicate_term[k_splitted[0]] + "\t" + "\t".join(k_splitted[1:])] = new_val


######################
## -  path2root - dependencies
######################

    path = {}
    for k, v in token_dependency.items():
        sentence_id = v[1]
        path[sentence_id + "#" + k] = sentence_id + "#" + v[9]

    path2root = {}
    path2root_solved = {}

    for k, v in path.items():
        path2root[k] = get_path2root(path, k)

    for k, v in path2root.items():
        k_splitted = k.split("#")
        sentence_id_path = k_splitted[0]

        for k1, v1 in token_dependency.items():
            sentence_id = v1[1]
            term_id = k1

            match = sentence_id + "#" + term_id

            if str(sentence_id_path) == str(sentence_id):
                for n, i in enumerate(v):
                    if str(i) == str(match):
                        if v1[8] == "_":
                            match_full = v1[4] + "|" + v1[5] + "|root"
                            v[n] = match_full
                            path2root_solved[k_splitted[1]] = tuple(v)
                        else:
                            match_full = v1[4] + "|" + v1[5] + "|" + v1[8]
                            v[n] = match_full
                            path2root_solved[k_splitted[1]] = tuple(v)


    for k, v in path2root_solved.items():
        lemma_path = tuple(["_".join([item.split('|')[0] for item in v])])
        pos_path = tuple(["_".join([item.split('|')[1] for item in v])])
        dep_path = tuple(["_".join([item.split('|')[2] for item in v])])

        dep_pos_path = [item.split('|')[1:] for item in v]
        path_dep_pos_reverse = [sublist[::-1] for sublist in dep_pos_path]
        dep_pos_path_flat = tuple(["_".join([item for sublist in path_dep_pos_reverse for item in sublist])])

        full_path_partial = [item.split('|') for item in v]
        full_path = tuple(["_".join([item for sublist in full_path_partial for item in sublist])])

        new_val = full_path + pos_path + lemma_path + dep_path + dep_pos_path_flat
        path2root_solved[k] = new_val


# ################
# ## merge data VN
# ################

    vn_verb = predicate_verb_vn(predicateMatrix)
    for k, v in token_dependency.items():
        if v[5].startswith('V'):
            if v[4] in vn_verb:
                vn_values = "_".join(vn_verb[v[4]])
                new_val = v + (vn_values,)
                token_dependency[k] = new_val
            else:
                new_val = v + ("O",)
                token_dependency[k] = new_val
        else:
            new_val = v + ("O",)
            token_dependency[k] = new_val


# ################
## merge data FN
# ################

    fn_verb = predicate_verb_fn(predicateMatrix)
    for k, v in token_dependency.items():
        if v[5].startswith('V'):
            if v[4] in fn_verb:
                fn_values = "_".join(fn_verb[v[4]])
                new_val = v + (fn_values,)
                token_dependency[k] = new_val
            else:
                new_val = v + ("O",)
                token_dependency[k] = new_val
        else:
            new_val = v + ("O",)
            token_dependency[k] = new_val


# ################
# ## merge supersenses
# ################

    wn_data = {}
    noun_supersense = wn_supersense(wn_supersenses)
    for k, v in token_dependency.items():
        if v[5].startswith('N'):
            if v[4] in noun_supersense:
                wn_values = "_".join(noun_supersense[v[4]])
                new_val = v + (wn_values,)
                wn_data[k] = new_val

    verb_supersense = predicate_verb_wn(predicateMatrix)
    for k, v in token_dependency.items():
        if v[5].startswith('V'):
            if v[4] in verb_supersense:
                wn_values = "_".join(verb_supersense[v[4]])
                new_val = v + (wn_values,)
                wn_data[k] = new_val


# ####################
# ## add supersense - stanford data
# ####################

    for k, v in token_dependency.items():
        if k in wn_data:
            new_val = wn_data[k]
            token_dependency[k] = new_val
        else:
            new_val = v + ("O",)
            token_dependency[k] = new_val



# ####################
# ## add path2root - stanford data
# ####################

    for k, v in token_dependency.items():
        if k in path2root_solved:
            new_val = v + path2root_solved[k]
            token_dependency[k] = new_val
        else:
            new_val = v + ("O", "O", "O", "O", "O",)
            token_dependency[k] = new_val

# ####################
# ## solve governor lemma and POS - stanford data
# ####################

    token_dependency_copy = token_dependency.copy()

    for k, v in token_dependency.items():
        gov_key = v[9]
        if gov_key in token_dependency_copy:
            new_val = v[:9] + (token_dependency_copy[gov_key][4], token_dependency_copy[gov_key][5],) + v[10:]
            token_dependency[k] = new_val
        else:
            new_val = v[:9] + ("O", "O",) + v[10:]
            token_dependency[k] = new_val

#################
# semantic roles and predicates
#################


    sem_roles_token = {}

    for k, v in token_dependency.items():

        for k1, v1 in predicate_argument_final.items():
            k1_splitted = k1.split("\t")

            if k in v1:
                sem_role = k1_splitted[1]

                if k in sem_roles_token:
                    list_value_type = sem_roles_token[k]
                    if sem_role not in list_value_type:
                        list_value_type.append(sem_role)
                else:
                    list_value_type = []
                    list_value_type.append(sem_role)
                sem_roles_token[k] = sorted(list_value_type)

    for k, v in token_dependency.items():
        if k in sem_roles_token:
            new_val = v + tuple(["_".join(sem_roles_token[k])])
            token_dependency[k] = new_val
        else:
            new_val = v + ("O",)
            token_dependency[k] = new_val

######################
## final format
######################

    final_test = {}
    for k, v in token_dependency.items():
        k_ord = k.replace('t', '')
        f = naff.split("/")[-1]
        final_val = (f,) + v + ("O", "O", "O", "O", "O",)
        final_test[int(k_ord)] = final_val

    for k, v in final_test.items():

        if int(k) == 0 and int(v[3]) == 1:
            output = open(outfile, 'a')
            output.writelines(
                v[0] + "\t" + str(k) + "\t" + '\t'.join(v[2:7]) + "\t" + "\t".join(v[9:12]) + "\t" + "\t".join(
                    v[15:20]) + "\t" + v[7] + "\t" + v[8] + "\t" + "\t".join(v[12:15]) + "\t" + "\t".join(
                    v[20:]) + "\tO" + "\n")
            output.close()

        elif int(k) != 0 and int(v[3]) == 1:
            output = open(outfile, 'a')
            output.writelines(
                "\n" + v[0] + "\t" + str(k) + "\t" + '\t'.join(v[2:7]) + "\t" + "\t".join(v[9:12]) + "\t" + "\t".join(
                    v[15:20]) + "\t" + v[7] + "\t" + v[8] + "\t" + "\t".join(v[12:15]) + "\t" + "\t".join(
                    v[20:]) + "\tO" + "\n")
            output.close()

        else:
            output = open(outfile, 'a')
            output.writelines(
                v[0] + "\t" + str(k) + "\t" + '\t'.join(v[2:7]) + "\t" + "\t".join(v[9:12]) + "\t" + "\t".join(
                    v[15:20]) + "\t" + v[7] + "\t" + v[8] + "\t" + "\t".join(v[12:15]) + "\t" + "\t".join(
                    v[20:]) + "\tO" + "\n")
            output.close()


    return final_test



def naf_features(nafdir, predicateMatrix, wn_supersenses, outdir):

    for f in os.listdir(nafdir):
        """
        Adapt the extension file to the output of the NWR pipeline - for ECB+ data the data ends in .xml
        """
        if f.endswith(".xml"):
            outfile = outdir + f + ".features.extent-test"
            process_features_naf(nafdir + f, predicateMatrix, wn_supersenses, outfile)


        else:
            print("File not processed: " + f)




def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 5:
        print('Usage: python3 features_test.py naf_folder predicateMatrix wordnet30_noun_supersenses outdir')
    else:
        naf_features(argv[1], argv[2], argv[3], argv[4])
        predicate_verb_vn(argv[2])
        predicate_verb_fn(argv[2])
        predicate_verb_wn(argv[2])
        wn_supersense(argv[3])

if __name__ == '__main__':
    main()