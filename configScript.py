import getpass
from util_logger import setup_logger

logger, logname = setup_logger(__file__)

# Database configuration
sender_email = 'XXXX@gmail.com'
sender_password = 'fill out your password here '


def get_user_credentials():
    email = input("Enter your email address: ")
    password = getpass.getpass("Enter your password: ")
    return email, password

def create_config_file(email, password):
    with open("config.py", "w") as f:
        f.write(f"EMAIL = '{email}'\n")
        f.write(f"PASSWORD = '{password}'\n")
        f.write(f"FLAG = True\n")
    logger.info("Config file created with email and password.")

def main():
    logger.info("Starting configuration setup.")
    print("Welcome to the configuration setup!")
    flag = input("Would you like to receive Email Notifications (y/n): ")
    logger.info(f"User chose to {'enable' if flag == 'y' else 'disable'} email notifications.")
    # Get user credentials
    if flag.lower() == "y":
        email, password = get_user_credentials()
        # Create the config file
        create_config_file(email, password)
    else:
        with open("config.py", "w") as f:
            f.write(f"EMAIL = ' '\n")
            f.write(f"PASSWORD = ' '\n")
            f.write(f"FLAG = False\n")
        logger.info("Config file created with empty email and password, notifications disabled.")
    print("Configuration setup complete. Your credentials have been saved to config.py.")
    logger.info("Configuration setup complete.")

if __name__ == "__main__":
    main()
