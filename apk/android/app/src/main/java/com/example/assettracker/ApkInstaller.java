package com.example.assettracker;

import android.content.Intent;
import android.net.Uri;
import androidx.core.content.FileProvider;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.io.File;

/**
 * Satu-satunya tugas plugin ini: membuka installer APK bawaan Android
 * untuk file yang sudah selesai di-download ke penyimpanan lokal app
 * (lihat www/index.html - downloadAndInstall()). Bukan plugin umum,
 * sengaja dibuat sendiri karena Capacitor tidak punya plugin resmi
 * untuk langkah "install APK ini" (beda dengan download file, yang
 * sudah ditangani @capacitor/filesystem).
 */
@CapacitorPlugin(name = "ApkInstaller")
public class ApkInstaller extends Plugin {

    @PluginMethod
    public void install(PluginCall call) {

        String path = call.getString("path");

        if (path == null || path.isEmpty()) {
            call.reject("path wajib diisi");
            return;
        }

        File file = new File(path);

        if (!file.exists()) {
            call.reject("File tidak ditemukan: " + path);
            return;
        }

        Uri uri = FileProvider.getUriForFile(
            getContext(),
            getContext().getPackageName() + ".fileprovider",
            file
        );

        Intent intent = new Intent(Intent.ACTION_VIEW);
        intent.setDataAndType(uri, "application/vnd.android.package-archive");
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

        getContext().startActivity(intent);

        call.resolve(new JSObject());
    }
}
