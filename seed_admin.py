import secrets

from app import create_app, db
from app.models import User, ROLE_ADMINISTRATOR


app = create_app()

with app.app_context():

    if User.query.filter_by(username="admin").first():

        print("User 'admin' sudah ada, dilewati.")

    else:

        user = User(
            username="admin",
            full_name="Administrator",
            role=ROLE_ADMINISTRATOR,
        )

        # Password acak, bukan nilai tetap yang tertulis di repo publik.
        password = secrets.token_urlsafe(9)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f"User administrator awal dibuat: admin / {password}")
        print("Segera login dan ganti password ini.")
