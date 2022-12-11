#!/bin/sh
#CommandLine question 2.



awk -F"," 'NR > 1 {arr[$4]++; spend[$4] += $9}END{for (a in arr) print a "\t" sprintf("%.2f", spend[a])}' "/Users/mattia/Desktop/ADM(Aris)/HM4/bank_transactions.csv" > cml2.txt

awk -F"\t" 'BEGIN{print "Sex", "Spend"}
{if ($1=="M"||$1=="F") print$1,$2}' cml2.txt




