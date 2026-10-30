package com.example.assettracker;

import android.app.DownloadManager;
import android.content.Context;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.webkit.CookieManager;
import android.webkit.URLUtil;
import android.webkit.WebView;
import android.widget.Toast;

import androidx.activity.OnBackPressedCallback;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(ApkInstaller.class);
        super.onCreate(savedInstanceState);

        // Capacitor tidak otomatis menangani tombol/gesture back untuk
        // mundur ke halaman sebelumnya di dalam WebView - tanpa ini,
        // back selalu langsung keluar dari aplikasi (dianggap activity
        // biasa yang di-finish). Pakai OnBackPressedCallback (API
        // modern, kompatibel dengan gesture predictive-back Android
        // 13+), bukan onBackPressed() lama yang bisa dilewati begitu
        // saja oleh gesture swipe di beberapa versi Android.
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {

                WebView webView = getBridge() != null ? getBridge().getWebView() : null;

                if (webView != null && webView.canGoBack()) {
                    webView.goBack();
                } else {
                    setEnabled(false);
                    getOnBackPressedDispatcher().onBackPressed();
                    setEnabled(true);
                }
            }
        });

        // WebView bawaan TIDAK menangani respons "Content-Disposition:
        // attachment" (mis. tombol Export ke Excel) sama sekali - tanpa
        // DownloadListener, tap link seperti itu tidak terjadi apa-apa.
        // Pakai DownloadManager bawaan Android: butuh cookie sesi login
        // disertakan manual (DownloadManager tidak berbagi cookie jar
        // WebView), lalu file masuk folder Downloads dan ada notifikasi
        // sistem untuk membukanya dengan app lain (Excel/WPS/Sheets).
        WebView webView = getBridge() != null ? getBridge().getWebView() : null;

        if (webView != null) {
            webView.setDownloadListener((url, userAgent, contentDisposition, mimetype, contentLength) -> {
                try {
                    String cookies = CookieManager.getInstance().getCookie(url);
                    String filename = URLUtil.guessFileName(url, contentDisposition, mimetype);

                    DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
                    request.addRequestHeader("Cookie", cookies);
                    request.addRequestHeader("User-Agent", userAgent);
                    request.setMimeType(mimetype);
                    request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                    request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, filename);

                    DownloadManager downloadManager = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                    downloadManager.enqueue(request);

                    Toast.makeText(this, "Mengunduh " + filename + "...", Toast.LENGTH_LONG).show();
                } catch (Exception e) {
                    Toast.makeText(this, "Gagal mengunduh file: " + e.getMessage(), Toast.LENGTH_LONG).show();
                }
            });
        }
    }
}
