from pymongo import MongoClient
import time, requests, smtplib, math, json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


with open('config.json') as config_file:
    config = json.load(config_file)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
gmail_user = config.get('GMAIL_USER')
gmail_password = config.get('GMAIL_PASSWORD')

server.login(gmail_user, gmail_password)

client = MongoClient('localhost', 27017)

def main():
    while True:
        check_appointments()
        time.sleep(60) #every minute


def check_appointments():
    states = ['OH']
    states_dict = {}
    for state in states:
        r = requests.get(f'https://www.vaccinespotter.org/api/v0/states/{state}.json')
        my_dict = r.json()
        states_dict.update({state:my_dict})
    active_users = client.vaccineNotifier.users.find({ "active": True })
    for user in active_users:
        accepted_appointments = []
        in_range_locations = 0
        for appointment in states_dict[ user["state"] ]["features"]:
            apt_coords = appointment["geometry"]["coordinates"]
            try:
                dist = round(coords_distance(apt_coords, user["coords"]), 2)
                if (dist <= user["distance"]):
                    in_range_locations += 1
                    if (appointment["properties"]["appointments_available"]):
                        props = appointment["properties"]
                        full_address = f"{props['address']}, {props['city']}, {state}"
                        apt_dict = { "address":full_address, "distance":dist, "url":props["url"], "name":props["name"] }
                        accepted_appointments.append(apt_dict)
            except Exception as e:
                pass
        accepted_appointments = sorted(accepted_appointments, key=lambda x: x["distance"])
        send_email(user["email"], accepted_appointments, in_range_locations)


def send_email(recipient, appointments, in_range_locations):
    mail_content = f"{len(appointments)}/{in_range_locations} locations available. \nAppointments found at: \n"
    for appointment in appointments:
        mail_content += appointment["name"] + ", " + \
                    appointment["address"] + ". " + str(appointment["distance"]) + " miles away." + \
                    " Click the link to schedule: " + appointment["url"] + "\n"
    message = MIMEMultipart()
    message['From'] = gmail_user
    message['To'] = recipient
    message['Subject'] = "Vaccine appointments available"
    message.attach(MIMEText(mail_content, 'plain'))
    text = message.as_string()
    server.sendmail(gmail_user, recipient, text)
    print("Email sent")


def coords_distance(pt1, pt2):
    lat1, lon1 = pt1
    lat2, lon2 = pt2
    radius = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    d = d * 0.6213712 #to miles
    return d


if __name__ == "__main__":
    main()
