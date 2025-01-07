import sacn, time, board, neopixel, json

pixels = neopixel.NeoPixel()
receiver = sacn.sACNreceiver()

CONFIG_DATA = {}

def main():
    global CONFIG_DATA
    global receiver
    global pixels
    
    with open('config/config.json') as f:
        CONFIG_DATA = json.load(f)
    
    pixels = neopixel.NeoPixel(
    CONFIG_DATA['pixel_pin'], int(CONFIG_DATA['num_of_leds']), brightness=int(CONFIG_DATA['brightness']), auto_write=True, pixel_order=CONFIG_DATA['pixel_order']
    )
    print("NeoPixel initialized")
    
    receiver = sacn.sACNreceiver()
    receiver.start()  # start the receiving thread
    
    print("Listening for DMX data...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        receiver.stop()  # stop the receiving thread
        pixels.fill((0, 0, 0)) # turn all LEDs off
        pixels.show()
        print("Stopped")
        
# define a callback function
@receiver.listen_on('universe', universe=1)  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
    if packet.dmxStartCode == 0x00:  # ignore non-DMX-data packets
        print(packet.dmxData)  # print the received DMX data
        
        pixels.fill((0, 0, 0)) # turn all LEDs off to clear any previous data
        dmxIndex = 0
        for pixelIndex in range(int(CONFIG_DATA['num_of_leds'])):
            pixels[pixelIndex] = (packet.dmxData[dmxIndex], packet.dmxData[dmxIndex+1], packet.dmxData[dmxIndex+2])
            dmxIndex += 3
        
        pixels.show()
        time.sleep(1/int(CONFIG_DATA['fps']))

if __name__ == "__main__":
    pass