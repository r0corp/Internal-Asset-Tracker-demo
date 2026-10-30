"""
Restrukturisasi menu sidebar (sekali jalan, aman diulang):

1. "Movement Report" dipindah dari menu utama berdiri sendiri jadi
   anak dari "Asset" - url "Asset" ("/") TETAP dipertahankan, karena
   app/__init__.py inject_nav_menu() mendeteksi menu ini lewat url=="/"
   dan memecahnya jadi grup per-kategori (lihat komentar di sana).
   "Movement Report" ditambahkan oleh kode yang sama sebagai link lepas
   setelah semua grup kategori.
2. "Company" dipindah jadi submenu di bawah "Master Data".
3. Separator ditambahkan sebelum grup menu admin (Master Data, User
   Management, Menu Management).
"""

from app import create_app, db
from app.models import MenuItem


app = create_app()

with app.app_context():

    asset = MenuItem.query.filter_by(label="Asset", parent_id=None).first()
    movement_report = MenuItem.query.filter_by(label="Movement Report", parent_id=None).first()
    master_data = MenuItem.query.filter_by(label="Master Data", parent_id=None).first()
    company = MenuItem.query.filter_by(label="Company", parent_id=None).first()

    if not asset or not master_data:

        print("Menu dasar (Asset/Master Data) tidak ditemukan, dibatalkan.")

    else:

        changed = False

        if asset.url != "/":
            asset.url = "/"
            changed = True

        if movement_report and movement_report.parent_id != asset.id:
            movement_report.parent_id = asset.id
            movement_report.order = 10
            changed = True

        if company and company.parent_id != master_data.id:
            company.parent_id = master_data.id
            company.order = 50
            changed = True

        divider = MenuItem.query.filter_by(is_divider=True, parent_id=None).first()

        if not divider:

            divider = MenuItem(
                label="Separator",
                is_divider=True,
                order=45,
                parent_id=None,
            )

            db.session.add(divider)
            changed = True

        if changed:
            db.session.commit()
            print("Struktur menu berhasil diperbarui.")
        else:
            print("Struktur menu sudah sesuai, tidak ada perubahan.")
