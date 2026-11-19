package com.example.agribandhu.network;

import com.example.agribandhu.BuildConfig;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class ApiClient {

    private static Retrofit retrofit = null;
    private static OkHttpClient okHttpClient = null;

    // Backend URL defined centrally in build.gradle.kts
    private static final String BASE_URL = BuildConfig.BACKEND_BASE_URL;

    public static synchronized OkHttpClient getOkHttpClient() {
        if (okHttpClient == null) {
            okHttpClient = new OkHttpClient.Builder()
                    .connectTimeout(15, TimeUnit.SECONDS)
                    .readTimeout(20, TimeUnit.SECONDS)
                    .writeTimeout(20, TimeUnit.SECONDS)
                    .addInterceptor(new Interceptor() {
                        @Override
                        public Response intercept(Chain chain) throws IOException {
                            Request originalRequest = chain.request();
                            Response response;
                            try {
                                response = chain.proceed(originalRequest);
                            } catch (IOException originalException) {
                                // If initial call failed, retry once after 500ms
                                try {
                                    Thread.sleep(500);
                                    return chain.proceed(originalRequest);
                                } catch (Exception ignored) {
                                    throw originalException;
                                }
                            }

                            // If proxy/gateway returns temporary 502, 503, or 504, auto-retry once
                            if (response.code() == 502 || response.code() == 503 || response.code() == 504) {
                                response.close();
                                try {
                                    Thread.sleep(500);
                                } catch (InterruptedException ignored) {}
                                return chain.proceed(originalRequest);
                            }

                            return response;
                        }
                    })
                    .build();
        }
        return okHttpClient;
    }

    public static synchronized Retrofit getClient() {
        if (retrofit == null) {
            retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .client(getOkHttpClient())
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit;
    }

    /**
     * Returns the base URL for use in components that make direct OkHttp calls.
     */
    public static String getBaseUrl() {
        return BASE_URL;
    }
}
