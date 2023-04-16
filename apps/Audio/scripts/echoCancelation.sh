if grep -q ".ifexists module-echo-cancel.so" "/etc/pulse/default.pa"; then
    echo "Error: Echo cancelation has already been enabled"
else
    echo ".ifexists module-echo-cancel.so
load-module module-echo-cancel aec_method=webrtc source_name=echocancel sink_name=echocancel1
set-default-source echocancel
set-default-sink echocancel1
.endif" >> /etc/pulse/default.pa
    
    echo "Echo cancelation enabled. Now run pulseaudio -k reload pulseaudio."
fi

