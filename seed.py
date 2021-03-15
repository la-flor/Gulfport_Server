from app import db
from models import User, Event

# Must first `createdb gulfport_votes` in CLI to create our psql database

db.drop_all()
db.create_all()

db.session.add(User(email="testuser@email.com", password="$2b$12$k7bl2ufz91/HfRq86T6mQ.7jStvvzM0XwrEiv/eaddo06.YPQvuTe"))
# creates sample email = "testuser@email.com" and password = "passwords"
db.session.commit()

print('User table created with sample user.')

db.session.add(Event(
            title="ComeUnity Celebration",
            description="Shake off the election stress and have some fun with your neighbors and friends",
            scheduled_time="2020-11-03 14:00:00"))
db.session.add(Event(
            title="Drive-in Movie Night",
            description="Join us in watching \"All In: The Fight for Democracy\", a riveting examination of voter suppression in the United States",
            scheduled_time="2020-10-24 15:00:00"))
db.session.add(Event(
            title="National Voter Registration",
            description="If you have not registered yet, today is the day!",
            scheduled_time="2020-10-21 23:00:00"))
db.session.add(Event(
            title="Porch Party",
            description="A free, family-friendly outdoor party celebration Volunteers and Voting",
            scheduled_time="2020-10-09 16:00:00"))
db.session.add(Event(
            title="Florida's Registration Day!",
            description="Florida's official registration day. Don't delay! Register today!",
            scheduled_time="2020-10-05 23:00:00"))

db.session.commit()

print('Events database table created and populated with events.')