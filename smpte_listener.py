import socket
import threading

class SMPTETimecodeListener:
    def __init__(self, ip="0.0.0.0", port=5005, callback=None):
        self.UDP_IP = ip  # IP address to listen on
        self.UDP_PORT = port
        self.callback = callback  # Optional callback function to pass the timecode to the parent
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))
        self.running = False
        self.thread = None

    def listen_for_timecode(self):
        """Listen for SMPTE timecode messages."""
        while self.running:
            data, addr = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
            timecode = data.decode()
            print(f"Received timecode: {timecode}")
            
            # Optionally pass the timecode to the callback
            if self.callback:
                self.callback(timecode)

    def start(self):
        """Start the SMPTE timecode listener in a separate thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.listen_for_timecode)
            self.thread.start()

    def stop(self):
        """Stop the SMPTE timecode listener."""
        if self.running:
            self.running = False
            self.thread.join()

    def set_parameters(self, ip=None, port=None):
        """Set the IP address and port to listen on."""
        if ip:
            self.UDP_IP = ip
        if port:
            self.UDP_PORT = port
        self.sock.bind((self.UDP_IP, self.UDP_PORT))  # Rebind to the new settings

# Parent Program Integration
def parent_program():
    listener = SMPTETimecodeListener(callback=handle_timecode)
    
    # Parent can start the listener
    listener.start()

    # Simulate parent controlling the listener
    try:
        while True:
            command = input("Enter command (start, stop, set, quit): ").strip().lower()
            if command == "start":
                listener.start()
            elif command == "stop":
                listener.stop()
            elif command.startswith("set"):
                _, ip, port = command.split()
                listener.set_parameters(ip=ip, port=int(port))
            elif command == "quit":
                listener.stop()
                break
            else:
                print("Invalid command.")
    except KeyboardInterrupt:
        listener.stop()

def handle_timecode(timecode):
    """Callback function to process the timecode received from the listener."""
    print(f"Processing timecode: {timecode}")
    # Your logic to handle the timecode, e.g., using it for synchronization
    # For example, you could update a UI, trigger an event, etc.

if __name__ == "__main__":
    parent_program()

