import sacn, time, board, neopixel, json

pixels = neopixel.NeoPixel()
receiver = sacn.sACNreceiver()

CONFIG_DATA = {}
FPS = 30
debugging = True

def main():
    global CONFIG_DATA
    global receiver
    global pixels
    global FPS
    
    with open('config/config.json') as f:
        CONFIG_DATA = json.load(f)
    
    FPS = int(CONFIG_DATA['fps'])
    PIXEL_PIN = CONFIG_DATA['pixel_pin']
    NUM_OF_LEDS = int(CONFIG_DATA['num_of_leds'])
    BRIGHTNESS = int(CONFIG_DATA['brightness'])
    PIXEL_ORDER = CONFIG_DATA['pixel_order']
    
    pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_OF_LEDS, brightness=BRIGHTNESS, auto_write=False, pixel_order=PIXEL_ORDER
    )
    if(debugging):
        print("NeoPixel initialized")
    
    receiver = sacn.sACNreceiver()
    receiver.start()  # start the receiving thread
    
    if(debugging):
        print("Listening for DMX data...")
        print("Press Ctrl+C to stop")
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        if(debugging):
            print("Stopping...")
    finally:
        receiver.stop()  # stop the receiving thread
        pixels.fill((0, 0, 0)) # turn all LEDs off
        pixels.show()
        if(debugging):
            print("Stopped")
        
# define a callback function
@receiver.listen_on('universe', universe=1)  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
    global FPS
    global pixels
    
    if packet.dmxStartCode == 0x00:  # ignore non-DMX-data packets
        # print(packet.dmxData)  # print the received DMX data
        
        pixels.fill((0, 0, 0)) # turn all LEDs off to clear any previous data
        
        dmxIndex = 0
        for pixelIndex in range(len(pixels)):
            pixels[pixelIndex] = (packet.dmxData[dmxIndex], packet.dmxData[dmxIndex+1], packet.dmxData[dmxIndex+2])
            dmxIndex += 3
        
        pixels.show()
        time.sleep(1/FPS)

if __name__ == "__main__":
    pass