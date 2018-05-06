This folder contains the stats for TE3 systems on event detection and classification

There 2 types of folder:

- systemName1-systemName2: compare 2 systems one wrt the other for event extent and event classification. The files in each folder are:

common_extent: events identified by both systems
different_extent: event identified by systemName1 and not by systemName2
common_same_class: events in common with same class
common_different_class: events in common with different class

- full_set_gold: for each system (7 systems overall) it compares the GOLD event (extent and class) and reports on the number of systems which have correctly identified each GOLD events