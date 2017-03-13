# TimeMLEventTrigger

This repo contains convertion scripts and models to automatically extract event triggers following the TimeML Annotation Guidelines.
The CRF models has been developed using the CRF++ Toolkit (https://taku910.github.io/crfpp/#format).

Scripts for feature extraction (training and test) take in input:
- the output of the NewsReader Pipeline (http://www.newsreader-project.eu/results/software/) ; or
- the output of the NewsReader Pipeline (http://www.newsreader-project.eu/results/software/) and the output of the Stanford CoreNLP pipeline (http://stanfordnlp.github.io/CoreNLP/)

Two CRF templates are made available: 
1) NWR-only: features are obtained only from the NewsReader Pipeline, Predicate Matrix (version 1.1), and WordNet supersenses (for nouns only)
2) Stanford+NWR: features are obtained by combning together the output of the Stanford CoreNLP tool (basic morph-synatactic and dependency features), the NewsReaer pipeline (the semantic role layer), Predicate Matrix (version 1.1), and and WordNet supersenses (for nouns only)

Evaluation has been conducted on the TempEval-3 Platinum test set. See table below for results and comparison with best 3 sota systems which took part to the TempEval-3 evaluation exercise (for more details https://www.cs.york.ac.uk/semeval-2013/task1/index.php%3Fid=results.html). 

| Sytem  | Precision | Recall | F1-score |
| ------------- | ------------- | ------------- | ------------- |
|  TE3-ATT1 | 0.814  | 0.806 | 0.81 |
|  TE3-ATT2 | 0.81 | 0.808 | 0.809 | 
| NavyTime-1 | 0.798 | 0.807 | 0.803 | 
| ------------- | ------------- | ------------- | ------------- |
| NWR-only| 0.809 | 0.787 | 0.798 | 
| Stanford+NWR | 0.806 | 0.799 | 0.803 | 

Both systems use Gold+Silver data in training.
Pre-trained models can be downloaded: http://kyoto.let.vu.nl/~caselli/pre-trained-models.tar.gz 


References and Links:
- TempEval-3: https://www.cs.york.ac.uk/semeval-2013/task1/ 
- Predicate Matrix: http://adimen.si.ehu.es/web/PredicateMatrix
- Caselli, T., H. Llorens, B. Navarro-Colorado, E. Saquete. (2011). <a href="http://www.aclweb.org/anthology/R/R11/R11-1074.pdf">Data-Driven Approach Using Semantics for Recognizing and Classifying TimeML Events in Italian<a>. In: Proceedings of the International Conference Recent Advances in Natural Language Processing (RANLP 2011), Hissar, Bulgaria pp 533-538.
- Russo, I., T. Caselli and M. Monachini. 2015. <a href="http://ceur-ws.org/Vol-1399/paper17.pdf">Extracting and Visualising Biographical Events from Wikipedia<a>. In Proceedings of the first Conference on Biographical Data in a Digital World 2015 (BD 2015): 111 -115
- Caselli, T. and R. Morante. 2016. <a href="https://www.aclweb.org/anthology/S/S16/S16-1193.pdf">VUACLTL at SemEval 2016 Task 12: A CRF Pipeline to Clinical TempEval<a>. In Proceedings of the 10th International Workshop on Semantic Evaluation (SemEval 2016).


