# checkout https://github.com/sonkm3/aiortc-example/tree/main/examples/raspberrypicamera

import argparse
import asyncio
import json
import logging
import os
import platform
import ssl
import av
import uuid
import configparser     # Required for ini files
import sys              # Required for loading special modules

from aiohttp import web
from av import VideoFrame

from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
#from aiortc import RTCPeerConnection, RTCSessionDescription
#from aiortc.rtcrtpsender import RTCRtpSender

#sys.path.insert(1, '/opt/boobot/apps/System/components/devices/')
sys.path.insert(1, '/home/pi/Documents/boobot/apps/System/components/devices/')
from systemSpeaker     import SystemSpeaker
from systemMic         import SystemMic


ROOT = "/home/pi/Documents/boobot/apps/WebApp/"
#ROOT = "/opt/boobot/apps/WebApp/"

logger = logging.getLogger("pc")
pcs = set()
relay = MediaRelay()


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
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote)

    # prepare local media
    player       = MediaPlayer(os.path.join(ROOT, "Website/demo-instruct.wav")).audio
    #player = SystemMic()
    if args.record_to:
        recorder = MediaRecorder(args.record_to)
    else:
        recorder = MediaBlackhole()
        #recorder = SystemSpeaker()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])
                
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        if track.kind == "audio":
            pc.addTrack(player.audio)
            recorder.addTrack(track)
        elif track.kind == "video":
            pc.addTrack(
                VideoTransformTrack(
                    relay.subscribe(track), transform=params["video_transform"]
                )
            )
            if args.record_to:
                recorder.addTrack(relay.subscribe(track))

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)
            await recorder.stop()


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
    parser.add_argument(
        "--host", default=getIP(ip), help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=port, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--record-to", help="Write received media to a file."),
    parser.add_argument("--verbose", "-v", action="count")


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
