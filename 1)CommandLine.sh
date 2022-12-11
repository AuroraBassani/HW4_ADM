#!/bin/sh
#CommandLine question 1.

#With this line of code we obtain the frequency regarding the location of the purchases.
#The output dataset is sorted in desceding order.
awk -F ',' '{print $5}' "/Users/mattia/Desktop/ADM(Aris)/HM4/bank_transactions.csv" | sort | uniq -c  | sort -nr   > cml1.txt 

#Now we take only the top 5.
head -5 cml1.txt 

