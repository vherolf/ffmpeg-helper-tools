## convert videos
ffmpeg -i input.MTS -vrf 23 output.mp4

## concat videos
ffmpeg -i "concat:00008.MTS|00009.MTS|00021.MTS|00010.MTS" -crf 23  output.mp4
