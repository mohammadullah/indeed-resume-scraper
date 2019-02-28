#!/usr/bin/env bash
# Usage: ./script.sh <file with job titles>
# Assumes each line is a job title
# Defaults search to be in Canada
# Defaults search for 1000 resumes
# Defaults override (False)

FILE=$1

while read -u 3 job || [ -n "$job" ]; do
    echo "Searching resumes for ${job}"
    python indeed-scraper.py -q "$job" --name "$job" -ei 1000
    
    ## This interactive section is nice but user have to wait after each search to give permission for next search otherwise program shutdown :(

    #read -u 1 -t 5 -p "Stop searching? (y/n) " isStop
    #if [[ "$isStop" == "y" || -z "$isStop" ]]; then
    #    break
    #fi
done 3< "$FILE"