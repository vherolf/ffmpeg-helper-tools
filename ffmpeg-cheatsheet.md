## convert videos
```ffmpeg -i input.MTS output.mp4```

## compress videos
crf is 0-52 (23 is a good choise)
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
