# config.py

# Database configuration
sender_email = 'XXXX@gmail.com'
sender_password = 'fill out your password here '


import getpass

def get_user_credentials():
    email = input("Enter your email address: ")
    password = getpass.getpass("Enter your password: ")
    return email, password

def create_config_file(email, password):
    with open("config.py", "w") as f:
        f.write(f"EMAIL = '{email}'\n")
        f.write(f"PASSWORD = '{password}'\n")

def main():
    print("Welcome to the configuration setup!")

    # Get user credentials
    email, password = get_user_credentials()

    # Create the config file
    create_config_file(email, password)

    print("Configuration setup complete. Your credentials have been saved to config.py.")

if __name__ == "__main__":
    main()