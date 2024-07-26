# HMain Files

In this folder the HMain files can be found together with their .sh bash script that can run them on a server. Naturally, the .sh file with the same name as the .py file will run that respective file. Also, when importing this code, keep in mind a file containing all python packages used should be present on the server within a folder called *Thoth*. 

A short description of each of the files:
* *HMain_Anglescan.py*: This code tries to simulate events coming from different angles and looping over them.
* *HMain_NMin_FHR_EFF.py*: This code is written with the aim to investigate the efficiency and false alarm rates of an array of hydrophones.
* *HMain_NMin_FHR_FE copy.py*: Similar to the previous two, but saving and printing different parameters.
* *HMain_NMin_FHR_FE.py*: Also very similar to the codes before.
* *HMain_NMin_VEff.py*: The code used to create the data files from which the effective volume could be determined without PanDepth.
* *HMain_NMin_VEff.py*: The code used to create the data files from which the effective volume could be determined without PanDepth.
* *HMain_NMin_VEff_PanDepth.py*: The code used to create the data files from which the effective volume could be determined with PanDepth.
* *HMain_Plot_Event_and_Clique.py*: The code used to create the data file from which the event reconstruction in the appendix could be plotted.
* *HMain_Reco_1.py* & *HMain_Reco_2.py*: Are codes used to visualise the workings of the algorithm to me personally. They print a lot of statements and helped me understand what is going on. They share the same .sh file that needs a tiny bit of adaptation to switch the .py file it runs.
 
