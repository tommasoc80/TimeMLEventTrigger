import sys
import collections
import os, os.path

"""
refine error stats on tlinks
"""


def get_tlink_detc_error(sys1_out):

    """
     sys error data
    """

    different_tense_same_aspect = collections.defaultdict(list)
    different_tense_different_aspect = collections.defaultdict(list)
    same_tense_different_aspect  = collections.defaultdict(list)

    fileObject = open(sys1_out)
    
    for line in fileObject:
        line_splitted = line.strip().split("\t")
        
        tense_val_e1 = line_splitted[3]
        tense_val_e2 = line_splitted[5]
        
        tokenId_e1 = line_splitted[1]
        tokenId_e2 = line_splitted[2]
    
        aspect_val_e1 = line_splitted[4]
        aspect_val_e2 = line_splitted[6]
        
        system_solved = line_splitted[7]
    
        if tense_val_e1 != tense_val_e2:
            if aspect_val_e1 != aspect_val_e2:
                different_tense_different_aspect[tense_val_e1 + "\t" + tense_val_e2].append(system_solved)

            else:
                different_tense_same_aspect[tense_val_e1 + "\t" + tense_val_e2].append(system_solved)
        
        if tense_val_e1 == tense_val_e2:
            if aspect_val_e1 != aspect_val_e2:
                same_tense_different_aspect[tense_val_e1 + "\t" + tense_val_e2].append(system_solved)
            
    
    fileObject.close()
    
    print("Different Tense & Different Aspect - DETC" + "\n")
    for k, v in different_tense_different_aspect.items():        
        print(k + "\t" +  str(v.count("0")) + "\t" + str(v.count("6")) + "\t" + str(v.count("1")) + "\t" + str(v.count("2")) + "\t" + str(v.count("3")) + "\t" + str(v.count("4")) + "\t" + str(v.count("5")))

    print("\n" + "Different Tense & Same Aspect - DETC" + "\n")
    for k, v in different_tense_same_aspect.items():        
        print(k + "\t" +  str(v.count("0")) + "\t" + str(v.count("6")) + "\t" + str(v.count("1")) + "\t" + str(v.count("2")) + "\t" + str(v.count("3")) + "\t" + str(v.count("4")) + "\t" + str(v.count("5")))

    print("\n" + "Same Tense & Different Aspect - DETC" + "\n")
    for k, v in same_tense_different_aspect.items():        
        print(k + "\t" +  str(v.count("0")) + "\t" + str(v.count("6")) + "\t" + str(v.count("1")) + "\t" + str(v.count("2")) + "\t" + str(v.count("3")) + "\t" + str(v.count("4")) + "\t" + str(v.count("5")))



def get_tlink_class_error(sys_out):

    different_tense_same_aspect = collections.defaultdict(list)
    different_tense_different_aspect = collections.defaultdict(list)
    same_tense_different_aspect  = collections.defaultdict(list)

    fileObject = open(sys_out)
    
    for line in fileObject:
        line_splitted = line.strip().split("\t")
        
        tense_val_e1 = line_splitted[4]
        tense_val_e2 = line_splitted[6]
        
        tokenId_e1 = line_splitted[1]
        tokenId_e2 = line_splitted[2]
    
        aspect_val_e1 = line_splitted[5]
        aspect_val_e2 = line_splitted[7]
        
        system_solved = line_splitted[8]
        tlink_class = line_splitted[3]
    
        if tense_val_e1 != tense_val_e2:
            if aspect_val_e1 != aspect_val_e2:
                different_tense_different_aspect[tense_val_e1 + "\t" + tense_val_e2 + "\t" + tlink_class].append(system_solved)

            else:
                different_tense_same_aspect[tense_val_e1 + "\t" + tense_val_e2 + "\t" + tlink_class].append(system_solved)
        
        if tense_val_e1 == tense_val_e2:
            if aspect_val_e1 != aspect_val_e2:
                same_tense_different_aspect[tense_val_e1 + "\t" + tense_val_e2 + "\t" + tlink_class].append(system_solved)
            
    
    fileObject.close()    

    print("Different Tense & Different Aspect - CLASS" + "\n")
    for k, v in different_tense_different_aspect.items():        
        print(k + "\t" +  str(v.count("0")) + "\t" + str(v.count("6")) + "\t" + str(v.count("1")) + "\t" + str(v.count("2")) + "\t" + str(v.count("3")) + "\t" + str(v.count("4")) + "\t" + str(v.count("5")))

    print("\n" + "Different Tense & Same Aspect - CLASS" + "\n")
    for k, v in different_tense_same_aspect.items():        
        print(k + "\t" +  str(v.count("0")) + "\t" + str(v.count("6")) + "\t" + str(v.count("1")) + "\t" + str(v.count("2")) + "\t" + str(v.count("3")) + "\t" + str(v.count("4")) + "\t" + str(v.count("5")))

    print("\n" + "Same Tense & Different Aspect - CLASS" + "\n")
    for k, v in same_tense_different_aspect.items():        
        print(k + "\t" +  str(v.count("0")) + "\t" + str(v.count("6")) + "\t" + str(v.count("1")) + "\t" + str(v.count("2")) + "\t" + str(v.count("3")) + "\t" + str(v.count("4")) + "\t" + str(v.count("5")))




def tlink_error_stats(sys1dir):
        
    for f in os.listdir(sys1dir):
        if f.endswith("diff_tense_aspect"):
            get_tlink_detc_error(sys1dir + f)

        if f.endswith("diff_tense_aspect_value"):
            get_tlink_class_error(sys1dir + f)



def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print('Usage: python error_tlink_stats.py [file_tlink_error]')
    else:
        tlink_error_stats(argv[1])

if __name__ == '__main__':
    main()