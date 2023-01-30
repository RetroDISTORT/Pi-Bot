# python3 webcam.py

import argparse
import asyncio
import json
import logging
import os
import platform
import ssl
import av

from aiohttp import web

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender

ROOT = os.path.dirname(__file__)


relay = None
webcam = None


def create_local_tracks(play_from, decode):
    global relay, webcam

    if play_from:
        player = MediaPlayer(play_from)
        return player.audio, player.video
    else:
        audio_options = {"channels": "2", "sample_rate": "10000", "-sample_fmt" : "s32"}#"-acodec": "pcm_s32le"}
        #video_options = {"framerate": "30", "video_size": "640x480"}
        #video_options = {"framerate": "2", "video_size": "640x480"}
        #video_options = {"framerate": "5", "video_size": "320x240"} #Fast
        #video_options = {"framerate": "30", "video_size": "320x240"} #Slow
        video_options = {"framerate": "20", "video_size": "160x120"}
        #video_options = {"framerate": "60", "video_size": "80x60"}
        if relay is None:
            if platform.system() == "Darwin":
                webcam_video = MediaPlayer(
                    "default:none", format="avfoundation", options=video_options
                )
            elif platform.system() == "Windows":
                webcam_video = MediaPlayer(
                    "video=Integrated Camera", format="dshow", options=video_options
                )
            else:
                # cannot setup the audio format pcm_s32le 
                webcam_video = MediaPlayer("/dev/video0", format="v4l2", options=video_options).video
                print("vvvvvvvvvvv")
                print(RTCRtpSender.getCapabilities("audio").codecs)
                #webcam_audio = MediaPlayer("dmic_sv", format="alsa", options=audio_options).audio 
                #webcam_audio = MediaPlayer("default", format="alsa").audio
                #webcam_audio = MediaPlayer("sysdefault:CARD=sndrpii2scard", format="alsa", options=audio_options).audio
                #webcam_audio = MediaPlayer("sysdefault:CARD=sndrpii2scard", format="alsa", options={'sample_rate':'12000'})
                #webcam = MediaPlayer("/dev/video0", format="h264", options=options)
            relay = MediaRelay()
        #return relay.subscribe(webcam_audio), relay.subscribe(webcam_video)
        return None, relay.subscribe(webcam_video)


def force_codec(pc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(
        [codec for codec in codecs if codec.mimeType == forced_codec]
    )


async def index(request):
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # open media source
    audio, video = create_local_tracks(
        args.play_from, decode=not args.play_without_decoding
        )

    if audio:
        audio_sender = pc.addTrack(audio)
        if args.audio_codec:
            force_codec(pc, audio_sender, args.audio_codec)
        elif args.play_without_decoding:
            raise Exception("You must specify the audio codec using --audio-codec")

    if video:
        video_sender = pc.addTrack(video)
        if args.video_codec:
            force_codec(pc, video_sender, args.video_codec)
        elif args.play_without_decoding:
            raise Exception("You must specify the video codec using --video-codec")

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


pcs = set()


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC webcam demo")
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument("--play-from", help="Read the media from a file and sent it."),
    parser.add_argument(
        "--play-without-decoding",
        help=(
            "Read the media without decoding it (experimental). "
            "For now it only works with an MPEGTS container with only H.264 video."
        ),
        action="store_true",
    )
    parser.add_argument(
        "--host", default="10.0.0.17", help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--verbose", "-v", action="count")
    parser.add_argument(
        "--audio-codec", help="Force a specific audio codec (e.g. audio/opus)"
    )
    parser.add_argument(
        "--video-codec", help="Force a specific video codec (e.g. video/H264)"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    #app.router.add_get("/static/scripts/controller.js", javascript)
    app.router.add_post("/offer", offer)
    app.router.add_static("/static/", path=str("./static/"))
    
    #web.static("css/style.css", "/static/css/style.css", show_index=True)
    #web.static("icon/favicon.ico", "/static/icon/favicon.ico", show_index=True)
    web.run_app(app, host=args.host, port=args.port, ssl_context=ssl_context)
