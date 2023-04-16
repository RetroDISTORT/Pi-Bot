# checkout https://github.com/sonkm3/aiortc-example/tree/main/examples/raspberrypicamera

import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid
import configparser     # Required for ini files
import sys              # Required for loading special modules
#import platform
#import av

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

sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/client/')
from clientSocket import ClientSocket


# Configuration
ROOT       = "/home/pi/Documents/boobot/apps/WebApp/"
#ROOT      = "/opt/boobot/apps/WebApp/"

logger     = logging.getLogger("pc")
pcs        = set()
relay      = MediaRelay()
#socket     = []


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
    pibotMicrophone, pibotCamera = create_local_tracks()
    pibotSpeaker = SystemSpeaker()
    #pibotSpeaker = MediaBlackhole()
    
    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            socket.send(message)
            serverResponse = socket.recieve()
            channel.send(str(serverResponse))
            
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


def loadConfig(configuration, fileName):
    configuration.read(os.path.expanduser(fileName))
    return

def connectionInfo(configurationFile):
    config  = configparser.ConfigParser()
    loadConfig(config, configFile)

    section = 'WebsiteLocal' if config['Settings'].getboolean('local settings') else 'WebsiteRemote'
    ip      = getIP(config[section]['ip'])
    portW   = config[section]['Port']
    portWS  = config[section]['websocketport']
    portS   = config['Socket']['Port']
    cert    = config['WebsiteCertificate']['certificate']
    key     = config['WebsiteCertificate']['key']

    return section, ip, portW, portWS, portS, cert, key


if __name__ == "__main__":
    global socket
    parser = argparse.ArgumentParser(description="Pibot WebApp")
    parser.add_argument("--config-file", default="/opt/boobot/apps/WebApp/configuration/app.config", help="File with configuration")
    parser.add_argument("--record-to", help="Write received media to a file."),
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    configFile  = args.config_file 
    section, ip, portW, portWS, portS, cert, key = connectionInfo(configFile)
    print("ip: " + getIP(ip) + " portW: " + portW + " portS: " + portS + " section: " + section)
    socket      = ClientSocket(getIP(ip), int(portS))
    

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if cert!="" and key!="":
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(cert, key)
    else:
        ssl_context = None

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get(    "/index.html",    index)
    app.router.add_get(    "/",              index)
    app.router.add_get(    "/webRTC.js",     webRTCJavascript)
    app.router.add_get(    "/controller.js", controllerJavascript)
    app.router.add_post(   "/offer",         offer)
    app.router.add_static( "/static/",       path=str("/opt/boobot/apps/WebApp/Website/static/"))
    
    web.run_app(app, host=ip, port=portW, ssl_context=ssl_context)
