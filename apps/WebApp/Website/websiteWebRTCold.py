# checkout https://github.com/sonkm3/aiortc-example/tree/main/examples/raspberrypicamera

import argparse
import asyncio
import json
import logging
import os
import platform
import ssl
import av
import configparser     # Required for ini files

from aiohttp import web

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender

import sys              # Required for loading special modules

sys.path.insert(1, '/opt/boobot/apps/System/components/devices/')
from systemMic     import SystemMic

ROOT = "/home/pi/Documents/boobot/apps/WebApp/"
#ROOT = "/opt/boobot/apps/WebApp/"

relay  = None
webcam = None


def getIP(IP):
    return IP if IP != "" else os.popen("hostname -I").read().split()[0]


def create_local_tracks(play_from, decode):
    global relay, webcam

    if play_from:
        player = MediaPlayer(play_from)
        return player.audio, player.video
    else:
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
                #webcam_video = MediaPlayer("/dev/video0", format="v4l2", options=video_options).video
                webcam = MediaPlayer("/dev/video0", format="v4l2", options=video_options)
                sysMic = SystemMic()
                
            relay = MediaRelay()
        return sysMic, relay.subscribe(webcam.video)

    
async def index(request):
    content = open(ROOT+"Website/templates/indexWebRTC.html", "r").read()
    return web.Response(content_type="text/html", text=content)


async def webRTCJavascript(request):
    content = open(ROOT+"Website/static/scripts/webRTC.js", "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def controllerJavascript(request):
    content = open(ROOT+"Website/static/scripts/controller.js", "r").read()
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

    WebResponse = web.Response( content_type="application/json", text=json.dumps( {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}),)

    return WebResponse


pcs = set()


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


def loadConfig(configuration, fileName):
    configuration.read(fileName)
    return

    
if __name__ == "__main__":
    fileName   = '/opt/boobot/apps/WebApp/server.config'
    config     = configparser.ConfigParser()
    loadConfig(config, fileName)
    ip         = ""
    port       = config['Website']['Port']
    
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
        "--host", default=getIP(ip), help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=port, help="Port for HTTP server (default: 8080)"
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
    app.router.add_get("/index.html", index)
    app.router.add_get("/webRTC.js", webRTCJavascript)
    app.router.add_get("/controller.js", controllerJavascript)
    app.router.add_post("/offer", offer)
    app.router.add_static("/static/", path=str("/opt/boobot/apps/WebApp/Website/static/"))
    web.run_app(app, host=args.host, port=args.port, ssl_context=ssl_context)
