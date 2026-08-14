# CYT160---Final Project-Raspberry Pi Temp Sensor
This readme is used for documentation on how to set up this project.

**Step 1: Ubuntu VM setup**
- Create a t2.medium instance in EC2 with a new security group, and a new key pair in order to SSH into the machine later. You will also have to change the permissions of the key pair to be more strict in accordance with standard AWS policies.
- Attach the virtual machine to a private cloud. Use the IPv4 CIDR of the private cloud to assign a private IP address to the EC2 instance.
- For the security group, create inbound rules for Port 22 (SSH), as well as Port 1883 (MQTT). The inbound rules for SSH can be any that let you access the machine, but for the purpose of the project, Port 1883 has to be allowed for connections from anywhere.
- Attach an elastic public IP address to the virtual machine.

Step 2: Rapsberry Pi / Hardware setup & integrations
- Plug in the power adapter for the Raspberry Pi.
- Set up the OS for the Raspberry Pi by plugging a MicroSD card with the OS onto the Raspberry Pi. The OS can be found at www.raspberrypi.com/software/ using the Raspberry Pi imager. Follow the on-screen instructions to install the OS, and enable I2C communications by running the command "sudo-raspi-config" in the terminal.
- Use the JST 4H-pin premium male header cable to connect the temperature sensor to the raspberry pi. Then, use female to female jumper wires as follows: Connect the red wire to GPIO pin 1 (3.3V), the black wire to pin 6 (GND), the blue wire to pin 3 (SDA), and the yellow wire to pin 5 (SCL).
- Connect additional necessary equipment as needed, such as a mouse and keyboard.
- Install the following software: Pip, adafruit-circuitpython-mcp9808, python, python3-pip, python3-venv, mosquitto, mosquitto-clients, hping3, and Hydra.
- Create a virtual environment with the command: "python3 -m venv iot_project_env" and then active it with the command "source iot_project_env/bin/activate".
- Additionally, take the "mqtt-lab.conf" file from the repository and copy it over to your Rapsberry Pi, placing it in the directory /etc/mosquitto/conf.d.

Step 3: Set up the Raspberry Pi for AWS IoT:
- In the AWS Management Console, search for "IoT Core" in the search bar and select it to go to the AWS IoT Core dashboard. In the IoT Core dashboard, click on "connect device" and then "Things". Then, click on "Create a thing" to add a new IoT device (in this case, your Raspberry Pi). Give your device a name (e.g., RaspberryPi), and then click "Next" to proceed with the thing creation process. When prompted to choose a platform and SDK, select: Linux as the platform and Python as the SDK.
- Download the connection kit from AWS, which consists of the Amazon Root CA certificate (AmazonRootCA1.pem), the device certificate (raspberrypi-certificate.pem.crt), and the device private key (raspberrypi-private.pem.key). Move those files to the Raspberry Pi - you can either use a USB drive or SSH into the Raspberry Pi and transfer the files using 
scp or other file transfer methods.

Step 4: Utilizing the temperature sensor script:
First, download the script from the repository to your Rapsberry Pi. Within the script, make the following changes:
- Change the "host" field in the to the elastic public IP address of your Ubuntu VM. Additionally, under the "Connect to EC2 Mosquitto" section, replace the IP address of the ec2_client.connect field with your VM's elastic public IP address.
- Under the AWS IoT Core settings, change the host to point to your AWS IoT endpoint
- Additionally, change the rootCAPath to point to the correct directory of the AWS root CA certificate downloaded to your Raspberry Pi from Step 3.
- Change the certificatepath to point to the correct directory of your Raspberry Pi's device certificate, and also change the privateKeyPath to point to the correct directory of your device's private key. 

Step 5: Set up the IDS:
- Install Suricata.
- Replace the file in /etc/suricata/suricata.yaml on your VM with the suricata.yaml file from the repository. Additionally, edit the file to make sure the interface under 'af-packet' has a matching name with the main network interface of your Ubuntu VM.
- Use the custom rules file in the repository and place it in /var/lib/suricata/rules/custom.rules on your VM.
- Then enable the Suricata service and start it.
- Install Filebeat with the command "curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.12.0-amd64.deb" followed by "sudo dpkg -i filebeat-8.12.0-amd64.deb" and "sudo apt update", 
- Replace the file in /etc/filebeat/filebeat.reference.yml with the one in the repository. You do not need to make any further changes to this file. Then enable the Filebeat service and start it.
- Install Elasticsearch and add the necessary key with the following commands: "sudo mkdir -p /etc/apt/keyrings", "wget -qO- https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor | sudo tee /etc/apt/keyrings/elasticsearch.gpg > /dev/null", "echo "deb [signed-by=/etc/apt/keyrings/elasticsearch.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elasticsearch.list", "sudo apt update && sudo apt install -y elasticsearch".
- Replace the file in /etc/elasticsearch/elasticsearch.yml with the one in the repository. Under cluster.initial_master_nodes, change the ip address to the private IP address of the EC2 instance.
- Create a directory for heap options, along with a file for the heap options, for ElasticSearch using the following commands: "sudo mkdir -p /etc/elasticsearch/jvm.options.d" followed by "sudo nano /etc/elasticsearch/jvm.options.d/heap.options". Under the heap.options file add two lines of text, both of which will say "Xma512m". This will set the minimum and maximum heap options to 512 MB.
- Change the permissions for the heap options file & directory with the following commands: "sudo chown elasticsearch:elasticsearch /etc/elasticsearch/jvm.options.d/heap.options", "sudo chmod 644 /etc/elasticsearch/jvm.options.d/heap.options", "sudo chmod 755 /etc/elasticsearch/jvm.options.d", and "sudo chmod 755 /etc/elasticsearch".
- Under the file "/etc/elasticsearch/jvm.options", edit it and comment out any heap options that are uncommented to avoid heap option conflicts.
- Apply the changes by restarting ElasticSearch, if you have not enabled and started the service already.
- Install Kibana
- Replace the file in /etc/kibana/kibana.yml with the one in the repository. You do not need to make any changes to this file. Then, enable the service and start it.
- Connect to Kibana via ssh on your local PC using the command: ssh -i "YourVMKey.pem" -L 5601:localhost:5601 ubuntu@yourelasticpublicip. You will then be able to connect to Kibana via http://localhost:9201 on your local PC. If necessary, login with the user: "kibana_user" as well as the password "NewPass123!".

Step 6:
- In AWS IoT Core, navigate to your thing, followed by the certificate of your thing, and the RaspberryPi policy.
- <Policy edits to be published here>
- Additionally, add to the policy two things: an "Allow" effect for the action "iotConnect", aimed at the policy resource "arn:aws:iot-us-east-1:<insert your AWS account ID>:client/rapsberrypi-client, and an "Allow" effect for the action "iotPublish", aimed at the policy resource "arn:aws:iot:us-east-1:<insert your AWS account ID>:client/raspberrypi-client. This will allow for the second instance of traffic mirroring using the mosquitto.py script.
