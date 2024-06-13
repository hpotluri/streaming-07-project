import csv
import random
import datetime
from util_logger import setup_logger

logger, logname = setup_logger(__file__)

# Define dictionaries mapping makes to their respective models
car_models = {
    "Tesla": ["Model S", "Model 3", "Model X", "Model Y"],
    "Nissan": ["Leaf"],
    "Chevrolet": ["Bolt EV"],
    "BMW": ["i3"],
    "Audi": ["e-tron"],
    "Ford": ["Mustang Mach-E", "Focus Electric"],
    "Hyundai": ["Kona Electric", "Ioniq Electric"],
    "Kia": ["Niro EV", "Soul EV"],
    "Jaguar": ["I-PACE"],
    "Volkswagen": ["ID.4", "e-Golf"],
    "Mercedes-Benz": ["EQC"],
    "Porsche": ["Taycan"],
    "Rivian": ["R1T", "R1S"],
    "Lucid": ["Air"],
    "Volvo": ["XC40 Recharge"],
    "Fisker": ["Ocean"],
    "Mazda": ["MX-30"],
    "Lexus": ["UX 300e"],
    "Mini": ["Cooper SE"],
    "Honda": ["Clarity Electric"],
    "Toyota": ["RAV4 EV"],
    "Smart": ["EQ fortwo"],
    "Polestar": ["2"],
    "Byton": ["M-Byte"],
    "Bollinger": ["B1", "B2"],
    "Canoo": ["Lifestyle Vehicle"],
    "Faraday Future": ["FF 91"],
    "NIO": ["ES6", "ES8"],
    "Rimac": ["C_Two"]
}

def generate_charging_data(filename, num_cars):
    # Define the header for the CSV file
    header = ['Timestamp', 'Make', 'Model', 'Battery Size (kWh)', 'Charging Limit (%)', 'Current Charge (%)']

    # Open the CSV file in write mode
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(header)
        logger.info("Header written to the CSV file")

        # Generate charging data for each car
        for _ in range(num_cars):
            # Generate random make and model
            make = random.choice(list(car_models.keys()))
            model = random.choice(car_models[make])

            # Generate random battery size (between 50 and 100 kWh)
            battery_kwh = random.randint(50, 100)

            # Generate random charging limit (above 70% and below battery size)
            charging_limit = min(random.randint(71, 100), battery_kwh)

            # Write the metadata for the charging session
            start_time = datetime.datetime.now()
            metadata = [start_time.strftime("%Y-%m-%d %H:%M:%S"), make, model, battery_kwh, charging_limit, "@"]
            writer.writerow(metadata)
            logger.info(f"Metadata written for {make} {model} with battery size {battery_kwh} kWh and limit {charging_limit}%")

            # Initialize current charge randomly
            current_charge = random.randint(0, charging_limit)

            # Initialize end time (when charge limit is reached)
            end_time = start_time + datetime.timedelta(hours=(battery_kwh - current_charge) / 250)

            # Write charging data until charge limit is reached or user disconnects
            while current_charge < charging_limit:
                # Increment current charge randomly
                current_charge += random.randint(1, 10)

                # Ensure current charge does not exceed charging limit
                current_charge = min(current_charge, charging_limit)

                # Simulate random disconnection with 5% probability
                if random.random() < 0.05:
                    # Write the charging data for the current time step
                    timestamp_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
                    row = [timestamp_str, make, model, battery_kwh, charging_limit, "ERROR"]
                    writer.writerow(row)
                    logger.warning(f"Error occurred for {make} {model} at {timestamp_str}")
                    break

                # Calculate timestamp for this sample
                timestamp = start_time + datetime.timedelta(seconds=random.randint(0, 3600))  # Randomize timestamp

                # Format timestamp as string
                timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

                # Write the charging data for the current time step
                row = [timestamp_str, make, model, battery_kwh, charging_limit, current_charge]
                writer.writerow(row)
                logger.info(f"Charging data written for {make} {model} at {timestamp_str} with charge {current_charge}%")

            # If charge limit is reached, add final data point
            if current_charge == charging_limit:
                timestamp_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
                final_row = [timestamp_str, make, model, battery_kwh, charging_limit, current_charge]
                writer.writerow(final_row)
                logger.info(f"Final charge limit reached for {make} {model} at {timestamp_str} with charge {current_charge}%")

    logger.info(f"Charging data generated and saved to {filename}")

# Example usage:
generate_charging_data("charging_data.csv", num_cars=5)
