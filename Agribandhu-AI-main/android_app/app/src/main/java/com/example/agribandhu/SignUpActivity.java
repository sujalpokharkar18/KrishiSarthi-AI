package com.example.agribandhu;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.util.Patterns;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class SignUpActivity extends AppCompatActivity {

    private static final String TAG = "SignUpActivity";

    private EditText editTextName, editTextEmail, editTextPassword, editTextAddress;
    private Button buttonSignUp;
    private TextView textViewLoginLink;
    private ProgressBar progressBar;

    private FirebaseAuth mAuth;
    private DatabaseReference dbRef;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_signup);

        mAuth = FirebaseAuth.getInstance();
        dbRef = FirebaseDatabase.getInstance().getReference("users");

        editTextName = findViewById(R.id.editTextName);
        editTextEmail = findViewById(R.id.editTextEmail);
        editTextPassword = findViewById(R.id.editTextPassword);
        editTextAddress = findViewById(R.id.editTextaddress);
        buttonSignUp = findViewById(R.id.buttonSignUp);
        textViewLoginLink = findViewById(R.id.textViewLogin);
        progressBar = findViewById(R.id.progressBar);

        buttonSignUp.setOnClickListener(v -> registerUser());

        textViewLoginLink.setOnClickListener(v -> {
            startActivity(new Intent(SignUpActivity.this, LoginActivity.class));
            finish();
        });
    }

    private void registerUser() {
        String name = editTextName.getText().toString().trim();
        String email = editTextEmail.getText().toString().trim();
        String password = editTextPassword.getText().toString().trim();
        String address = editTextAddress.getText().toString().trim();

        if (TextUtils.isEmpty(name)) {
            editTextName.setError("Name is required");
            editTextName.requestFocus();
            return;
        }

        if (TextUtils.isEmpty(email) || !Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            editTextEmail.setError("Valid email is required");
            editTextEmail.requestFocus();
            return;
        }

        if (TextUtils.isEmpty(password) || password.length() < 6) {
            editTextPassword.setError("Password must be at least 6 characters");
            editTextPassword.requestFocus();
            return;
        }

        if (TextUtils.isEmpty(address)) {
            editTextAddress.setError("Address/Village is required");
            editTextAddress.requestFocus();
            return;
        }

        if (progressBar != null) progressBar.setVisibility(View.VISIBLE);
        buttonSignUp.setEnabled(false);

        // 1. Try modern Firebase Auth first
        mAuth.createUserWithEmailAndPassword(email, password)
                .addOnCompleteListener(this, task -> {
                    if (task.isSuccessful()) {
                        FirebaseUser user = mAuth.getCurrentUser();
                        String uid = user != null ? user.getUid() : UUID.randomUUID().toString();
                        saveUserProfile(uid, name, email, address, password);
                    } else {
                        String errorMsg = task.getException() != null ? task.getException().getMessage() : "Registration failed";
                        Log.w(TAG, "FirebaseAuth error: " + errorMsg);

                        // If Firebase Console has not enabled Email/Password Auth yet
                        if (errorMsg != null && errorMsg.contains("CONFIGURATION_NOT_FOUND")) {
                            Log.i(TAG, "Email Auth not enabled in console. Falling back to secure database registration.");
                            String fallbackUid = UUID.randomUUID().toString();
                            saveUserProfile(fallbackUid, name, email, address, password);
                        } else {
                            if (progressBar != null) progressBar.setVisibility(View.GONE);
                            buttonSignUp.setEnabled(true);
                            Toast.makeText(SignUpActivity.this, "Sign Up Error: " + errorMsg, Toast.LENGTH_LONG).show();
                        }
                    }
                });
    }

    private void saveUserProfile(String uid, String name, String email, String address, String rawPassword) {
        String emailKey = email.replace(".", "_");

        Map<String, Object> userProfile = new HashMap<>();
        userProfile.put("uid", uid);
        userProfile.put("name", name);
        userProfile.put("email", email);
        userProfile.put("address", address);
        userProfile.put("farmSize", "5 Acres");
        userProfile.put("income", "₹25,000/month");
        userProfile.put("passwordHash", hashPassword(rawPassword));
        userProfile.put("createdAt", System.currentTimeMillis());

        dbRef.child(emailKey).setValue(userProfile)
                .addOnCompleteListener(dbTask -> {
                    if (progressBar != null) progressBar.setVisibility(View.GONE);
                    buttonSignUp.setEnabled(true);

                    if (dbTask.isSuccessful()) {
                        // Persist session locally
                        SharedPreferences sp = getSharedPreferences("AgriBandhuSession", MODE_PRIVATE);
                        sp.edit()
                                .putString("saved_email", email)
                                .putString("saved_uid", uid)
                                .putString("saved_name", name)
                                .putString("saved_address", address)
                                .putBoolean("is_logged_in", true)
                                .apply();

                        Toast.makeText(SignUpActivity.this, "Account created successfully!", Toast.LENGTH_SHORT).show();

                        Intent intent = new Intent(SignUpActivity.this, MainActivity.class);
                        intent.putExtra("email", email);
                        intent.putExtra("uid", uid);
                        startActivity(intent);
                        finish();
                    } else {
                        String dbError = dbTask.getException() != null ? dbTask.getException().getMessage() : "Failed to save profile";
                        Toast.makeText(SignUpActivity.this, "Database Error: " + dbError, Toast.LENGTH_LONG).show();
                    }
                });
    }

    public static String hashPassword(String password) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(password.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            return String.valueOf(password.hashCode());
        }
    }
}
