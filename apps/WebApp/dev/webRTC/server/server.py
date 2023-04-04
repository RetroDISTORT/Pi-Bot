import argparse
import asyncio
import json
import logging
import os
import sys
import ssl
import uuid

#import cv2
from aiohttp import web
from av import VideoFrame

from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay

#sys.path.insert(1, '/opt/boobot/apps/System/components/devices/')
sys.path.insert(1, '/home/pi/Documents/boobot/apps/System/components/devices/')
from systemSpeaker     import SystemSpeaker
from systemMicPA       import SystemMic


ROOT = os.path.dirname(__file__)

logger = logging.getLogger("pc")
pcs = set()
relay = MediaRelay()


def getIP(IP):
    return IP if IP != "" else os.popen("hostname -I").read().split()[0]

def create_local_tracks():
    #video_options = {"framerate": "30", "video_size": "640x480"}
    #video_options = {"framerate": "2", "video_size": "640x480"}
    #video_options = {"framerate": "5", "video_size": "320x240"} #Fast
    #video_options = {"framerate": "30", "video_size": "320x240"} #Slow
    video_options = {"framerate": "20", "video_size": "160x120"}
    webcam = MediaPlayer("/dev/video0", format="v4l2", options=video_options)
    sysMic = SystemMic()
    relay = MediaRelay()
    
    return sysMic, relay.subscribe(webcam.video)


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
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote)


    # prepare local media
    pibotMicrophone, pibotCamera = create_local_tracks()
    pibotSpeaker = SystemSpeaker()
    #pibotSpeaker = MediaBlackhole()
    
    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        if track.kind == "audio":
            pibotSpeaker.addTrack(track)
            pc.addTrack(pibotMicrophone)
        elif track.kind == "video":
            pc.addTrack(pibotCamera)

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)
            await pibotSpeaker.stop()

    # handle offer
    await pc.setRemoteDescription(offer)
    await pibotSpeaker.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WebRTC audio / video / data-channels demo"
    )
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default=getIP(""), help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
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
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)
    web.run_app(
        app, host=args.host, port=args.port, ssl_context=ssl_context
    )
