There are several parts to the glados hardware and software door control system.
1. Synapse door node which consists of a synapse wireless chip, a door latch or magnetic lock, and software on the synapse (door_node_rfid). This included rfid reader.
2. Raspbery pi or other bridge node to receive door information and FOB key information and pass it to glados web service
3. Glados web service to store fob keys, names, and any other associated information.

Synapse Portal Software, Reference material, can be found:
http://forums.synapse-wireless.com/showthread.php?t=9

The raspberry pi needs PyCrypto for encryption settings with SnappyConnect.

Good starting material and reference can be found here:
https://www.sparkfun.com/tutorials/367

This system is the part of glados that will be on the Raspberry Pi's

This part receives an RFID card swipe and checks if a person is authorized for a door. This will interface with the glados system


Synapse Door Node for RF266 chip.

Introduction: The RF266 Synapse chip was packed with a home made PCB that controls the door latch. The schematic can be found in the schematics folder are written with Fritzing. RFID reader has serial out and is in the ID-12LA (ID20LA) family. The RF266 node reads the fob, sends it to the raspi bridge node which then does a restful call to our glados server. If the person is authorized for the door we get an open_door: true response otherwise a fail. Based on that response sent back to the node, the node opens the door or doesn't and potentially flashes an led red/green or other activities. 

The RF266 node chip needs to be flashed using the synapse Portal software. I'm on OSX so using python 2.7. I'm flashing the node with RF266 with AES128 firmware. Make sure to Factory Default NV params, and erase any snappy image on it. Make sure all the nodes are upgrade and flashed to the same firmware or none will communicate. This includes the bridge node. Our system is using the AES128 RF266 firmware. 

There is an order to getting the script uploaded and the encryption turned on.
1. Do what I mentioned above and upgrade the firmware, clear all NV params and erase Snappy images.
2. Copy the rfid_reader_node.py file from glados_rfid folder into the snappyimages folder. Sadly anytime you save your file it goes there so remember to copy it back to the git repo when you want to commit.
3. Connect your rf266 in the usb connector plug it into your computer and conect to it from portal.
4. Look at the node views it should show up with it's address.
5. Double click the node of interest and you should end up with Node Info window.
6. There should be a doucment with a tiny upward facing green array. that uploads your script. Choose the rfid_reader_node.py script and upload it. 
7. Click the little gear icon now to add encryption. 
7a. Device type you can change the Device Name
7b. Security Tab, Set Encryption Type to 1, Encryption Key is the same on on the pi as auth.json. Ask Hacklab David Volbracht, David Vitrant or Mike Greenberg for the key and why you need it.
7c. Before clicking OK. make sure the Reboot After Apply is checked, then click OK.
8. The node will reboot and will now disapear from the nodeviews. This happens because the node will ONLY talk to encrypted nodes and our bridge node is well not encrypted. To encrypt the bridge node go to Options -> Configure Crypto Settings. 
8a. Check Encrypt and decrypt all packets, Type AES128, Key is the same key you filled above. then click ok.
8b. Refresh the node or disconnect and reconnect, wait a few seconds and if the other node is powered on you should be able to see it from the bridge node. 
8c. REMEMBER: Only encrypted nodes can talk to encrypted nodes, unencrypted to unencrypted. That includes the bridge node. Remember to uncheck and re-check encryption when setting up new nodes.
9. Put the programmed chip back into it's PCB and install in the door like the schematic explains.


Raspberry Pi Bridge Node:
This is the software running on the raspberry pi with the bridge node.

gems to install for GPI access and serial access:
wiringpi
sudo apt-get install ruby1.9.1-dev
ruby-serialport

Introduction:

This pi is considered to be node address:

raspi_node = "\x00\x00\x20"

You need to be running python on this server and have downloaded the snapyconnect python libraries.
You will also need to have a rf266 chip, with any xbee to usb connector that is plugged into the raspberry pi. 

The pi will use serial to "bridge" the synapse on the Pi with the whole Synapse mesh network and transfer communication.

This python node has access to the full python library world and so can be
made to integrate with other tools and libraries. We are using httpconnect
to check door access and then have callbacks go and open the door on the synapse
node that called for the fob check.

In addition doorbell dingdong access is provided and will probably get further
integrated as we add more doors and equipment access.

read-more about the synapseclient tools:
https://www.sparkfun.com/tutorials/367
manual:
http://www.synapse-wireless.com/documents/products/Synapse-SNAP-Connect-Python-Package-Manual.pdf

Folder: sample_glados_runtime_files
has a sample /etc/rc.local file that you need to install as root.
We need the run_glados.sh script too and folders to be present for that structure.

Instructions:
1. You will need to download snapconnect-3.1.0 for python 2.7 from here: http://forums.synapse-wireless.com/showthread.php?t=9
2. In the folder where you will install the glados_receiver.py script and the auth.json script (not committed) unpack the snapconnect script.
3. Run python setup.py install and install any missing libraries as you go.
4. Make sure you install https://www.dlitz.net/software/pycrypto/ or NO AES encryption will work. 
5. You might have to do this with sudo as the GPIO reading is sduo and the sample_glados_runtime_files are run through root. 
6. If all goes well you should be able to at this point plug in the rf266 bridge, and run in command line: python glados_receiver.py (or sudo)
7. Swipe your fob on the door node and watch the fob key show up on the pi if it's plugged into a monitor. 
8. If that doesn't work try fixing the AES key as that is the likely culprit. 
