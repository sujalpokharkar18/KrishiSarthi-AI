package com.example.agribandhu;

import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.HashMap;
import java.util.Map;

public class Main_Account extends AppCompatActivity {

    private LinearLayout aiCropButton, aiFertilizerButton;
    private TextView farmerName, farmerLocation, farmerEmailText, farmSize, farmIncome;
    private TextView txtTotalCropsCount;
    private LinearLayout cropContainer, emptyCropsView;
    private Button btnEditProfile, btnLogout, btnPlanFirstCrop;

    private String email;
    private String currentName = "";
    private String currentLocation = "";
    private String currentFarmSize = "5 Acres";
    private String currentIncome = "₹25,000/month";

    private DatabaseReference dbRef, cropRef;
    private SharedPreferences sessionSp;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_account);

        sessionSp = getSharedPreferences("AgriBandhuSession", MODE_PRIVATE);

        // Toolbar
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            toolbar.setNavigationOnClickListener(v -> finish());
        }

        // Initialize UI Elements
        farmerName = findViewById(R.id.farmerName);
        farmerLocation = findViewById(R.id.farmerLocation);
        farmerEmailText = findViewById(R.id.farmerEmailText);
        farmSize = findViewById(R.id.farmSize);
        farmIncome = findViewById(R.id.farmIncome);

        btnEditProfile = findViewById(R.id.btnEditProfile);
        btnLogout = findViewById(R.id.btnLogout);

        aiCropButton = findViewById(R.id.aiCropButton);
        aiFertilizerButton = findViewById(R.id.aiFertilizerButton);

        cropContainer = findViewById(R.id.cropContainer);
        emptyCropsView = findViewById(R.id.emptyCropsView);
        txtTotalCropsCount = findViewById(R.id.txtTotalCropsCount);
        btnPlanFirstCrop = findViewById(R.id.btnPlanFirstCrop);

        // Resolve Email Session
        resolveUserEmail();

        String emailKey = email.replace(".", "_");
        dbRef = FirebaseDatabase.getInstance().getReference("users").child(emailKey);
        cropRef = dbRef.child("crops");

        // Fetch User and Farm Data
        loadUserProfile();
        loadCropCards();

        // Listeners
        btnEditProfile.setOnClickListener(v -> showEditProfileDialog());
        btnLogout.setOnClickListener(v -> performLogout());

        if (btnPlanFirstCrop != null) {
            btnPlanFirstCrop.setOnClickListener(v -> launchAIChatbot());
        }

        aiCropButton.setOnClickListener(v -> {
            Intent i = new Intent(Main_Account.this, Ai_chat.class);
            i.putExtra("email", email);
            startActivity(i);
        });

        aiFertilizerButton.setOnClickListener(v -> launchAIChatbot());
    }

    private void resolveUserEmail() {
        Intent intent = getIntent();
        email = intent.getStringExtra("email");

        if (email == null || email.isEmpty()) {
            FirebaseUser u = FirebaseAuth.getInstance().getCurrentUser();
            if (u != null && u.getEmail() != null) {
                email = u.getEmail();
            }
        }

        if (email == null || email.isEmpty()) {
            email = sessionSp.getString("saved_email", null);
        }

        if (email == null || email.isEmpty()) {
            email = "farmer@krishisarthi.com";
        }

        if (farmerEmailText != null) {
            farmerEmailText.setText("✉️ " + email);
        }
    }

    private void launchAIChatbot() {
        Intent i = new Intent(Main_Account.this, AIChatbot.class);
        i.putExtra("email", email);
        startActivity(i);
    }

    // ──────────────── Load Profile & Farm Details ────────────────
    private void loadUserProfile() {
        dbRef.addListenerForSingleValueEvent(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot snapshot) {
                if (snapshot.exists()) {
                    String name = snapshot.child("name").getValue(String.class);
                    String address = snapshot.child("address").getValue(String.class);
                    String size = snapshot.child("farmSize").getValue(String.class);
                    String inc = snapshot.child("income").getValue(String.class);

                    if (name != null && !name.isEmpty()) currentName = name;
                    else currentName = email.split("@")[0];

                    if (address != null && !address.isEmpty()) currentLocation = address;
                    else currentLocation = "Not specified";

                    if (size != null && !size.isEmpty()) currentFarmSize = size;
                    if (inc != null && !inc.isEmpty()) currentIncome = inc;

                    updateProfileUi();
                } else {
                    currentName = sessionSp.getString("saved_name", email.split("@")[0]);
                    currentLocation = "Not specified";
                    updateProfileUi();
                }
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
                Toast.makeText(Main_Account.this, "Offline profile loaded", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void updateProfileUi() {
        farmerName.setText(capitalize(currentName));
        farmerLocation.setText("📍 " + currentLocation);
        farmSize.setText("🌾 " + currentFarmSize);
        farmIncome.setText("💰 " + currentIncome);
    }

    // ──────────────── Edit Profile Dialog ────────────────
    private void showEditProfileDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_edit_profile, null);
        builder.setView(dialogView);

        AlertDialog dialog = builder.create();

        EditText editName = dialogView.findViewById(R.id.editName);
        EditText editLocation = dialogView.findViewById(R.id.editLocation);
        EditText editFarmSize = dialogView.findViewById(R.id.editFarmSize);
        EditText editIncome = dialogView.findViewById(R.id.editIncome);
        Button btnCancel = dialogView.findViewById(R.id.btnCancelEdit);
        Button btnSave = dialogView.findViewById(R.id.btnSaveProfile);

        // Pre-fill existing data
        editName.setText(currentName);
        editLocation.setText(currentLocation.equals("Not specified") ? "" : currentLocation);
        editFarmSize.setText(currentFarmSize);
        editIncome.setText(currentIncome);

        btnCancel.setOnClickListener(v -> dialog.dismiss());

        btnSave.setOnClickListener(v -> {
            String newName = editName.getText().toString().trim();
            String newLoc = editLocation.getText().toString().trim();
            String newSize = editFarmSize.getText().toString().trim();
            String newInc = editIncome.getText().toString().trim();

            if (newName.isEmpty()) {
                editName.setError("Name is required");
                return;
            }

            if (newLoc.isEmpty()) newLoc = "Not specified";
            if (newSize.isEmpty()) newSize = "5 Acres";
            if (newInc.isEmpty()) newInc = "₹25,000/month";

            // Save to Firebase
            Map<String, Object> updates = new HashMap<>();
            updates.put("name", newName);
            updates.put("address", newLoc);
            updates.put("farmSize", newSize);
            updates.put("income", newInc);

            final String fName = newName;
            final String fLoc = newLoc;
            final String fSize = newSize;
            final String fInc = newInc;

            dbRef.updateChildren(updates).addOnCompleteListener(task -> {
                currentName = fName;
                currentLocation = fLoc;
                currentFarmSize = fSize;
                currentIncome = fInc;

                // Save locally
                sessionSp.edit()
                        .putString("saved_name", fName)
                        .putString("saved_address", fLoc)
                        .apply();

                updateProfileUi();
                dialog.dismiss();
                Toast.makeText(Main_Account.this, "Profile updated successfully! ✅", Toast.LENGTH_SHORT).show();
            });
        });

        dialog.show();
    }

    // ──────────────── Crop Tracking Section ────────────────
    private void loadCropCards() {
        cropRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot snapshot) {
                cropContainer.removeAllViews();

                if (!snapshot.exists() || snapshot.getChildrenCount() == 0) {
                    emptyCropsView.setVisibility(View.VISIBLE);
                    txtTotalCropsCount.setText("0 Crops");
                    return;
                }

                emptyCropsView.setVisibility(View.GONE);
                long totalCount = snapshot.getChildrenCount();
                txtTotalCropsCount.setText(totalCount + (totalCount == 1 ? " Crop" : " Crops"));

                for (DataSnapshot cropSnap : snapshot.getChildren()) {
                    String cropName = cropSnap.child("cropName").getValue(String.class);
                    String startDate = cropSnap.child("startDate").getValue(String.class);

                    if (cropName == null || cropName.isEmpty()) continue;

                    View card = getLayoutInflater().inflate(R.layout.item_crop_card, cropContainer, false);
                    ImageView img = card.findViewById(R.id.imgCrop);
                    TextView txtName = card.findViewById(R.id.txtCropName);
                    TextView txtDate = card.findViewById(R.id.txtCropDate);

                    txtName.setText(capitalize(cropName));
                    if (txtDate != null) {
                        txtDate.setText(startDate != null && !startDate.isEmpty() ? "Started: " + startDate : "Active Track");
                    }

                    // Dynamic icon mapping for all supported crops
                    String normalizedCrop = cropName.toLowerCase().trim();
                    if (normalizedCrop.contains("onion") || normalizedCrop.contains("pyaz") || normalizedCrop.contains("kanda")) {
                        img.setImageResource(R.drawable.onion);
                    } else if (normalizedCrop.contains("tomato") || normalizedCrop.contains("tamatar")) {
                        img.setImageResource(R.drawable.tomato);
                    } else if (normalizedCrop.contains("wheat") || normalizedCrop.contains("gehu")) {
                        img.setImageResource(R.drawable.wheat);
                    } else if (normalizedCrop.contains("potato") || normalizedCrop.contains("aloo")) {
                        img.setImageResource(R.drawable.potato);
                    } else if (normalizedCrop.contains("rice") || normalizedCrop.contains("paddy") || normalizedCrop.contains("chawal")) {
                        img.setImageResource(R.drawable.rice);
                    } else if (normalizedCrop.contains("maize") || normalizedCrop.contains("corn") || normalizedCrop.contains("makka")) {
                        img.setImageResource(R.drawable.maize);
                    } else if (normalizedCrop.contains("cotton") || normalizedCrop.contains("kapas")) {
                        img.setImageResource(R.drawable.cotton);
                    } else if (normalizedCrop.contains("soy") || normalizedCrop.contains("soya")) {
                        img.setImageResource(R.drawable.soybean);
                    } else if (normalizedCrop.contains("sugar") || normalizedCrop.contains("ganna")) {
                        img.setImageResource(R.drawable.sugarcane);
                    } else if (normalizedCrop.contains("chilli") || normalizedCrop.contains("chili") || normalizedCrop.contains("mirch")) {
                        img.setImageResource(R.drawable.chilli);
                    } else if (normalizedCrop.contains("brinjal") || normalizedCrop.contains("eggplant") || normalizedCrop.contains("baingan")) {
                        img.setImageResource(R.drawable.brinjal);
                    } else if (normalizedCrop.contains("groundnut") || normalizedCrop.contains("peanut") || normalizedCrop.contains("mungfali")) {
                        img.setImageResource(R.drawable.groundnut);
                    } else {
                        img.setImageResource(R.drawable.wheat);
                    }

                    card.setTag(cropName);
                    card.setOnClickListener(v -> {
                        String selected = (String) v.getTag();
                        Intent intent = new Intent(Main_Account.this, crop_actitvty.class);
                        intent.putExtra("cropName", selected);
                        intent.putExtra("email", email);
                        startActivity(intent);
                    });

                    cropContainer.addView(card);
                }
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
                Toast.makeText(Main_Account.this, "Failed to load crops", Toast.LENGTH_SHORT).show();
            }
        });
    }

    // ──────────────── Switch Account / Logout ────────────────
    private void performLogout() {
        new AlertDialog.Builder(this)
                .setTitle("Switch Account / Logout")
                .setMessage("Are you sure you want to log out? You can sign in to another account or create a new one.")
                .setPositiveButton("Logout", (dialog, which) -> {
                    FirebaseAuth.getInstance().signOut();
                    sessionSp.edit().clear().apply();

                    Intent intent = new Intent(Main_Account.this, LoginActivity.class);
                    intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                    startActivity(intent);
                    finish();
                    Toast.makeText(Main_Account.this, "Logged out successfully", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private String capitalize(String s) {
        if (s == null || s.isEmpty()) return s;
        return s.substring(0, 1).toUpperCase() + s.substring(1);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.account_toolbar, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.post_icon) {
            Intent intent = new Intent(this, post.class);
            intent.putExtra("email", email);
            startActivity(intent);
            return true;
        } else if (id == R.id.logout_icon) {
            performLogout();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
}
