#!/bin/bash

colors=("w" "u" "b" "r" "g" "gold" "land" "colorless")
cmcs=(1 2 3 4 5 6)
types=(creature enchantment artifact instant sorcery)

# If the first argument is "init", then create the files
if [ "$1" == "init" ]; then
  # Iterate over the arrays and create the files
  for str in "${colors[@]}"
  do
      for cmc in "${cmcs[@]}"
      do
          for type in "${types[@]}"
          do
            mkdir -p $str/$cmc/
            touch $str/$cmc/$str-$cmc-$type.txt
          done
      done
  done
fi
if [ "$1" == "collate" ]; then
  rm cube.txt
  # Iterate over the arrays and create the files
  for str in "${colors[@]}" # FIXME: deal with gold and colorless separately
  do
      for cmc in "${cmcs[@]}"
      do
          for type in "${types[@]}"
          do
            cat cards/$str/$cmc/$str-$cmc-$type.txt >> cube.txt
          done
      done
  done
fi
