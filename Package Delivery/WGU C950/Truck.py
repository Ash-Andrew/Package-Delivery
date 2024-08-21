# Truck Class 
class DeliveryTruck:
    def __init__(self, capacity, speed, time, packages, mileage, address, depart_time):
        self.capacity = capacity
        self.speed = speed
        self.time = depart_time  # Initialize time to depart_time
        self.packages = packages
        self.mileage = mileage
        self.address = address
        self.depart_time = depart_time
