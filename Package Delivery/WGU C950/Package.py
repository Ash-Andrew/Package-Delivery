class Parcel:
    def __init__(self, ID, address, city, state, zipcode, deadline, weight, status):
        self.ID = ID
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline
        self.weight = weight
        self.status = status
        self.delivery_time = None
        self.departure_time = None

    def update_status(self, current_time):
        if self.delivery_time and self.delivery_time <= current_time:
            self.status = 'Delivered'
        elif self.departure_time and self.departure_time <= current_time:
            self.status = 'En Route'
        else:
            self.status = 'At Hub'

    def update_address(self, address, city, state, zipcode):
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode

    def __str__(self):
        return f"ID: {self.ID}, Address: {self.address}, City: {self.city}, State: {self.state}, Zip: {self.zipcode}, Deadline: {self.deadline}, Weight: {self.weight} Kilos, Status: {self.status}, Departure: {self.departure_time}, Delivery: {self.delivery_time}"
