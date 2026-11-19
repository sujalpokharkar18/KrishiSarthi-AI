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
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

public class LoginActivity extends AppCompatActivity {

    private static final String TAG = "LoginActivity";

    private EditText editTextEmail, editTextPassword;
    private Button buttonLogin;
    private TextView textViewSignUpLink;
    private ProgressBar progressBar;

    private FirebaseAuth mAuth;
    private DatabaseReference dbRef;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        mAuth = FirebaseAuth.getInstance();
        dbRef = FirebaseDatabase.getInstance().getReference("users");

        editTextEmail = findViewById(R.id.editTextEmail);
        editTextPassword = findViewById(R.id.editTextPassword);
        buttonLogin = findViewById(R.id.buttonLogin);
        textViewSignUpLink = findViewById(R.id.textViewSignUp);
        progressBar = findViewById(R.id.progressBar);

        buttonLogin.setOnClickListener(v -> loginUser());

        textViewSignUpLink.setOnClickListener(v -> {
            startActivity(new Intent(LoginActivity.this, SignUpActivity.class));
            finish();
        });
    }

    @Override
    protected void onStart() {
        super.onStart();
        // Check local saved session or Firebase User for auto-login
        SharedPreferences sp = getSharedPreferences("AgriBandhuSession", MODE_PRIVATE);
        boolean isLoggedIn = sp.getBoolean("is_logged_in", false);
        String savedEmail = sp.getString("saved_email", null);
        String savedUid = sp.getString("saved_uid", "");

        if (isLoggedIn && savedEmail != null && !savedEmail.isEmpty()) {
            navigateToMain(savedEmail, savedUid);
            return;
        }

        FirebaseUser currentUser = mAuth.getCurrentUser();
        if (currentUser != null && currentUser.getEmail() != null) {
            navigateToMain(currentUser.getEmail(), currentUser.getUid());
        }
    }

    private void loginUser() {
        String email = editTextEmail.getText().toString().trim();
        String password = editTextPassword.getText().toString().trim();

        if (TextUtils.isEmpty(email) || !Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            editTextEmail.setError("Valid email is required");
            editTextEmail.requestFocus();
            return;
        }

        if (TextUtils.isEmpty(password)) {
            editTextPassword.setError("Password is required");
            editTextPassword.requestFocus();
            return;
        }

        if (progressBar != null) progressBar.setVisibility(View.VISIBLE);
        buttonLogin.setEnabled(false);

        // 1. Try Firebase Auth
        mAuth.signInWithEmailAndPassword(email, password)
                .addOnCompleteListener(this, task -> {
                    if (task.isSuccessful()) {
                        if (progressBar != null) progressBar.setVisibility(View.GONE);
                        buttonLogin.setEnabled(true);

                        FirebaseUser user = mAuth.getCurrentUser();
                        String uid = user != null ? user.getUid() : "";

                        saveLocalSession(email, uid);
                        Toast.makeText(LoginActivity.this, "Login successful!", Toast.LENGTH_SHORT).show();
                        navigateToMain(email, uid);
                    } else {
                        String error = task.getException() != null ? task.getException().getMessage() : "Authentication failed";
                        Log.w(TAG, "Auth error: " + error);

                        // If Firebase Console has not enabled Email Auth provider yet
                        if (error != null && error.contains("CONFIGURATION_NOT_FOUND")) {
                            Log.i(TAG, "Email Auth disabled in console. Verifying via Realtime Database fallback.");
                            loginViaDatabaseFallback(email, password);
                        } else {
                            if (progressBar != null) progressBar.setVisibility(View.GONE);
                            buttonLogin.setEnabled(true);
                            Toast.makeText(LoginActivity.this, "Login Failed: " + error, Toast.LENGTH_LONG).show();
                        }
                    }
                });
    }

    private void loginViaDatabaseFallback(String email, String password) {
        String emailKey = email.replace(".", "_");
        String inputHash = SignUpActivity.hashPassword(password);

        dbRef.child(emailKey).addListenerForSingleValueEvent(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot snapshot) {
                if (progressBar != null) progressBar.setVisibility(View.GONE);
                buttonLogin.setEnabled(true);

                if (snapshot.exists()) {
                    String storedHash = snapshot.child("passwordHash").getValue(String.class);
                    String legacyPlainPassword = snapshot.child("password").getValue(String.class);
                    String uid = snapshot.child("uid").getValue(String.class);
                    if (uid == null) uid = "";

                    boolean valid = false;
                    if (storedHash != null && storedHash.equals(inputHash)) {
                        valid = true;
                    } else if (legacyPlainPassword != null && legacyPlainPassword.equals(password)) {
                        valid = true;
                    }

                    if (valid) {
                        saveLocalSession(email, uid);
                        Toast.makeText(LoginActivity.this, "Login successful!", Toast.LENGTH_SHORT).show();
                        navigateToMain(email, uid);
                    } else {
                        Toast.makeText(LoginActivity.this, "Incorrect password. Please try again.", Toast.LENGTH_SHORT).show();
                    }
                } else {
                    Toast.makeText(LoginActivity.this, "Account not found. Please Sign Up.", Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
                if (progressBar != null) progressBar.setVisibility(View.GONE);
                buttonLogin.setEnabled(true);
                Toast.makeText(LoginActivity.this, "Database Error: " + error.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void saveLocalSession(String email, String uid) {
        SharedPreferences sp = getSharedPreferences("AgriBandhuSession", MODE_PRIVATE);
        sp.edit()
                .putString("saved_email", email)
                .putString("saved_uid", uid)
                .putBoolean("is_logged_in", true)
                .apply();
    }

    private void navigateToMain(String email, String uid) {
        Intent intent = new Intent(LoginActivity.this, MainActivity.class);
        intent.putExtra("email", email);
        intent.putExtra("uid", uid);
        startActivity(intent);
        finish();
    }
}
