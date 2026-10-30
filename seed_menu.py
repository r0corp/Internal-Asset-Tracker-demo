from app import create_app, db
from app.models import MenuItem, ROLE_ADMINISTRATOR


app = create_app()

with app.app_context():

    if MenuItem.query.first():

        print("Menu sudah ada data, dilewati.")

    else:

        dashboard = MenuItem(
            label="Dashboard",
            icon="bi-speedometer2",
            url="/dashboard",
            order=10,
        )

        # url "/" SENGAJA dipertahankan (bukan None) - app/__init__.py
        # inject_nav_menu() mendeteksi menu "Asset" lewat url=="/" ini
        # dan memecahnya jadi grup per-kategori (PC/Laptop, Ponsel, dst,
        # masing2 dengan Asset List/Add Asset/Stock Opname/ATK Pickup
        # sendiri) - bukan dirender dari relasi children seperti Master
        # Data. Child di bawah ini ("Movement Report") TETAP ditambahkan
        # manual sebagai link lepas setelah semua grup kategori lewat
        # kode yang sama, jangan diubah ke url=None lagi.
        asset = MenuItem(
            label="Asset",
            icon="bi-box-seam",
            url="/",
            order=20,
        )

        master_data = MenuItem(
            label="Master Data",
            icon="bi-database",
            url=None,
            order=50,
        )

        divider = MenuItem(
            label="Separator",
            is_divider=True,
            order=45,
        )

        manajemen_user = MenuItem(
            label="User Management",
            icon="bi-people",
            url="/users",
            order=70,
            roles=ROLE_ADMINISTRATOR,
        )

        manajemen_menu = MenuItem(
            label="Menu Management",
            icon="bi-list-ul",
            url="/menus",
            order=80,
            roles=ROLE_ADMINISTRATOR,
        )

        db.session.add_all([
            dashboard,
            asset,
            divider,
            master_data,
            manajemen_user,
            manajemen_menu,
        ])

        db.session.flush()

        children = [
            MenuItem(
                label="Movement Report",
                url="/assets/movements/report",
                order=10,
                parent_id=asset.id,
            ),
            MenuItem(
                label="Category",
                url="/categories",
                order=10,
                parent_id=master_data.id,
            ),
            MenuItem(
                label="Location",
                url="/locations",
                order=20,
                parent_id=master_data.id,
            ),
            MenuItem(
                label="Department",
                url="/departments",
                order=30,
                parent_id=master_data.id,
            ),
            MenuItem(
                label="Vendor",
                url="/vendors",
                order=40,
                parent_id=master_data.id,
            ),
            MenuItem(
                label="Company",
                url="/company",
                order=50,
                parent_id=master_data.id,
            ),
        ]

        db.session.add_all(children)
        db.session.commit()

        print("Menu default berhasil dibuat.")
