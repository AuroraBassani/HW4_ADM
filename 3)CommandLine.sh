#!/bin/sh
#CommandLine question 3.


awk -F"," 'NR > 1 {arr[$2]++; spend[$2] += $9}END{for (a in arr) print a "\t" sprintf("%.2f", spend[a]/ arr[a]);}' "/Users/mattia/Desktop/ADM(Aris)/HM4/bank_transactions.csv"  | sort -k 2,2nr >  cml3.txt

head -1 cml3.txt > cml3one.txt


awk -F"\t" 'BEGIN{print "CustomerID", "Average transaction amount"}
{print$1,$2}' cml3one.txt







