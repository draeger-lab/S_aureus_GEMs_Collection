#!/bin/bash

# Fixing Bosi
for file in /Users/renz/Nextcloud/Documents/Promotion/Research_topics/Staphylococcus_review/Models/Bosi_corrected/*; do
  echo "$(echo "<?xml version='1.0' encoding='UTF-8'?>" | cat - "$file")" > "$file";
done
cd /Users/renz/Nextcloud/Documents/Promotion/Research_topics/Staphylococcus_review/Analysis/
for file in /Users/renz/Nextcloud/Documents/Promotion/Research_topics/Staphylococcus_review/Models/Bosi_corrected/*; do
  python Fixing_Bosi.py "$file";
done
cd /Users/renz/Nextcloud/Documents/Promotion/Research_topics/Staphylococcus_review/Memote_Report/Bosi
for file in /Users/renz/Nextcloud/Documents/Promotion/Research_topics/Staphylococcus_review/Models/Bosi_corrected/*; do
  memote report snapshot --filename "$(basename -s .xml ${file}).html" "$file";
done;


# Updating Bosi
for file in /Users/renz/Nextcloud/Documents/Promotion/Research_topics/Staphylococcus_review/Models/Bosi_updated/*; do
  python Update_bosi.py "$file";
done

cd /Users/renz/Nextcloud/Documents/Promotion/Sonstiges

for file in /Users/renz/Nextcloud/Documents/Promotion/Research_topics/Staphylococcus_review/Models/Bosi_updated/*; do
  java -jar ModelPolisher-1.7.jar --input "$file" --output "$file" --annotate-with-bigg=True;
done

cd /Users/renz/Nextcloud/Documents/Promotion/Research_topics/Staphylococcus_review/Memote_Report/Bosi_updated

for file in /Users/renz/Nextcloud/Documents/Promotion/Research_topics/Staphylococcus_review/Models/Bosi_updated/*; do
  memote report snapshot --filename "$(basename -s .xml ${file}).html" "$file";
done;

exit 0
