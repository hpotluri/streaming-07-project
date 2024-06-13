from collections import deque
import pika
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from util_logger import setup_logger
import json
import config  

# Setting up logger
logger, logname = setup_logger(__file__)

# Constants for queues


sender_email = config.EMAIL
sender_password = config.PASSWORD
flag = config.FLAG

# Queues for storing data
CurrentCar = ("Honda", "Accord")
chargeQueue = deque(maxlen=20)


currentTimeStamp = 0

# Function to send email alert
def send_email_alert(sender_email, sender_password, recipient_email, subject, message):
    # Set up SMTP server details
    if flag == False:
        return 
    smtp_server = 'smtp.gmail.com'  # Set your SMTP server here
    smtp_port = 587  # Set the appropriate port for your SMTP server
    smtp_username = sender_email

    # Create a MIME message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Connect to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, sender_password)

    # Send the email
    server.send_message(msg)

    # Close the connection
    server.quit()

# Callback functions for message processing
def timecallback(ch, method, properties, body):
    global currentTimeStamp 
    currentTimeStamp = body.decode()
    ch.basic_ack(delivery_tag=method.delivery_tag)



def carChargercallback(ch, method, properties, body):
    chargingSpeed = 0
    
    jsoncarinfo  = body.decode()
    carinfo = json.loads(jsoncarinfo)

    global CurrentCar
    make = carinfo[0]
    model = carinfo[1]
    capacity: float  = carinfo[2]
    maxLimit : float = carinfo[3]
    currentCharge = carinfo[4]
    
    sys.stdout.flush()
    
    if CurrentCar[1] != model or CurrentCar[0] != make: 
        logger.info(f" [x] New Car Detected ")
        CurrentCar = (make, model)
        chargeQueue.clear()
        currentCharge = 0
    elif currentCharge == maxLimit:
        logger.info(f" [x] Received  {carinfo} at Time {currentTimeStamp}")
        logger.info(f" [o] Car is done charging at {maxLimit} and will be disconnected")
        send_email_alert(sender_email, sender_password, sender_email, "Car Charging Finished", f"Car is done charging at {maxLimit} and will be disconnected")
    elif currentCharge == 'ERROR': 
        logger.info(f" [x] Received  {carinfo} at Time {currentTimeStamp}")
        logger.info(f" [o] An Error occurred when Charging and will be disconnected")
        currentCharge = 0
        send_email_alert(sender_email, sender_password, sender_email, "Car Charging Error", f"An Error occurred when Charging and will be disconnected")
    else:
        if currentCharge == '@':
            currentCharge = 0
        chargeQueue.append(int(currentCharge))
        chargingSpeed = calculate_charging_speed(chargeQueue, float(maxLimit))
        currentPercent = (float(currentCharge) / float(capacity)) * 100
        logger.info(f" [x] Received  {carinfo} at Time {currentTimeStamp}")
        logger.info(f" [o] Current Charging at {chargingSpeed} and is at {currentPercent}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def calculate_charging_speed(charge_queue, max_limit):
    """
    Calculates the current charging speed based on a queue of charges and the maximum charging limit.

    Parameters:
        charge_queue (deque): A deque containing the recent charges.
        max_limit (int): The maximum charging limit.

    Returns:
        float: The current charging speed.
    """
    # Ensure the charge queue is not empty
    if not charge_queue:
        return 0.0
    # Calculate the average charge increase over the last few samples
    total_change = 0
    num_samples = min(len(charge_queue) - 1, 5)  # Limit to at most 5 samples
    if len(charge_queue) == 1:
        return charge_queue[0]
    else:
        for i in range(num_samples):
            total_change += float(charge_queue[i + 1]) - float(charge_queue[i])

        # Calculate the average charge increase per sample
        avg_change = total_change / num_samples if num_samples > 0 else 0

        # Calculate the current charging speed as a percentage per hour
        charging_speed = (avg_change / max_limit) * 100 / num_samples

        return charging_speed






# Main function to listen for task messages
def main(hn: str = "localhost", qn1: str = "task_queue1", qn2: str = "task_queue2"):
    try:
        # Establish connection to RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hn))
    except Exception as e:
        logger.error("ERROR: Connection to RabbitMQ server failed.")
        logger.error(f"Verify the server is running on host={hn}.")
        logger.error(f"The error says: {e}")
        sys.exit(1)

    try:
        channel = connection.channel()
        # Declare durable queues for message persistence
        channel.queue_declare(queue=qn1, durable=True)
        channel.queue_declare(queue=qn2, durable=True)
        # Set prefetch count to limit concurrent message processing
        channel.basic_qos(prefetch_count=1)
        # Register callback functions for message consumption
        channel.basic_consume(queue=qn1, on_message_callback=timecallback)
        channel.basic_consume(queue=qn2, on_message_callback=carChargercallback)
        logger.info(" [*] Ready for work. To exit press CTRL+C")
        # Start consuming messages
        channel.start_consuming()
    except Exception as e:
        logger.error("ERROR: Something went wrong.")
        logger.error(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info(" User interrupted continuous listening process.")
        sys.exit(0)
    finally:
        logger.info("\nClosing connection. Goodbye.\n")
        connection.close()

# Entry point of the program
if __name__ == "__main__":
    main("localhost", "time_stamp", "car_charger")
    sys.stdout.flush()
