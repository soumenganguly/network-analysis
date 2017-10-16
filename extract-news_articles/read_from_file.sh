#!/bin/bash

input="/home/sougangu/news_crawls/french_online_news_publishers/google_unique_sources.txt"

output="/home/sougangu/news_crawls/french_online_news_publisers/french_outlets_temp.txt"

old_IFS=$IFS
IFS=$'\n'
outlets=`cat "$input"`
IFS=$old_IFS

x=$((${#outlets[@]} / 10))

while true;
do
	for (( i = 0 ; i < $x ; i++ ))
	do
		count=$((i * 10))
		for (( j = count ; j < $(count + 10) ; j++ ))
		do
		 	echo ${outlets[$j]} >> $output 
		done
		python news_crawler.py 
		sleep 120
		echo  > $output
	done
	sleep 1200
done
