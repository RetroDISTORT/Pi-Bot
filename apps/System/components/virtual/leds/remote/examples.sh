#!/bin/bash

E=(
"off.py $1 $2"
    
"rainbowCycle.py $1 $2 -3"

"colorGlowCycle.py $1 $2 255 0  .1     3"
"colorGlowCycle.py $1 $2  0  0   0     3"
"colorGlowCycle.py $1 $2  0  0   2   100"
"colorGlowCycle.py $1 $2  0  4   2   100"

"pixelCycle.py $1 $2 255   0   8   0   5"
"pixelCycle.py $1 $2   0   1   0   1 100"
"pixelCycle.py $1 $2   0   4   0  .2   5"
"pixelCycle.py $1 $2   0   0   0  .2   5"
"pixelCycle.py $1 $2   0   1   0 -.2   5"

"VU.py       $1 $2 0 -2 17.4 .65    4000"

"VUStereo.py $1 $2 0 -2 17.4 .65    4000"

"spectrum.py $1 $2 0  4    0  50 .8 4000"

"3PointVU.py $1 $2 0  4    0  50 .8 4000"
)

echo "LED Color animation code examples"
echo ""
echo "Make sure that the server is running using sudo!"
echo "Command list:"
for i in {0..14}
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
  
