package com.example.agribandhu;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.cardview.widget.CardView;

import com.example.agribandhu.network.ApiClient;
import com.example.agribandhu.network.ApiService;
import com.example.agribandhu.network.models.AnswerResponse;
import com.example.agribandhu.network.models.DiagnosisRequest;
import com.example.agribandhu.network.models.DiagnosisResponse;
import com.example.agribandhu.network.models.QuestionRequest;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class Ai_chat extends AppCompatActivity {

    private EditText etPrompt;
    private Button btnSend;
    private ImageButton btnAttachPhoto, btnRemoveAttachment;
    private TextView tvResponse, tvAttachedSubtitle;
    private ImageView ivAttachedThumbnail;
    private CardView layoutAttachedImage;
    private ScrollView chatScrollView;

    private Uri attachedImageUri = null;
    private final StringBuilder chatHistory = new StringBuilder();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ai_chat);

        Toolbar toolbar = findViewById(R.id.chatToolbar);
        if (toolbar != null) {
            toolbar.setNavigationOnClickListener(v -> finish());
        }

        etPrompt = findViewById(R.id.etPrompt);
        btnSend = findViewById(R.id.btnSend);
        btnAttachPhoto = findViewById(R.id.btnAttachPhoto);
        btnRemoveAttachment = findViewById(R.id.btnRemoveAttachment);
        tvResponse = findViewById(R.id.tvResponse);
        tvAttachedSubtitle = findViewById(R.id.tvAttachedSubtitle);
        ivAttachedThumbnail = findViewById(R.id.ivAttachedThumbnail);
        layoutAttachedImage = findViewById(R.id.layoutAttachedImage);
        chatScrollView = findViewById(R.id.chatScrollView);

        // Photo picker launcher
        ActivityResultLauncher<Intent> imagePickerLauncher = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> {
                    if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                        Uri uri = result.getData().getData();
                        if (uri != null) {
                            setAttachedPhoto(uri);
                        }
                    }
                });

        if (btnAttachPhoto != null) {
            btnAttachPhoto.setOnClickListener(v -> {
                Intent pickIntent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
                pickIntent.setType("image/*");
                imagePickerLauncher.launch(pickIntent);
            });
        }

        if (btnRemoveAttachment != null) {
            btnRemoveAttachment.setOnClickListener(v -> clearAttachedPhoto());
        }

        // Check if opened from Post activity with photo and/or diagnosis
        Intent intent = getIntent();
        if (intent != null) {
            String incomingCrop = intent.getStringExtra("crop_name");
            String incomingReport = intent.getStringExtra("diagnosis_report");
            String incomingImageUri = intent.getStringExtra("image_uri");

            if (incomingImageUri != null && !incomingImageUri.isEmpty()) {
                setAttachedPhoto(Uri.parse(incomingImageUri));
            }

            if (incomingReport != null && !incomingReport.isEmpty()) {
                appendChatMessage("🤖 KrishiSarthi Plant Doctor Diagnosis:\n\n" + incomingReport);
                etPrompt.setHint("Ask any question about this disease or treatment...");
            }
        }

        btnSend.setOnClickListener(v -> {
            String prompt = etPrompt.getText().toString().trim();

            if (prompt.isEmpty() && attachedImageUri == null) {
                Toast.makeText(this, "Please enter a question or attach a crop photo.", Toast.LENGTH_SHORT).show();
                return;
            }

            if (attachedImageUri != null) {
                // Diagnose or ask question about attached photo
                diagnoseAttachedPhoto(prompt);
            } else {
                // Text question to AI chatbot
                askTextQuestion(prompt);
            }
        });
    }

    private void setAttachedPhoto(Uri uri) {
        attachedImageUri = uri;
        if (layoutAttachedImage != null) {
            layoutAttachedImage.setVisibility(View.VISIBLE);
        }
        if (ivAttachedThumbnail != null) {
            ivAttachedThumbnail.setImageURI(uri);
        }
        if (tvAttachedSubtitle != null) {
            tvAttachedSubtitle.setText("Photo ready. Tap 'Ask AI' to diagnose disease & treatment.");
        }
    }

    private void clearAttachedPhoto() {
        attachedImageUri = null;
        if (layoutAttachedImage != null) {
            layoutAttachedImage.setVisibility(View.GONE);
        }
        if (ivAttachedThumbnail != null) {
            ivAttachedThumbnail.setImageURI(null);
        }
    }

    private void appendChatMessage(String message) {
        if (chatHistory.length() > 0) {
            chatHistory.append("\n\n────────────────────\n\n");
        }
        chatHistory.append(message);
        tvResponse.setText(chatHistory.toString());

        if (chatScrollView != null) {
            chatScrollView.post(() -> chatScrollView.fullScroll(View.FOCUS_DOWN));
        }
    }

    private void askTextQuestion(String question) {
        btnSend.setEnabled(false);
        appendChatMessage("🧑‍🌾 Farmer:\n" + question);
        etPrompt.setText("");

        ApiService api = ApiClient.getClient().create(ApiService.class);
        QuestionRequest req = new QuestionRequest(question);

        api.askAI(req).enqueue(new Callback<AnswerResponse>() {
            @Override
            public void onResponse(@NonNull Call<AnswerResponse> call, @NonNull Response<AnswerResponse> response) {
                runOnUiThread(() -> btnSend.setEnabled(true));

                if (response.isSuccessful() && response.body() != null) {
                    AnswerResponse answer = response.body();
                    String reply = answer.getReply();
                    String label = answer.getLabel();

                    StringBuilder sb = new StringBuilder("🤖 KrishiSarthi AI:\n");
                    if (!label.isEmpty() && !label.equals("UNKNOWN")) {
                        sb.append("📋 Topic: ").append(label.replace("_", " ")).append("\n\n");
                    }
                    sb.append(reply);

                    runOnUiThread(() -> appendChatMessage(sb.toString()));
                } else {
                    runOnUiThread(() -> appendChatMessage("⚠️ Server error code: " + response.code() + ". Please retry."));
                }
            }

            @Override
            public void onFailure(@NonNull Call<AnswerResponse> call, @NonNull Throwable t) {
                runOnUiThread(() -> {
                    btnSend.setEnabled(true);
                    appendChatMessage("⚠️ Connection Failed: " + t.getMessage()
                            + "\n\nPlease ensure your Python FastAPI server is running.");
                });
            }
        });
    }

    private void diagnoseAttachedPhoto(String userQuestion) {
        btnSend.setEnabled(false);
        String farmerDisplay = userQuestion.isEmpty() ? "Diagnose crop disease in this photo." : userQuestion;
        appendChatMessage("🧑‍🌾 Farmer (📷 Photo Attached):\n" + farmerDisplay);
        etPrompt.setText("");

        Uri imageToProcess = attachedImageUri;
        new Thread(() -> {
            byte[] imageBytes = compressImage(imageToProcess);
            if (imageBytes == null || imageBytes.length == 0) {
                runOnUiThread(() -> {
                    btnSend.setEnabled(true);
                    appendChatMessage("❌ Could not read photo data. Please choose another picture.");
                });
                return;
            }

            String base64Image = Base64.encodeToString(imageBytes, Base64.NO_WRAP);
            DiagnosisRequest request = new DiagnosisRequest(base64Image, "", userQuestion);
            ApiService api = ApiClient.getClient().create(ApiService.class);

            api.diagnoseCrop(request).enqueue(new Callback<DiagnosisResponse>() {
                @Override
                public void onResponse(@NonNull Call<DiagnosisResponse> call, @NonNull Response<DiagnosisResponse> response) {
                    runOnUiThread(() -> {
                        btnSend.setEnabled(true);
                        clearAttachedPhoto();

                        if (response.isSuccessful() && response.body() != null && response.body().getDiagnosis() != null) {
                            DiagnosisResponse.DiagnosisDetail diag = response.body().getDiagnosis();
                            appendChatMessage("🤖 KrishiSarthi Plant Doctor:\n\n" + diag.getReport());
                        } else {
                            appendChatMessage("⚠️ Server returned response code: " + response.code());
                        }
                    });
                }

                @Override
                public void onFailure(@NonNull Call<DiagnosisResponse> call, @NonNull Throwable t) {
                    runOnUiThread(() -> {
                        btnSend.setEnabled(true);
                        appendChatMessage("⚠️ Failed to diagnose photo: " + t.getMessage());
                    });
                }
            });
        }).start();
    }

    private byte[] compressImage(Uri imageUri) {
        try {
            InputStream input = getContentResolver().openInputStream(imageUri);
            Bitmap original = BitmapFactory.decodeStream(input);
            if (input != null) input.close();

            if (original == null) return null;

            int maxDim = 1024;
            int width = original.getWidth();
            int height = original.getHeight();

            float ratio = Math.min((float) maxDim / width, (float) maxDim / height);
            if (ratio < 1.0f) {
                width = Math.round(ratio * width);
                height = Math.round(ratio * height);
                original = Bitmap.createScaledBitmap(original, width, height, true);
            }

            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            original.compress(Bitmap.CompressFormat.JPEG, 75, baos);
            return baos.toByteArray();
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
}
