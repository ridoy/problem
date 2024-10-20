#!/bin/bash

# Define the base input files
INTRO="problem_beat_intro_8_bars.wav"
BEAT_A="problem_beat_a_16_bars.wav"
BEAT_B="problem_beat_b_16_bars.wav"
OUTRO="problem_beat_outro_8_bars.wav"

# Loop through the 10 beats
for i in {1..10}
do
  # Create the filter_complex dynamically
  FILTER_COMPLEX="[0]atrim=0:12.064[intro]; [1]atrim=0:76.428,asetpts=PTS-STARTPTS[beat_a];"
  
  # Add repetitions of beat_b based on the iteration number (i-2) for beats 2-10
  if (( i > 1 )); then
    for j in $(seq 1 $((i-1)))
    do
      FILTER_COMPLEX+=" [2]atrim=0:76.428,asetpts=PTS-STARTPTS[beat_b${j}];"
    done
  fi

  # Add the outro
  FILTER_COMPLEX+=" [3]atrim=0:12.064[outro];"

  # Construct the concat filter
  CONCAT="concat=n=$((i+2)):v=0:a=1[out]"
  FILTER_COMPLEX+=" [intro][beat_a]"

  # Add beat_b labels for concatenation
  if (( i > 1 )); then
    for j in $(seq 1 $((i-1)))
    do
      FILTER_COMPLEX+="[beat_b${j}]"
    done
  fi

  # Add the outro label
  FILTER_COMPLEX+="[outro]$CONCAT"

  # Construct the output file name
  OUTPUT="full_beat_${i}.mp3"

  # Generate the FFmpeg command
  ffmpeg -i "$INTRO" -i "$BEAT_A" -i "$BEAT_B" -i "$OUTRO" \
    -filter_complex "$FILTER_COMPLEX" \
    -map "[out]" -c:a libmp3lame -b:a 320k "$OUTPUT"

  echo "Generated: $OUTPUT"
done

