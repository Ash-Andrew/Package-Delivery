# Andrew Ashbaker -- Student ID: 011694372 
# WGUPS Routing Program Implementation. Nearest Neighbor Algorithm and Hash table
# WGU Data Structures & Algorithms II Task 2

import csv
import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
from Truck import DeliveryTruck
from CreateHashTable import CustomHashMap
from Package import Parcel
import argparse

# Function to read CSV files and return a list of rows
# This helper function abstracts the CSV reading functionality to keep the code modular and reusable
def read_csv(file_path):
    with open(file_path) as csvfile:
        return list(csv.reader(csvfile))

# Read the three provided CSV files for the parcel data
# Reading distance, address, and package data into corresponding lists
CSV_Distance = read_csv("CSV/Distance_File.csv") # Distance Data
CSV_Address = read_csv("CSV/Address_File.csv") # Address Data
CSV_Package = read_csv("CSV/Package_File.csv") # Package/Parcel Data

# Function to load package data into the hash table
# This function parses the CSV data and creates Parcel objects,
# then inserts them into the hash table with parcel ID as the key
def load_package_data(filename, package_hash_table):
    with open(filename) as package_info:
        package_data = csv.reader(package_info)
        for package in package_data:
            parcel_id = int(package[0])
            parcel_address = package[1]
            parcel_city = package[2]
            parcel_state = package[3]
            parcel_zipcode = package[4]
            parcel_deadline = package[5]
            parcel_weight = package[6]
            parcel_status = "At Hub"
            # Create a Parcel object and insert it into the hash table
            parcel = Parcel(parcel_id, parcel_address, parcel_city, parcel_state, parcel_zipcode, parcel_deadline, parcel_weight, parcel_status)
            package_hash_table.insert(parcel_id, parcel)

# Function to find the distance between two addresses for optimal route calculation
# It uses the CSV_Distance data to find the distance between two locations based on their indices
def distance_in_between(x_value, y_value):
    distance = CSV_Distance[x_value][y_value]
    if distance == '':
        distance = CSV_Distance[y_value][x_value]
    return float(distance)

# Function to return the address ID for each package based on the address string
# This function matches the address string to the address data to find the corresponding address ID
def extract_address(address):
    for row in CSV_Address:
        if address in row[2]:
            return int(row[0])
    print(f"Address not found: {address}")
    return None

# Global variable to store delivered packages
delivered_packages_global = {
    1: [],
    2: [],
    3: []
}
def delivering_packages(truck, package_hash_table, truck_number):
    not_delivered = [package_hash_table.lookup(package_id) for package_id in truck.packages]
    truck.packages.clear()
    address_update_done = False
    current_mileage = 0.0
    delivered_packages = []

    # Set the departure time for the truck before delivering any packages
    truck.depart_time = truck.time

    while not_delivered:
        next_address = 2000
        next_package = None

        # Handle address update for package 9
        if truck_number == 3 and not address_update_done and truck.time >= datetime.timedelta(hours=10, minutes=20):
            package_9 = package_hash_table.lookup(9)
            if package_9:
                print(f"Updating address for package #9 at time {truck.time}")
                package_9.update_address("410 S State St", "Salt Lake City", "UT", "84111")
                address_update_done = True
                # Ensure package 9 is not already in the not_delivered list before appending it
                if package_9 not in not_delivered:
                    not_delivered.append(package_9)

        for parcel in not_delivered:
            x_value = extract_address(truck.address)
            y_value = extract_address(parcel.address)
            if x_value is None or y_value is None:
                continue
            current_distance = distance_in_between(x_value, y_value)
            if current_distance < next_address:
                next_address = current_distance
                next_package = parcel

        if next_package is None:
            print("No valid next package found.")
            break

        not_delivered.remove(next_package)

        current_mileage += next_address
        truck.mileage = current_mileage
        truck.address = next_package.address
        truck.time += datetime.timedelta(hours=next_address / 18)
        next_package.departure_time = truck.depart_time  # Ensure departure time is set before delivery
        next_package.delivery_time = truck.time
        next_package.status = "Delivered"

        print(f"Current address: {truck.address}, Next address: {next_package.address}, Distance: {next_address}")
        print(f"Truck {truck_number}: Delivered package {next_package.ID} to {next_package.address} at {truck.time}, truck mileage: {truck.mileage}")

        delivered_packages.append((next_package.delivery_time, next_package, truck.mileage))

        # Ensure the truck departure time is only set once
        truck.depart_time = min(truck.depart_time, next_package.departure_time)

    for parcel in not_delivered:
        print(f"Undelivered package: ID {parcel.ID}, Address {parcel.address}, Status {parcel.status}")

    return delivered_packages

# Function to parse time strings with AM/PM format and convert them to timedelta
# This function handles both 12-hour and 24-hour formats
def parse_time_string(time_str):
    if 'AM' in time_str or 'PM' in time_str:
        time_obj = datetime.datetime.strptime(time_str, '%I:%M%p')
    else:
        time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S')
    return datetime.timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)

# Function to display the status of packages in a new window
# This function creates a GUI window to show the delivery status of packages and truck mileage
def display_status(package_hash_table, convert_timedelta, truck1, truck2, truck3, single_package_id=None):
    root = tk.Tk()
    root.title("Parcel Status")
    root.configure(bg='lightblue')

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=120, height=55, bg='white', fg='black', font=("Helvetica", 12))
    text_area.pack(pady=10, padx=10)

    def calculate_total_mileage(truck_number):
        delivered_packages = delivered_packages_global[truck_number]
        total_mileage = 0.0
        for delivery_time, parcel, mileage in delivered_packages:
            if delivery_time <= convert_timedelta:
                total_mileage = mileage  # Update the total mileage to the mileage of the current delivery
        return total_mileage

    truck1_mileage = calculate_total_mileage(1)
    truck2_mileage = calculate_total_mileage(2)
    truck3_mileage = calculate_total_mileage(3)

    # Display truck mileage information with clearer formatting
    mileage_info = (
        f"Truck 1 Mileage: {truck1_mileage:.2f} miles\n"
        f"Truck 2 Mileage: {truck2_mileage:.2f} miles\n"
        f"Truck 3 Mileage: {truck3_mileage:.2f} miles\n"
        f"Total Mileage: {(truck1_mileage + truck2_mileage + truck3_mileage):.2f} miles\n"
    )
    text_area.insert(tk.END, mileage_info + "\n\n", 'header')

    def get_truck_number(package_id):
        if package_id in truck1.packages:
            return 1
        elif package_id in truck2.packages:
            return 2
        elif package_id in truck3.packages:
            return 3
        return "Unknown"

    def display_packages_for_truck(truck_number):
        delivered_packages = delivered_packages_global[truck_number]
        delivered_packages.sort(key=lambda x: x[0])
        for delivery_time, parcel, mileage in delivered_packages:
            parcel.update_status(convert_timedelta)
            if parcel.ID == 9 and convert_timedelta < datetime.timedelta(hours=10, minutes=20):
                parcel.update_address("300 State St", "Salt Lake City", "UT", "84103")
            status = f"Truck {truck_number}: {str(parcel)}, truck mileage: {mileage:.2f}"
            if parcel.delivery_time and parcel.delivery_time <= convert_timedelta:
                status = f"DELIVERED: {status}"
                text_area.insert(tk.END, status + "\n", 'delivered')
            elif parcel.departure_time and parcel.departure_time <= convert_timedelta:
                status = f"EN ROUTE: {status}"
                text_area.insert(tk.END, status + "\n", 'enroute')
            else:
                text_area.insert(tk.END, status + "\n", 'athub')

    if single_package_id is not None:
        parcel = package_hash_table.lookup(single_package_id)
        parcel.update_status(convert_timedelta)
        if parcel.ID == 9 and convert_timedelta < datetime.timedelta(hours=10, minutes=20):
            parcel.update_address("300 State St", "Salt Lake City", "UT", "84103")
        truck_number = get_truck_number(parcel.ID)
        status = f"Truck {truck_number}: {str(parcel)}, truck mileage: {truck1.mileage if truck_number == 1 else truck2.mileage if truck_number == 2 else truck3.mileage:.2f}"
        text_area.insert(tk.END, status + "\n")
    else:
        # Display packages in order of each truck
        text_area.insert(tk.END, "Truck 1 Packages:\n", 'subheader')
        display_packages_for_truck(1)
        text_area.insert(tk.END, "\nTruck 2 Packages:\n", 'subheader')
        display_packages_for_truck(2)
        text_area.insert(tk.END, "\nTruck 3 Packages:\n", 'subheader')
        display_packages_for_truck(3)

    text_area.tag_config('header', font=("Helvetica", 14, "bold"), background='lightblue', foreground='darkblue')
    text_area.tag_config('subheader', font=("Helvetica", 12, "bold"), background='lightgrey', foreground='black')
    text_area.tag_config('delivered', background='green', foreground='white')
    text_area.tag_config('enroute', background='yellow', foreground='black')
    text_area.tag_config('athub', background='red', foreground='white')

    text_area.configure(state='disabled')

    root.mainloop()

# Function to start the main interface
# This function creates the main GUI interface for the application
def start_interface(package_hash_table, truck1, truck2, truck3):
    root = tk.Tk()
    root.title("WGUPS Parcel Service")
    root.configure(bg='lightblue')

    title_label = tk.Label(root, text="WGUPS Parcel Service", font=("Helvetica", 16, "bold"), bg='lightblue', fg='darkblue')
    title_label.pack(pady=10)

    mileage_label = tk.Label(root, text=f"Total Mileage: {truck1.mileage + truck2.mileage + truck3.mileage}", font=("Helvetica", 14), bg='lightblue', fg='darkgreen')
    mileage_label.pack(pady=10)

    # Function to check the status of packages at a specific time or between times
    def check_status():
        user_time = simpledialog.askstring("Input", "Enter a single time to check the status of a Parcel(s) or two times separated by a comma to check the status between times (e.g., HH:MM:SS or HH:MM:SS,HH:MM:SS):", parent=root)
        if user_time:
            times = user_time.split(',')
            if len(times) == 1:
            
                # Single time check
                convert_timedelta = parse_time_string(times[0])
                
                # Update package #9 address if current time is 10:20 AM or later
                package_9 = package_hash_table.lookup(9)
                if package_9 and convert_timedelta >= datetime.timedelta(hours=10, minutes=20):
                    package_9.update_address("410 S State St", "Salt Lake City", "UT", "84111")
                
                second_input = simpledialog.askstring("Input", "To view the status of an individual parcel please type '1'. For the status of all parcels please type '0':", parent=root)
                if second_input == "1":
                    solo_input = simpledialog.askinteger("Input", "Enter the numeric package ID:", parent=root)
                    if solo_input:
                        display_status(package_hash_table, convert_timedelta, truck1, truck2, truck3, solo_input)
                elif second_input == "0":
                    display_status(package_hash_table, convert_timedelta, truck1, truck2, truck3)
                else:
                    messagebox.showerror("Error", "Entry invalid. Quitting program.")
            
            elif len(times) == 2:
                # Check status between times
                try:
                    start_time = parse_time_string(times[0])
                    end_time = parse_time_string(times[1])
                    
                    if start_time <= end_time:
                        current_time = start_time
                        while current_time <= end_time:
                            # Update package #9 address if current time is 10:20 AM or later
                            package_9 = package_hash_table.lookup(9)
                            if package_9 and current_time >= datetime.timedelta(hours=10, minutes=20):
                                package_9.update_address("410 S State St", "Salt Lake City", "UT", "84111")
                            
                            display_status(package_hash_table, current_time, truck1, truck2, truck3)
                            current_time += datetime.timedelta(minutes=10)  # Adjust the increment as needed
                    else:
                        messagebox.showerror("Error", "End time must be after start time.")
                except ValueError:
                    messagebox.showerror("Error", "Invalid time format entered.")
            else:
                messagebox.showerror("Error", "Invalid input. Please enter a single time or two times separated by a comma.")

    # Add buttons for checking status and checking status between times
    start_button = tk.Button(root, text="Check Status", command=check_status, font=("Helvetica", 12), bg='darkblue', fg='white')
    start_button.pack(pady=10)

    root.mainloop()
def main():
    global truck1, truck2, truck3  # Ensure trucks are accessible globally for mileage display

    # Parsing command-line arguments
    parser = argparse.ArgumentParser(description='WGUPS Routing Program')
    parser.add_argument('--no-interface', action='store_true', help='Run the program without starting the interface')
    args = parser.parse_args()

    # Creating truck objects with initial data
    truck1 = DeliveryTruck(16, 18, None, [1, 13, 14, 15, 16, 20, 29, 30, 31, 34, 37, 40], 0.0, "4001 South 700 East", datetime.timedelta(hours=8))
    truck2 = DeliveryTruck(16, 18, None, [3, 6, 12, 17, 18, 19, 21, 22, 23, 24, 26, 27, 35, 36, 38, 39], 0.0, "4001 South 700 East", datetime.timedelta(hours=10, minutes=20))
    truck3 = DeliveryTruck(16, 18, None, [2, 4, 5, 7, 8, 9, 10, 11, 25, 28, 32, 33], 0.0, "4001 South 700 East", datetime.timedelta(hours=9, minutes=5))

    # Create the hash table for packages and load package data into it
    package_hash_table = CustomHashMap()
    load_package_data("CSV/Package_File.csv", package_hash_table)

    # Deliver packages for each truck using the Nearest Neighbor Algorithm
    delivered_packages_global[1] = delivering_packages(truck1, package_hash_table, 1)
    delivered_packages_global[2] = delivering_packages(truck2, package_hash_table, 2)
    truck3.depart_time = min(truck1.time, truck2.time)
    delivered_packages_global[3] = delivering_packages(truck3, package_hash_table, 3)

    # Print the total mileage traveled for all trucks
    print("Western Governors University Parcel Service (WGUPS)")
    print("The mileage for the route is:", truck1.mileage + truck2.mileage + truck3.mileage)

    # Function to print package statuses in the terminal
    def print_package_status(package_hash_table, convert_timedelta):
        def get_truck_number(package_id):
            if package_id in truck1.packages:
                return 1
            elif package_id in truck2.packages:
                return 2
            elif package_id in truck3.packages:
                return 3
            return "Unknown"

        for package_id in range(1, 41):
            parcel = package_hash_table.lookup(package_id)
            parcel.update_status(convert_timedelta)
            if parcel.ID == 9 and convert_timedelta < datetime.timedelta(hours=10, minutes=20):
                parcel.update_address("300 State St", "Salt Lake City", "UT", "84103")
            truck_number = get_truck_number(parcel.ID)
            status = f"Truck {truck_number}: {str(parcel)}"
            if parcel.delivery_time and parcel.delivery_time <= convert_timedelta:
                status = f"DELIVERED: {status}"
                print(status)
            elif parcel.departure_time and parcel.departure_time <= convert_timedelta:
                status = f"EN ROUTE: {status}"
                print(status)
            else:
                print(status)

    # Print the status of all packages if the --no-interface flag is set
    if args.no_interface:
        # Prompt user for the time to check the status of packages
        user_time = input("Enter time to check the status of a Parcel(s). Use the following format, HH:MM:SS or HH:MMAM/PM: ")
        if user_time:
            convert_timedelta = parse_time_string(user_time)
            print_package_status(package_hash_table, convert_timedelta)
    else:
        # Start the Tkinter interface for user interaction if the flag is not set
        start_interface(package_hash_table, truck1, truck2, truck3)

if __name__ == "__main__":
    main()


"""
Summary of Major Code Blocks with Comments:

1. Imports and Initial Setup:
   - Import necessary libraries and modules.
   - Define helper functions to read CSV files.

2. Reading CSV Files:
   - Read distance, address, and package CSV files into corresponding lists.

3. Loading Package Data:
   - Define and use the `load_package_data` function to load package information into a hash table.

4. Distance Calculation:
   - Define the `distance_in_between` function to calculate the distance between two addresses.

5. Address Extraction:
   - Define the `extract_address` function to get the address ID from an address string.

6. Package Delivery Algorithm:
   - Implement the `delivering_packages` function using the Nearest Neighbor Algorithm to deliver packages.

7. Time Parsing:
   - Define the `parse_time_string` function to handle time string parsing and conversion to `timedelta`.

8. Displaying Package Status:
   - Define the `display_status` function to create a new window displaying the status of packages.

9. User Interface for Checking Status:
   - Implement the `start_interface` function to create the main Tkinter interface.
   - python main.py --no-interface to run file in terminal only

10. Main Function:
    - Create truck objects and execute the package delivery process.
    - Start the Tkinter interface if the flag is not set.
"""

