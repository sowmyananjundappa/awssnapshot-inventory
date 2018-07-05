#!/bin/bash
while IFS= read -r line
do
  python  "file path of snapshot.py" $line
done < "file path of owner.txt"
