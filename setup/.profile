if [ `users | wc -w` -lt 2 ] # If there are no more users logged in
then
    python3 /opt/boobot/apps/System/programs/startup.py &
fi
