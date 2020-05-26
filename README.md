# Anorexia Topical Trends in Self-declared Reddit Users
CIRCLE 2020 paper "Anorexia Topical Trends in Self-declared Reddit Users"

The current directory contains:

1. labeled_dat.zip: A folder contains
    - pos: a folder contains CSV files each corresponds to a positive user
    - neg: a folder contains CSV files each corresponds to a negative user
    The CSV files contains only the labels of the post (multiple and main_label), where the labels are for the posts 
    starting from the beginning and ordered by time. Any other information is not mentioned as you should contact the 
    original dataset owners.
    - data_split.txt: contains the users_ids used in each split train, dev, test -sets.

2. Notebooks: a folder contains 3 folders. Each folder is related to one model mentioned in the paper. contains Jupyter notebooks that has the code for the 3 
    models mentioned in the paper. 
   