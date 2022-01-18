from pausedefi_api.models import *


users = []


for x in range(1, 11):
    user = User(
        email=f"email{x}@mail.com",
        password='0000'
    )
    users.append(user)
    db.session.add(user)
    db.session.commit()

room1 = Room(
    name='room1'
)
room1.creator = users[1]
room1.creator_id = users[1].id
room1.users.append(users[1])
room1.users.append(users[2])
room1.users.append(users[3])
db.session.add(room1)
db.session.commit()

for y in range(1, 4):
    defi = Challenge(
        title=f"titre #{y}",
        content=f"content {y}"
    )
    defi.room_id = room1.id
    defi.room = room1
    defi.creator_id = users[1].id
    defi.creator = users[1]
    defi.challengers.append(users[y])
    db.session.add(defi)
    db.session.commit()




