from pausedefi_api.models import *

for x in range(1, 11):
    user = User(
        email=f"email{x}@mail.com",
        password='0000'
    )
    db.session.add(user)
    db.session.commit()