import getpass
from util_logger import setup_logger

# Set up logging
logger, logname = setup_logger(__file__)

def get_user_credentials():
    """
    Prompt the user to enter their email and password securely.
    Password entry will be masked for privacy.
    
    Returns:
        tuple: Contains the user's email and masked password.
    """
    email = input("Enter your email address: ")
    password = getpass.getpass("Enter your password: ")
    return email, password

def create_config_file(email, password):
    """
    Creates a configuration file with the user's email and password.
    This file also includes a flag to enable email notifications.
    
    Parameters:
        email (str): User's email address.
        password (str): User's password.
    """
    with open("config.py", "w") as f:
        f.write(f"EMAIL = '{email}'\n")
        f.write(f"PASSWORD = '{password}'\n")
        f.write(f"FLAG = True\n")
    logger.info("Config file created with email and password.")

def main():
    """
    Main function to run the configuration setup.
    Asks the user if they want to enable email notifications and
    proceeds based on their response.
    """
    logger.info("Starting configuration setup.")
    print("Welcome to the configuration setup!")
    flag = input("Would you like to receive Email Notifications (y/n): ")
    logger.info(f"User chose to {'enable' if flag == 'y' else 'disable'} email notifications.")
    
    # Get user credentials if notifications are enabled
    if flag.lower() == "y":
        email, password = get_user_credentials()
        create_config_file(email, password)
    else:
        # Create a configuration file with empty values and notifications disabled
        with open("config.py", "w") as f:
            f.write(f"EMAIL = ' '\n")
            f.write(f"PASSWORD = ' '\n")
            f.write(f"FLAG = False\n")
        logger.info("Config file created with empty email and password, notifications disabled.")
    
    print("Configuration setup complete. Your credentials have been saved to config.py.")
    logger.info("Configuration setup complete.")

if __name__ == "__main__":
    main()
