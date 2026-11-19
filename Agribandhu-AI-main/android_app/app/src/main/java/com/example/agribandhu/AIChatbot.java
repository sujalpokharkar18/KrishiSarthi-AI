package com.example.agribandhu;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.net.URLEncoder;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class AIChatbot extends AppCompatActivity {

    private static final String TAG = "AIChatbot";

    private EditText etArea, etVegetable;
    private Button btnFetchWeather, btnGenerateAI, btnStartProgress;
    private TextView tvAITimetable;
    private LinearLayout weatherSection, aiResultSection, weatherContainer;

    private DatabaseReference dbRef;
    private JSONArray lastGeneratedTimetable;
    private String userEmail;

    private String cityName, vegetableName;
    private String weatherSummary = "";
    private String startDate = "";
    private double latitude = 0.0;
    private double longitude = 0.0;

    private final OkHttpClient httpClient = com.example.agribandhu.network.ApiClient.getOkHttpClient();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_aichatbot);

        etArea = findViewById(R.id.etArea);
        etVegetable = findViewById(R.id.etVegetable);
        btnFetchWeather = findViewById(R.id.btnFetchWeather);
        btnGenerateAI = findViewById(R.id.btnGenerateAI);
        tvAITimetable = findViewById(R.id.tvAIResponse);
        weatherSection = findViewById(R.id.weatherSection);
        aiResultSection = findViewById(R.id.aiResultSection);
        weatherContainer = findViewById(R.id.weatherContainer);
        btnStartProgress = findViewById(R.id.btnStartProgress);
        btnStartProgress.setVisibility(View.GONE);

        Intent intent = getIntent();
        userEmail = intent.getStringExtra("email");

        if (userEmail == null || userEmail.isEmpty()) {
            if (com.google.firebase.auth.FirebaseAuth.getInstance().getCurrentUser() != null) {
                userEmail = com.google.firebase.auth.FirebaseAuth.getInstance().getCurrentUser().getEmail();
            }
        }

        if (userEmail == null || userEmail.isEmpty()) {
            android.content.SharedPreferences sp = getSharedPreferences("AgriBandhuSession", MODE_PRIVATE);
            userEmail = sp.getString("saved_email", null);
        }

        if (userEmail == null || userEmail.isEmpty()) {
            userEmail = "farmer@krishisarthi.com";
        }

        String safeEmail = userEmail.replace(".", "_");
        dbRef = FirebaseDatabase.getInstance()
                .getReference("users")
                .child(safeEmail)
                .child("crops");

        btnStartProgress.setOnClickListener(v -> saveCropProgress());

        btnFetchWeather.setOnClickListener(v -> {
            cityName = etArea.getText().toString().trim();
            vegetableName = etVegetable.getText().toString().trim();

            if (cityName.isEmpty() || vegetableName.isEmpty()) {
                Toast.makeText(this, "Please enter both area and crop name", Toast.LENGTH_SHORT).show();
                return;
            }

            btnFetchWeather.setEnabled(false);
            Toast.makeText(this, "Locating coordinates...", Toast.LENGTH_SHORT).show();
            fetchCoordinates(cityName);
        });

        btnGenerateAI.setOnClickListener(v -> {
            if (weatherSummary.isEmpty()) {
                Toast.makeText(this, "Please fetch weather first", Toast.LENGTH_SHORT).show();
                return;
            }
            if (startDate.isEmpty()) {
                Toast.makeText(this, "Start date not found. Fetch weather again.", Toast.LENGTH_SHORT).show();
                return;
            }

            btnGenerateAI.setEnabled(false);
            generateAITimetable();
        });
    }

    private void saveCropProgress() {
        try {
            if (lastGeneratedTimetable == null) {
                Toast.makeText(this, "No timetable to save", Toast.LENGTH_SHORT).show();
                return;
            }

            String cropKey = vegetableName.toLowerCase().replace(" ", "_");
            DatabaseReference cropRef = dbRef.child(cropKey);

            cropRef.child("cropName").setValue(vegetableName);
            cropRef.child("startDate").setValue(startDate);
            cropRef.child("city").setValue(cityName);
            cropRef.child("latitude").setValue(latitude);
            cropRef.child("longitude").setValue(longitude);
            cropRef.child("createdAt").setValue(System.currentTimeMillis());

            for (int i = 0; i < lastGeneratedTimetable.length(); i++) {
                JSONObject dayObj = lastGeneratedTimetable.getJSONObject(i);
                String dayKey = "day" + dayObj.getInt("day");
                String task = dayObj.getString("task");
                cropRef.child("timetable").child(dayKey).setValue(task);
            }

            Toast.makeText(this, "✅ Crop timetable saved to profile!", Toast.LENGTH_LONG).show();

        } catch (Exception e) {
            e.printStackTrace();
            Toast.makeText(this, "Failed to save data: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    // ──────────────── Modern Asynchronous Networking ────────────────

    private void fetchCoordinates(String city) {
        try {
            String cityEncoded = URLEncoder.encode(city, "UTF-8");
            String url = "https://us1.locationiq.com/v1/search.php?key=" + BuildConfig.LOCATIONIQ_API_KEY
                    + "&q=" + cityEncoded + "&format=json&limit=1";

            Request request = new Request.Builder().url(url).build();
            httpClient.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(@NonNull Call call, @NonNull IOException e) {
                    runOnUiThread(() -> {
                        btnFetchWeather.setEnabled(true);
                        Toast.makeText(AIChatbot.this, "Network error finding city: " + e.getMessage(), Toast.LENGTH_LONG).show();
                    });
                }

                @Override
                public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                    if (!response.isSuccessful() || response.body() == null) {
                        runOnUiThread(() -> {
                            btnFetchWeather.setEnabled(true);
                            Toast.makeText(AIChatbot.this, "Could not find coordinates for: " + city, Toast.LENGTH_LONG).show();
                        });
                        return;
                    }

                    try {
                        String body = response.body().string();
                        JSONArray geoArray = new JSONArray(body);
                        if (geoArray.length() == 0) {
                            runOnUiThread(() -> {
                                btnFetchWeather.setEnabled(true);
                                Toast.makeText(AIChatbot.this, "Location not found. Check spelling.", Toast.LENGTH_SHORT).show();
                            });
                            return;
                        }

                        JSONObject location = geoArray.getJSONObject(0);
                        latitude = Double.parseDouble(location.getString("lat"));
                        longitude = Double.parseDouble(location.getString("lon"));

                        runOnUiThread(() -> {
                            Toast.makeText(AIChatbot.this, "Location confirmed! Fetching 7-day weather...", Toast.LENGTH_SHORT).show();
                            fetchWeather(latitude, longitude);
                        });

                    } catch (Exception e) {
                        runOnUiThread(() -> {
                            btnFetchWeather.setEnabled(true);
                            Toast.makeText(AIChatbot.this, "Parse error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                        });
                    }
                }
            });

        } catch (Exception e) {
            btnFetchWeather.setEnabled(true);
            Toast.makeText(this, "Encoding error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private void fetchWeather(double lat, double lon) {
        String url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
                + lat + "," + lon
                + "/next7days?unitGroup=metric&key=" + BuildConfig.WEATHER_API_KEY + "&contentType=json";

        Request request = new Request.Builder().url(url).build();
        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                runOnUiThread(() -> {
                    btnFetchWeather.setEnabled(true);
                    Toast.makeText(AIChatbot.this, "Weather fetch failed: " + e.getMessage(), Toast.LENGTH_LONG).show();
                });
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                runOnUiThread(() -> btnFetchWeather.setEnabled(true));

                if (!response.isSuccessful() || response.body() == null) {
                    runOnUiThread(() ->
                            Toast.makeText(AIChatbot.this, "Weather API error: " + response.code(), Toast.LENGTH_SHORT).show()
                    );
                    return;
                }

                try {
                    String result = response.body().string();
                    JSONObject jsonObject = new JSONObject(result);
                    JSONArray daysArray = jsonObject.getJSONArray("days");

                    runOnUiThread(() -> {
                        weatherContainer.removeAllViews();
                        JSONArray weatherList = new JSONArray();
                        startDate = "";

                        for (int i = 0; i < daysArray.length(); i++) {
                            try {
                                JSONObject dayObj = daysArray.getJSONObject(i);
                                String date = dayObj.optString("datetime", "");
                                String condition = dayObj.optString("conditions", "Clear");
                                double maxTemp = dayObj.optDouble("tempmax", 0);
                                double minTemp = dayObj.optDouble("tempmin", 0);
                                double humidity = dayObj.optDouble("humidity", 0);
                                double rainMM = dayObj.optDouble("precip", 0);

                                if (i == 0) startDate = date;

                                JSONObject w = new JSONObject();
                                w.put("condition", condition);
                                w.put("rain_mm", rainMM);
                                w.put("temp_c", maxTemp);
                                weatherList.put(w);

                                TextView card = new TextView(AIChatbot.this);
                                card.setText("📅 " + date + "\n" + condition + "\n🌡 "
                                        + minTemp + "°C - " + maxTemp + "°C\n💧 "
                                        + humidity + "%");
                                card.setPadding(30, 30, 30, 30);
                                card.setBackgroundResource(R.drawable.editext);
                                card.setTextColor(getResources().getColor(android.R.color.black));
                                card.setTextSize(15f);

                                LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                                        LinearLayout.LayoutParams.WRAP_CONTENT,
                                        LinearLayout.LayoutParams.WRAP_CONTENT
                                );
                                params.setMargins(20, 10, 20, 10);
                                card.setLayoutParams(params);
                                card.setGravity(Gravity.CENTER);

                                weatherContainer.addView(card);
                            } catch (Exception ex) {
                                ex.printStackTrace();
                            }
                        }

                        weatherSummary = weatherList.toString();
                        weatherSection.setVisibility(View.VISIBLE);
                        Toast.makeText(AIChatbot.this, "Weather updated (Start: " + startDate + ")", Toast.LENGTH_SHORT).show();
                    });

                } catch (Exception e) {
                    runOnUiThread(() ->
                            Toast.makeText(AIChatbot.this, "Weather parse error: " + e.getMessage(), Toast.LENGTH_SHORT).show()
                    );
                }
            }
        });
    }

    private void generateAITimetable() {
        tvAITimetable.setText("🧠 Generating weather-aware timetable from KrishiSarthi AI...");
        aiResultSection.setVisibility(View.VISIBLE);

        try {
            JSONObject json = new JSONObject();
            json.put("crop", vegetableName);
            json.put("start_date", startDate);

            JSONArray fullWeather = new JSONArray(weatherSummary);
            JSONArray trimmedWeather = new JSONArray();
            for (int i = 0; i < Math.min(fullWeather.length(), 7); i++) {
                trimmedWeather.put(fullWeather.getJSONObject(i));
            }
            json.put("weather", trimmedWeather);

            String backendUrl = com.example.agribandhu.network.ApiClient.getBaseUrl() + "ai_timetable";

            RequestBody body = RequestBody.create(
                    json.toString(),
                    MediaType.parse("application/json; charset=utf-8")
            );

            Request request = new Request.Builder()
                    .url(backendUrl)
                    .post(body)
                    .build();

            httpClient.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(@NonNull Call call, @NonNull IOException e) {
                    runOnUiThread(() -> {
                        btnGenerateAI.setEnabled(true);
                        tvAITimetable.setText("⚠️ Cannot reach KrishiSarthi AI server at:\n" + backendUrl
                                + "\n\nPlease ensure your Python backend is running on your computer!");
                    });
                }

                @Override
                public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                    runOnUiThread(() -> btnGenerateAI.setEnabled(true));

                    try {
                        String responseBody = response.body() != null ? response.body().string() : "";

                        if (!response.isSuccessful()) {
                            // Extract clean error detail if available
                            String errorDetail = "Server returned status: " + response.code();
                            try {
                                JSONObject errObj = new JSONObject(responseBody);
                                if (errObj.has("detail")) errorDetail = errObj.getString("detail");
                            } catch (Exception ignored) {}

                            final String finalErr = errorDetail;
                            runOnUiThread(() -> tvAITimetable.setText("❌ " + finalErr));
                            return;
                        }

                        JSONObject obj = new JSONObject(responseBody);
                        JSONArray timetable = obj.getJSONArray("timetable");
                        lastGeneratedTimetable = timetable;

                        StringBuilder formatted = new StringBuilder();
                        for (int i = 0; i < timetable.length(); i++) {
                            JSONObject item = timetable.getJSONObject(i);
                            int day = item.getInt("day");
                            String date = item.getString("date");
                            String task = item.getString("task");

                            formatted.append("Day ").append(day)
                                    .append(" – ").append(date)
                                    .append("\nTask: ").append(task)
                                    .append("\n\n");
                        }

                        runOnUiThread(() -> {
                            tvAITimetable.setText(formatted.toString());
                            btnStartProgress.setVisibility(View.VISIBLE);
                        });

                    } catch (Exception e) {
                        runOnUiThread(() -> tvAITimetable.setText("Error parsing response: " + e.getMessage()));
                    }
                }
            });

        } catch (Exception e) {
            btnGenerateAI.setEnabled(true);
            tvAITimetable.setText("Request preparation error: " + e.getMessage());
        }
    }
}
