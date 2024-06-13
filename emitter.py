"""
Harinya Potluri 

5/27/24

"""

import pika
import sys
import webbrowser
import csv
import time
from collections import defaultdict
import json
from util_logger import setup_logger

logger, logname = setup_logger(__file__)

HOST = "localhost"


def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website"""
    ans = input("Would you like to monitor RabbitMQ queues? y or n ")
    logger.info("User input received for RabbitMQ monitoring site offer")
    if ans.lower() == "y":
        webbrowser.open_new("http://localhost:15672/#/queues")
        logger.info("Opened RabbitMQ Admin website")
        print()

def send_message(host: str, queue_name: str, message):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (str): the message to be sent to the queue
    """

    try:
        message_body = json.dumps(message)
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        ch.queue_declare(queue=queue_name, durable=True)

        # use the channel to publish a message to the queue
        # every message passes through an exchange
        ch.basic_publish(exchange="", routing_key=queue_name, body=message_body)
        # log a message for the user
        logger.info(f" [x] Sent {message} to {queue_name}")
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        # close the connection to the server
        conn.close()


def readData(filename):
    """
    Reads the file and creates a list of timestamps and a dictionary of car charges.
    
    Parameters:
        filename (str): name of the csv file used to pull data from. 
    
    Returns:
        list: list of timestamps
        dict: dictionary containing car charges
    """
    listofTimes = []
    carCharges = defaultdict(list)  # Use defaultdict to automatically create lists for each car

    with open(filename, 'r') as csvFile:
        file = csv.reader(csvFile)
        header = next(file)  # Skip the header line

        # Read each row in the file
        for row in file:
            timestamp = row[0]  # First element is the timestamp
            cars = row[1:]  # Rest of the elements are charges for each car
            
            listofTimes.append(timestamp)  # Add timestamp to list

            # Iterate over each car charge and add it to the dictionary
            for i, charge in enumerate(cars):
                carCharges[header[i+1]].append(charge)

    return listofTimes, carCharges


def print_data(list_of_times, car_charges):
    header = ["Timestamp", "Make", "Model", "Battery Size (kWh)", "Charging Limit (%)", "Current Charge (%)"]
    
    # Log the header
    logger.info("\t".join(header))
    
    # Log each row of data
    for timestamp, charges in zip(list_of_times, zip(*car_charges.values())):
        logger.info(f"{timestamp}\t" + "\t".join(charges))


# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":  
    show_offer = False
    if show_offer:
        offer_rabbitmq_admin_site()

    filename = "charging_data.csv"  # Replace with the filename of your generated data
    listofTimes, carCharges = readData(filename)
    
    for timestamp, charges in zip(listofTimes, zip(*carCharges.values())):
        # time.sleep(.5)  # Need to change to 30 secs but for testing this is preferable
        sys.stdout.flush()
        send_message(HOST, "time_stamp", timestamp)
        send_message(HOST, "car_charger", charges)
