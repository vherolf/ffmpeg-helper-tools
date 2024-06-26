# ffmpeg-helper-tools
simple python scripts for ffmpeg batch tasks  

# FFMPEG Cheatsheet

## convert videos
```ffmpeg -i input.MTS output.mp4```  

## compress videos
crf is 0-52 (23-28 is a good choice)  
compress the videos with ffmpeg to h.265 (better)  
```ffmpeg -i videoin.mp4 -vcodec libx265 -crf 28 -c:a copy videoout.mp4 -y```  
compress the videos with ffmpeg to h.264 (for legacy systems)  
```ffmpeg -i input.MTS -crf 23 output.mp4```  

## concat videos
```ffmpeg -i "concat:00008.MTS|00009.MTS|00021.MTS|00010.MTS" -crf 23  output.mp4```

## cut out part of video
https://video.stackexchange.com/questions/4563/how-can-i-crop-a-video-with-ffmpeg

```ffmpeg -i input.mp4 -filter:v crop=iw/2:ih/2:0:0 -c:a copy output.mp4```


## trim a video
- The -ss parameter is the starting point.
- The -t provides the length of the clip  
```ffmpeg -i input.mp4 -ss 00:00:10 -t 00:20:00 -async 1 output.mp4```

## make animated gif from mp4

```ffmpeg -i input.pm4 rainbowunicorn.gif```

## dvgrab

extract from old video camcorder over firewire

```
dvgrab -size=0 -rewind -t mpeg2  -showstatus  -timesys -autosplit=10000
```
and to properly convert it to a mp4 use yadif filter  
```
ffmpeg -i dv-grabbed-video.dv  out.mp4
```