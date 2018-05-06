# TimeMLEventTrigger

This repo contains convertion scripts and models to automatically extract event triggers following the TimeML Annotation Guidelines.
The CRF models has been developed using the CRF++ Toolkit (https://taku910.github.io/crfpp/#format).

Scripts for feature extraction (training and test) take in input:
- the output of the NewsReader Pipeline (http://www.newsreader-project.eu/results/software/) ; or
- the output of the NewsReader Pipeline (http://www.newsreader-project.eu/results/software/) and the output of the Stanford CoreNLP pipeline (http://stanfordnlp.github.io/CoreNLP/)

As for test data, two feature extraction scripts are available. The scripts ending with "*_te3.py*" deal with TempEval-3 data only; the other with any other dataset or pre-processed text files.
 
Two CRF templates are made available: 
1. NWR-only: features are obtained only from the NewsReader Pipeline, Predicate Matrix (version 1.1), and WordNet supersenses (for nouns only)
2. Stanford+NWR: features are obtained by combning together the output of the Stanford CoreNLP tool (basic morph-synatactic and dependency features), the NewsReaer pipeline (the semantic role layer), Predicate Matrix (version 1.1), and and WordNet supersenses (for nouns only)


Evaluation has been conducted on the TempEval-3 Platinum test set. See table below for results and comparison with best 3 sota systems which took part to the TempEval-3 evaluation exercise (for more details https://www.cs.york.ac.uk/semeval-2013/task1/index.php%3Fid=results.html). 

| Sytem  | Precision | Recall | F1-score |
| ------------- | ------------- | ------------- | ------------- |
|  TE3-ATT1 | 0.814  | 0.806 | 0.81 |
|  TE3-ATT2 | 0.81 | 0.808 | 0.809 | 
| NavyTime-1 | 0.798 | 0.807 | 0.803 | 
| ------------- | ------------- | ------------- | ------------- |
| NWR-only| 0.809 | 0.787 | 0.798 | 
| Stanford+NWR | 0.817 | 0.82 | 0.817 | 

Both systems use Gold+Silver data in training .
Pre-trained models can be downloaded: http://kyoto.let.vu.nl/~caselli/pre-trained-models.tar.gz 

###### Event Attributes

The script for extracting training and test format for the event attributes are stored in the event_attributes folder.
The templates are available the event_attribute_template folder.

Evaluation against the TempEval-3 Platinum test:

| Sytem  | Class - F1 | Tense  - F1 | Aspect - F1 |
| ------------- | ------------- | ------------- | ------------- |
|  TE3-ATT1 | 0.718  | 0.594 | 0.735 |
|  ClearTK | 0.678 | 0.616 | 0.716 | 
| NavyTime-1 | 0.674 | 0.698 | 0.732 | 
| ------------- | ------------- | ------------- | ------------- |
| Stanford+NWR | 0.722 | 0.608 | 0.731 | 


Note: for the Class attribute, we used both gold and silver data to train the model. For Tense and Aspect training was done using the gold data only.


###### Temporal Relations

Three subsets of temporal relations are available:

- Event - Document Creation Time (DCT)
- Event - Temporal expression (same sentence)
- Event - Event (same sentence)

Script for extrating the training data are available in the tlinks folder.
The templates are available the tlinks_template folder.
The best system assumes dense temporal relations (i.e. all events in the same sentence connected among them) in test mode.


| Sytem  | P | R | F1 |
| ------------- | ------------- | ------------- | ------------- |
|  ClearTK | 0.34 | 0.284 | 0.309 | 
| ------------- | ------------- | ------------- | ------------- |
| Stanford+NWR | 0.238 | 0.392 | 0.296 | 


###### LREC 2018 paper

All materials in the LREC 2018 paper are available in the folder LREC18_materials.


References and Links:
- TempEval-3: https://www.cs.york.ac.uk/semeval-2013/task1/ 
- Predicate Matrix: http://adimen.si.ehu.es/web/PredicateMatrix
- Caselli, T., H. Llorens, B. Navarro-Colorado, E. Saquete. (2011). <a href="http://www.aclweb.org/anthology/R/R11/R11-1074.pdf">Data-Driven Approach Using Semantics for Recognizing and Classifying TimeML Events in Italian<a>. In: Proceedings of the International Conference Recent Advances in Natural Language Processing (RANLP 2011), Hissar, Bulgaria pp 533-538.
- Russo, I., T. Caselli and M. Monachini. 2015. <a href="http://ceur-ws.org/Vol-1399/paper17.pdf">Extracting and Visualising Biographical Events from Wikipedia<a>. In Proceedings of the first Conference on Biographical Data in a Digital World 2015 (BD 2015): 111 -115
- Caselli, T. and R. Morante. 2016. <a href="https://www.aclweb.org/anthology/S/S16/S16-1193.pdf">VUACLTL at SemEval 2016 Task 12: A CRF Pipeline to Clinical TempEval<a>. In Proceedings of the 10th International Workshop on Semantic Evaluation (SemEval 2016).
- Caselli, T. and R. Morante. 2018. <a href="http://www.lrec-conf.org/proceedings/lrec2018/pdf/880.pdf">Agreements and Disagreements in Temporal Processing: An Extensive Error Analysis of the TempEval-3 Systems<a>. In Proceedings of the 11th International Conference on Language Resources and Evaluation (LREC2018).


