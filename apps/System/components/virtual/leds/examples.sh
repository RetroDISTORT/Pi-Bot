#!/bin/bash

E=("rainbowCycle.py -3"

"colorGlowCycle.py 255 0  .1     3"
"colorGlowCycle.py 0   0   0     3"
"colorGlowCycle.py 0   0   2   100"
"colorGlowCycle.py 0   4   2   100"

"pixelCycle.py 255   0   8   0   5"
"pixelCycle.py   0   1   0   1 100"
"pixelCycle.py   0   4   0  .2   5"
"pixelCycle.py   0   0   0  .2   5"
"pixelCycle.py   0   1   0 -.2   5")

echo "LED Color animation code examples"
echo ""
echo "Make sure that the server is running using sudo!"
echo "Command list:"
for i in {0..9}
do
    echo example ${i}. ${E[${i}]}
done

echo "Input a command number:"
read input
if [[ $input ]] && [ $input -eq $input 2>/dev/null ]
then
    python3 ${E[${input}]}
else
    echo "Bad input."
fi
  
