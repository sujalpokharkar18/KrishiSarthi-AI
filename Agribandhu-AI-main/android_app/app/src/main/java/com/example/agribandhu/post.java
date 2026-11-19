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
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.example.agribandhu.network.ApiClient;
import com.example.agribandhu.network.ApiService;
import com.example.agribandhu.network.models.DiagnosisRequest;
import com.example.agribandhu.network.models.DiagnosisResponse;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageReference;
import com.google.firebase.storage.UploadTask;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class post extends AppCompatActivity {

    private ImageView imagePreview;
    private EditText postDescription;
    private Button selectImageBtn, uploadPostBtn, btnDiagnosePhoto, btnApplyToDescription, btnChatAboutDisease;
    private ProgressBar uploadProgressBar;
    private LinearLayout layoutAiDiagnosis;
    private TextView tvDiagnosisResult;

    private Uri selectedImageUri = null;
    private DatabaseReference dbRef;
    private StorageReference storageRef;
    private String userEmail;

    private String lastDiagnosisReport = "";
    private String lastCropName = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_post);

        Toolbar toolbar = findViewById(R.id.toolbar);
        if (toolbar != null) {
            toolbar.setNavigationOnClickListener(v -> finish());
        }

        imagePreview = findViewById(R.id.imagePreview);
        postDescription = findViewById(R.id.postDescription);
        selectImageBtn = findViewById(R.id.selectImageBtn);
        uploadPostBtn = findViewById(R.id.uploadPostBtn);
        uploadProgressBar = findViewById(R.id.uploadProgressBar);
        btnDiagnosePhoto = findViewById(R.id.btnDiagnosePhoto);
        layoutAiDiagnosis = findViewById(R.id.layoutAiDiagnosis);
        tvDiagnosisResult = findViewById(R.id.tvDiagnosisResult);
        btnApplyToDescription = findViewById(R.id.btnApplyToDescription);
        btnChatAboutDisease = findViewById(R.id.btnChatAboutDisease);

        // Get user email from intent, active auth, or session preferences
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

        // Database and Storage references
        String emailKey = userEmail.replace(".", "_");
        dbRef = FirebaseDatabase.getInstance().getReference("users")
                .child(emailKey)
                .child("post");
        storageRef = FirebaseStorage.getInstance().getReference("posts").child(emailKey);

        // Image picker launcher
        ActivityResultLauncher<Intent> imagePickerLauncher = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> {
                    if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                        selectedImageUri = result.getData().getData();
                        imagePreview.setImageURI(selectedImageUri);
                        findViewById(R.id.tvSelectHint).setVisibility(View.GONE);
                    }
                });

        selectImageBtn.setOnClickListener(v -> {
            Intent pickIntent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
            pickIntent.setType("image/*");
            imagePickerLauncher.launch(pickIntent);
        });

        // 🔬 Diagnose Crop Disease from Photo
        if (btnDiagnosePhoto != null) {
            btnDiagnosePhoto.setOnClickListener(v -> performAiDiagnosis());
        }

        // 📝 Copy diagnosis into post description
        if (btnApplyToDescription != null) {
            btnApplyToDescription.setOnClickListener(v -> {
                if (!lastDiagnosisReport.isEmpty()) {
                    String existing = postDescription.getText().toString().trim();
                    if (existing.isEmpty()) {
                        postDescription.setText(lastDiagnosisReport);
                    } else {
                        postDescription.setText(existing + "\n\n" + lastDiagnosisReport);
                    }
                    Toast.makeText(this, "Diagnosis copied into post description!", Toast.LENGTH_SHORT).show();
                }
            });
        }

        // 💬 Open AI Chatbot to converse about this photo/disease
        if (btnChatAboutDisease != null) {
            btnChatAboutDisease.setOnClickListener(v -> {
                Intent chatIntent = new Intent(post.this, Ai_chat.class);
                chatIntent.putExtra("crop_name", lastCropName);
                chatIntent.putExtra("diagnosis_report", lastDiagnosisReport);
                if (selectedImageUri != null) {
                    chatIntent.putExtra("image_uri", selectedImageUri.toString());
                }
                startActivity(chatIntent);
            });
        }

        uploadPostBtn.setOnClickListener(v -> uploadPost());
    }

    /**
     * Sends the selected image to the KrishiSarthi FastAPI plant pathology doctor engine.
     */
    private void performAiDiagnosis() {
        if (selectedImageUri == null) {
            Toast.makeText(this, "Please select a crop photo first!", Toast.LENGTH_SHORT).show();
            return;
        }

        btnDiagnosePhoto.setEnabled(false);
        btnDiagnosePhoto.setText("🔬 Analyzing Photo with KrishiSarthi AI...");
        if (layoutAiDiagnosis != null) {
            layoutAiDiagnosis.setVisibility(View.VISIBLE);
        }
        if (tvDiagnosisResult != null) {
            tvDiagnosisResult.setText("⏳ Scanning leaf/crop patterns, disease lesions, and consulting AI plant pathologist...");
        }

        new Thread(() -> {
            byte[] imageBytes = compressImage(selectedImageUri);
            if (imageBytes == null || imageBytes.length == 0) {
                runOnUiThread(() -> {
                    btnDiagnosePhoto.setEnabled(true);
                    btnDiagnosePhoto.setText("🔬 Ask AI to Diagnose Disease in This Photo");
                    if (tvDiagnosisResult != null) {
                        tvDiagnosisResult.setText("❌ Failed to process the selected image. Please try another photo.");
                    }
                });
                return;
            }

            String base64Image = Base64.encodeToString(imageBytes, Base64.NO_WRAP);
            String userNotes = postDescription.getText().toString().trim();

            // Extract crop name if mentioned in description
            String probableCrop = "";
            String lowerNotes = userNotes.toLowerCase();
            for (String c : new String[]{"tomato", "potato", "wheat", "rice", "chilli", "cotton", "onion", "maize"}) {
                if (lowerNotes.contains(c)) {
                    probableCrop = c;
                    break;
                }
            }

            DiagnosisRequest request = new DiagnosisRequest(base64Image, probableCrop, userNotes);
            ApiService apiService = ApiClient.getClient().create(ApiService.class);

            apiService.diagnoseCrop(request).enqueue(new Callback<DiagnosisResponse>() {
                @Override
                public void onResponse(@NonNull Call<DiagnosisResponse> call, @NonNull Response<DiagnosisResponse> response) {
                    runOnUiThread(() -> {
                        btnDiagnosePhoto.setEnabled(true);
                        btnDiagnosePhoto.setText("🔬 Ask AI to Diagnose Disease in This Photo");

                        if (response.isSuccessful() && response.body() != null && response.body().getDiagnosis() != null) {
                            DiagnosisResponse.DiagnosisDetail diag = response.body().getDiagnosis();
                            lastCropName = diag.getCrop();
                            lastDiagnosisReport = diag.getReport();
                            if (tvDiagnosisResult != null) {
                                tvDiagnosisResult.setText(lastDiagnosisReport);
                            }
                            Toast.makeText(post.this, "✅ AI Diagnosis Complete!", Toast.LENGTH_SHORT).show();
                        } else {
                            if (tvDiagnosisResult != null) {
                                tvDiagnosisResult.setText("⚠️ Server returned response code " + response.code() + ". Please retry in a moment.");
                            }
                        }
                    });
                }

                @Override
                public void onFailure(@NonNull Call<DiagnosisResponse> call, @NonNull Throwable t) {
                    runOnUiThread(() -> {
                        btnDiagnosePhoto.setEnabled(true);
                        btnDiagnosePhoto.setText("🔬 Ask AI to Diagnose Disease in This Photo");
                        if (tvDiagnosisResult != null) {
                            tvDiagnosisResult.setText("⚠️ Could not reach AI Plant Doctor: " + t.getMessage()
                                    + "\n\nPlease ensure your Python backend is active.");
                        }
                    });
                }
            });
        }).start();
    }

    /**
     * Resizes and compresses image to prevent Out-Of-Memory and high storage consumption.
     */
    private byte[] compressImage(Uri imageUri) {
        try {
            InputStream input = getContentResolver().openInputStream(imageUri);
            Bitmap original = BitmapFactory.decodeStream(input);
            if (input != null) input.close();

            if (original == null) return null;

            // Maximum dimension 1024px
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

    private void uploadPost() {
        String description = postDescription.getText().toString().trim();

        if (selectedImageUri == null) {
            Toast.makeText(this, "Please select an image first!", Toast.LENGTH_SHORT).show();
            return;
        }

        if (description.isEmpty()) {
            Toast.makeText(this, "Please enter a description!", Toast.LENGTH_SHORT).show();
            return;
        }

        if (uploadProgressBar != null) uploadProgressBar.setVisibility(View.VISIBLE);
        uploadPostBtn.setEnabled(false);
        selectImageBtn.setEnabled(false);

        // 1. Compress image in background
        new Thread(() -> {
            byte[] imageBytes = compressImage(selectedImageUri);

            runOnUiThread(() -> {
                if (imageBytes == null || imageBytes.length == 0) {
                    resetUiAfterUpload();
                    Toast.makeText(post.this, "Failed to process image.", Toast.LENGTH_SHORT).show();
                    return;
                }

                // 2. Upload to Firebase Storage with automatic Base64 fallback
                String fileName = System.currentTimeMillis() + "_" + UUID.randomUUID().toString().substring(0, 8) + ".jpg";
                StorageReference fileRef = storageRef.child(fileName);

                UploadTask uploadTask = fileRef.putBytes(imageBytes);
                uploadTask.addOnSuccessListener(taskSnapshot -> {
                    // 3. Obtain permanent download URL
                    fileRef.getDownloadUrl().addOnSuccessListener(downloadUri -> {
                        savePostToDatabase(description, downloadUri.toString());
                    }).addOnFailureListener(e -> {
                        // Fallback: save compressed base64 directly to database
                        String base64Img = Base64.encodeToString(imageBytes, Base64.NO_WRAP);
                        savePostToDatabase(description, base64Img);
                    });
                }).addOnFailureListener(e -> {
                    // Fallback on storage failure: save compressed base64 directly to database
                    String base64Img = Base64.encodeToString(imageBytes, Base64.NO_WRAP);
                    savePostToDatabase(description, base64Img);
                });
            });
        }).start();
    }

    private void savePostToDatabase(String description, String imageUrl) {
        dbRef.get().addOnSuccessListener(snapshot -> {
            long nextPostNumber = snapshot.getChildrenCount() + 1;
            DatabaseReference newPostRef = dbRef.child(String.valueOf(nextPostNumber));

            Map<String, Object> postMap = new HashMap<>();
            postMap.put("description", description);
            postMap.put("farmerName", userEmail.split("@")[0]);
            postMap.put("imageUri", imageUrl);
            postMap.put("timestamp", System.currentTimeMillis());

            newPostRef.setValue(postMap)
                    .addOnSuccessListener(aVoid -> {
                        resetUiAfterUpload();
                        Toast.makeText(post.this, "Post uploaded successfully!", Toast.LENGTH_LONG).show();
                        postDescription.setText("");
                        imagePreview.setImageURI(null);
                        selectedImageUri = null;
                        finish();
                    })
                    .addOnFailureListener(e -> {
                        resetUiAfterUpload();
                        Toast.makeText(post.this, "Database error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                    });
        }).addOnFailureListener(e -> {
            resetUiAfterUpload();
            Toast.makeText(post.this, "Failed to read post count: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        });
    }

    private void resetUiAfterUpload() {
        if (uploadProgressBar != null) uploadProgressBar.setVisibility(View.GONE);
        uploadPostBtn.setEnabled(true);
        selectImageBtn.setEnabled(true);
    }
}
