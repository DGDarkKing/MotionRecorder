# Application purpose

"Motion Recorder" is an application for creating sliced video
consisting of movement in the area of interest

## Reason of development

There were videos from a static camera, from which frames must be taken to train the `NN`.
\
To take frames using `ffmpeg`, you should cut the video into a clip, where the entities of interest go in a row.
\
Since the entity moves and the background changes slowly over time, it was decided to develop a **"Motion Recorder"**

## Features of work

### On host machine

To run the `app` on the host machine you can install `requirements.txt`
but be aware of the limitations of the `opencv-python` module.
\
If you need something specific, then install `opencv-python` yourself with the necessary libraries.

### On Docker

Inside the docker container is installed `python3-opencv`
and a libraries for working with `H264`.
\
So when using the container, you don't need to install the `opencv-python` module,
otherwise the `app` may not work

##### _Reason of containerization:_
The application worked well on `Windows` with the `H264` codec, 
but `opencv` and `Windows media player` could not read working files, although they used the `H264` codec
(`ffmpeg` worked correctly with these files).
\
Through an online file analyzer, I found out that they have a mime-type application/octet.
\
Maybe it was necessary to fix something additionally, but the answer was not found. And when you install `opencv` in the
`docker` container directly, many restrictions are removed.

