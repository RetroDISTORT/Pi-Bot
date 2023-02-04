class Colors:
    def checkStep(step):
        if step > 765:             # RESET TO A STATE IN RANGE
            step = step - 765
        if 0 > step:
            step = 765 + step
                
        return step

    def rainbow(step):
        step = checkStep(step)
    
        if step<255:               # From 0 - 255
            R=255-step
            G=step
            B=0
        else:
            if step<510:           # From 255 - 510
                R=0
                G=510-step
                B=step-255
            else:                  # From 510 - 765
                R=step-510
                G=0
                B=765-step      

        return (int(R),int(G),int(B)), step


    def pixelBrightness(pixel, percentage):
        #Assuming the current color is max value
        dimmedColors =[]
        for maxColor in range(len(pixel)):
            dimmedColor = int(MapValue(percentage, 0, 100, 0, pixel[maxColor]))
            dimmedColors.append(dimmedColor)
    
        return tuple(dimmedColors)
    
    
    def dimPixels(pixelColors, dim):
        for pixel in range(len(pixelColors)):
            dimmedColors = []
            
            for color in range(len(pixelColors[pixel])):
                dimmedColors.append(int(pixelColors[pixel][color]-dim if pixelColors[pixel][color]-dim>0 else 0))
                
            pixelColors[pixel] = tuple(dimmedColors)
    
        return pixelColors
    
    
    def guage(value, pixels, pixelStep, colorSpeed, minValue, maxValue):
        pixelColors         = [(0,0,0)]*pixels
        lastColor           = [(0,0,0)]
        pixelsOn            = MapValue(value, minValue, maxValue, 0, pixels)
        lastPixelBrightness = (pixelsOn-int(pixelsOn))*100
        
        for pixel in range(ceil(pixelsOn)):
            pixelColors[pixel], pixelStep = rainbow(pixelStep)
            pixelStep   += colorSpeed
    
        if lastPixelBrightness != 0:
            pixelColors[ceil(pixelsOn)-1] = pixelBrightness(pixelColors[ceil(pixelsOn)-1], lastPixelBrightness)
    
                
        return pixelColors, pixelStep

    
    def brightnessGuage(value, pixels, minValue, maxValue):
        brightness          = [0]*pixels
        pixelsOn            = MapValue(value, minValue, maxValue, 0, pixels)
        lastPixelBrightness = (pixelsOn-int(pixelsOn))*100
    
        for pixel in range(ceil(pixelsOn)):
            brightness[pixel] = 100
    
        if lastPixelBrightness != 0:
            brightness[ceil(pixelsOn)-1] = lastPixelBrightness
    
        return brightness

    
    def MapValue(value, fromMinimum, fromMaximum, toMinimum, toMaximum):
        if value==fromMaximum:
            return toMaximum #Rounding in the last line may cause it to return a greater value
        if value==fromMinimum:
            return toMinimum
    
        inMax    = abs(fromMinimum-fromMaximum)
        outMax   = abs(toMinimum-toMaximum)
        newValue = value - fromMinimum 

        return 0 if inMax==0 else (newValue*outMax/inMax)+toMinimum
