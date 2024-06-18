# main.py
from StagePlan import DragNumbers
from network_manager import NetworkManager

if __name__ == "__main__":
    network_manager = NetworkManager(None)  # Create a NetworkManager instance
    app = DragNumbers(network_manager)  # Create a DragNumbers instance and pass the NetworkManager instance
    network_manager.parent = app  # Set the parent of the NetworkManager instance to the DragNumbers instance
    app.mainloop()  # Start the main event loop
