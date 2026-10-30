# APK (Capacitor WebView wrapper)

APK ini **bukan** aplikasi native terpisah - isinya cuma 1 WebView yang
membuka alamat web Internal Asset Tracker. Semua fitur, login, dan
pembatasan akses per role (termasuk rencana pembatasan khusus role
OB/Receptionist/Mekanik) tetap ditangani sepenuhnya oleh aplikasi web
itu sendiri, sama seperti diakses lewat browser biasa.

## Alamat server - otomatis LAN dulu, fallback ke internet

APK ini **tidak** pakai satu alamat server tetap (`server.url`) lagi.
Sebagai gantinya, `www/index.html` adalah halaman loader kecil yang:

1. Coba akses LAN kantor langsung (`http://<IP-LAN-SERVER>:8000/`),
   timeout 2 detik.
2. Kalau berhasil (lagi di WiFi kantor) → langsung dipakai, cepat &
   tidak lewat internet sama sekali.
3. Kalau gagal/timeout (lagi di luar kantor, pakai data seluler/WiFi
   lain) → otomatis pindah ke alamat publik lewat Tailscale Funnel:
   `https://<device>.<tailnet>.ts.net:8443/` (device Tailscale
   server, port `8443` karena `443` sudah dipakai Funnel
   untuk aplikasi lain/legal-contract di device yang sama).

Supaya kedua alamat ini boleh dibuka DI DALAM WebView aplikasi (bukan
malah lempar ke Chrome eksternal), keduanya didaftarkan di
`capacitor.config.json` → `server.allowNavigation`. Dan supaya alamat
LAN (HTTP biasa, bukan HTTPS) boleh diakses, ada izin cleartext khusus
untuk IP itu saja di
`android/app/src/main/res/xml/network_security_config.xml`.

**Kalau Funnel di server produksi mati/berhenti** (misal device
Tailscale restart), aktifkan lagi di server itu:

```powershell
tailscale funnel --bg --https=8443 8000
```

(butuh firewall rule TCP 8443 sekali saja - sudah dibuat, tidak perlu
diulang kecuali firewall-nya di-reset).

## Ganti alamat server

Edit kedua alamat (LAN & publik) langsung di `www/index.html`
(`LAN_URL` dan `PUBLIC_URL`), lalu jalankan ulang:

```bash
npx cap sync android
```

Untuk testing di **Android Emulator** ke dev server lokal (bukan
produksi): ganti sementara `LAN_URL`/`PUBLIC_URL` jadi
`http://10.0.2.2:8001/` (alamat khusus emulator menjangkau
`localhost:8001` di PC dev - tidak jalan untuk HP fisik), dan tambahkan
IP/hostname itu juga ke `network_security_config.xml` kalau perlu.

## Build ulang APK

Build debug butuh **JDK 21** (sudah terpasang di PC ini terpisah dari
JDK 17 yang dipakai untuk kebutuhan lain):

```bash
cd android
JAVA_HOME="C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot" ./gradlew.bat assembleDebug
```

Hasilnya ada di `android/app/build/outputs/apk/debug/app-debug.apk`.

APK debug ini belum ditandatangani untuk rilis (`assembleRelease`) -
cukup untuk uji coba internal, instal manual (install dari file,
bukan Play Store).

Simpan salinan tiap versi yang sudah dirilis ke
`releases/AIT_HRGA_v<N>.apk` (folder ini TIDAK masuk git - `*.apk`
di-gitignore - tapi tetap disimpan lokal di PC ini sebagai
arsip/track record, jangan dihapus).

## Update otomatis (cek versi lewat GitHub Releases)

Setiap kali APK dibuka, `www/index.html` cek rilis terbaru langsung ke
GitHub Releases (repo publik, gratis, tanpa server/database tambahan):
`https://api.github.com/repos/r0corp/Internal-Asset-Tracker/releases/latest`.
Kalau versi di sana lebih baru dari yang terpasang, muncul layar
"Update tersedia" dengan tombol download file .apk-nya - kalau tidak,
APK lanjut seperti biasa tanpa gangguan.

**Alur rilis versi baru** (setiap kali ada perubahan yang perlu masuk
ke APK, bukan cuma perubahan web biasa yang otomatis ke-update sendiri):

1. Naikkan `versionCode`/`versionName` di `android/app/build.gradle`,
   DAN `CURRENT_VERSION_CODE` di `www/index.html` (harus sama persis).
2. Build APK (lihat langkah di atas).
3. Buat **GitHub Release** baru, dengan:
   - Tag **harus** persis `v<versionCode>` (mis. `v3` untuk versionCode 3) -
     APK baca angka dari tag ini buat dibandingkan ke versi terpasang.
   - Lampirkan file `.apk` hasil build sebagai release asset.
   - Isi deskripsi rilis (opsional) - ini yang muncul sebagai catatan
     update di layar "Update tersedia".
4. Push commit source code seperti biasa - tidak ada endpoint/database
   khusus di server yang perlu disentuh.

Kalau `gh` (GitHub CLI) sudah terpasang & login, langkah 3 bisa lewat:

```bash
gh release create v3 path/to/app-debug.apk --title "v3" --notes "Catatan perubahan di versi ini"
```
