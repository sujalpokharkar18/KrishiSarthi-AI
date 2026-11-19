package com.example.agribandhu;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.ArrayList;
import java.util.List;

public class scheme_actitvy extends AppCompatActivity {

    private EditText editTextDate;
    private Button btnFetchScheme, btnViewAllSchemes;
    private ProgressBar schemeProgressBar;
    private LinearLayout schemeContainer;

    private DatabaseReference dbRef;

    // Verified Agricultural Schemes for instant display / offline fallback
    private static class SchemeItem {
        String name;
        String details;
        SchemeItem(String name, String details) {
            this.name = name;
            this.details = details;
        }
    }

    private final List<SchemeItem> verifiedSchemes = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_scheme_actitvy);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }
        toolbar.setNavigationOnClickListener(v -> finish());

        editTextDate = findViewById(R.id.editTextdate);
        btnFetchScheme = findViewById(R.id.btnfetchscheme);
        btnViewAllSchemes = findViewById(R.id.btnViewAllSchemes);
        schemeProgressBar = findViewById(R.id.schemeProgressBar);
        schemeContainer = findViewById(R.id.schemeContainer);

        initVerifiedSchemes();

        dbRef = FirebaseDatabase.getInstance().getReference("schemes");

        // Search by specific date
        btnFetchScheme.setOnClickListener(v -> {
            String date = editTextDate.getText().toString().trim();
            if (date.isEmpty()) {
                fetchAndDisplayAllSchemes();
            } else {
                fetchSchemeByDate(date);
            }
        });

        // Browse all schemes button
        btnViewAllSchemes.setOnClickListener(v -> fetchAndDisplayAllSchemes());

        // Display default verified schemes on first load so screen is never blank!
        displaySchemesList(verifiedSchemes, "Active Central & State Agricultural Initiatives");
    }

    private void initVerifiedSchemes() {
        verifiedSchemes.add(new SchemeItem(
                "PM-KISAN Samman Nidhi",
                "Direct income support of ₹6,000 per year in three equal four-monthly installments to all landholding farmer families across India via DBT."
        ));
        verifiedSchemes.add(new SchemeItem(
                "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                "Comprehensive crop insurance coverage against non-preventable natural risks (drought, flood, unseasonal rain, pests) from pre-sowing to post-harvest. Farmer premium: 1.5% - 2%."
        ));
        verifiedSchemes.add(new SchemeItem(
                "Soil Health Card Scheme",
                "Free periodic soil testing (every 3 years) assessing 12 parameters with customized crop-wise fertilizer recommendations to lower cultivation costs."
        ));
        verifiedSchemes.add(new SchemeItem(
                "Kisan Credit Card (KCC)",
                "Low-interest short-term credit (up to ₹3 Lakh at 4% effective interest upon timely repayment) for cultivation expenses, crop inputs, and post-harvest maintenance."
        ));
        verifiedSchemes.add(new SchemeItem(
                "PM Krishi Sinchayee Yojana (Per Drop More Crop)",
                "Financial subsidy up to 55% for small & marginal farmers to install water-efficient drip and sprinkler micro-irrigation systems."
        ));
        verifiedSchemes.add(new SchemeItem(
                "Paramparagat Krishi Vikas Yojana (PKVY)",
                "Financial assistance of ₹50,000 per hectare for 3 years to adopt organic farming practices, cluster certification, and organic value chain marketing."
        ));
    }

    private void fetchSchemeByDate(String date) {
        if (schemeProgressBar != null) schemeProgressBar.setVisibility(View.VISIBLE);

        dbRef.child(date).addListenerForSingleValueEvent(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot snapshot) {
                if (schemeProgressBar != null) schemeProgressBar.setVisibility(View.GONE);

                List<SchemeItem> results = new ArrayList<>();
                if (snapshot.exists()) {
                    for (DataSnapshot schemeSnap : snapshot.getChildren()) {
                        String name = schemeSnap.child("Name").getValue(String.class);
                        if (name == null) name = schemeSnap.child("name").getValue(String.class);

                        String details = schemeSnap.child("Details").getValue(String.class);
                        if (details == null) details = schemeSnap.child("details").getValue(String.class);

                        if (name != null) {
                            results.add(new SchemeItem(name, details != null ? details : ""));
                        }
                    }
                }

                if (!results.isEmpty()) {
                    displaySchemesList(results, "Schemes Announced on " + date);
                } else {
                    Toast.makeText(scheme_actitvy.this, "No schemes recorded for " + date + ". Showing active initiatives:", Toast.LENGTH_LONG).show();
                    displaySchemesList(verifiedSchemes, "Active Initiatives (No specific updates for " + date + ")");
                }
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
                if (schemeProgressBar != null) schemeProgressBar.setVisibility(View.GONE);
                Toast.makeText(scheme_actitvy.this, "Network error: " + error.getMessage(), Toast.LENGTH_SHORT).show();
                displaySchemesList(verifiedSchemes, "Active Initiatives (Offline Mode)");
            }
        });
    }

    private void fetchAndDisplayAllSchemes() {
        if (schemeProgressBar != null) schemeProgressBar.setVisibility(View.VISIBLE);

        dbRef.addListenerForSingleValueEvent(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot snapshot) {
                if (schemeProgressBar != null) schemeProgressBar.setVisibility(View.GONE);

                List<SchemeItem> results = new ArrayList<>();
                if (snapshot.exists()) {
                    for (DataSnapshot dateSnap : snapshot.getChildren()) {
                        for (DataSnapshot schemeSnap : dateSnap.getChildren()) {
                            String name = schemeSnap.child("Name").getValue(String.class);
                            if (name == null) name = schemeSnap.child("name").getValue(String.class);

                            String details = schemeSnap.child("Details").getValue(String.class);
                            if (details == null) details = schemeSnap.child("details").getValue(String.class);

                            if (name != null) {
                                results.add(new SchemeItem(name, details != null ? details : ""));
                            }
                        }
                    }
                }

                if (!results.isEmpty()) {
                    displaySchemesList(results, "All Registered Schemes (" + results.size() + ")");
                } else {
                    displaySchemesList(verifiedSchemes, "All Active Government Schemes (" + verifiedSchemes.size() + ")");
                }
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
                if (schemeProgressBar != null) schemeProgressBar.setVisibility(View.GONE);
                displaySchemesList(verifiedSchemes, "Government Schemes (Offline Mode)");
            }
        });
    }

    private void displaySchemesList(List<SchemeItem> list, String headerTitle) {
        schemeContainer.removeAllViews();

        TextView tvHeader = new TextView(this);
        tvHeader.setText(headerTitle);
        tvHeader.setTextSize(16f);
        tvHeader.setTextColor(getResources().getColor(android.R.color.holo_green_dark));
        tvHeader.setPadding(16, 8, 16, 8);
        schemeContainer.addView(tvHeader);

        for (SchemeItem item : list) {
            View cardView = getLayoutInflater().inflate(R.layout.scheme_card, schemeContainer, false);
            TextView tvName = cardView.findViewById(R.id.tvSchemeName);
            TextView tvDetails = cardView.findViewById(R.id.tvSchemeDetails);

            tvName.setText(item.name);
            tvDetails.setText(item.details);

            schemeContainer.addView(cardView);
        }
    }
}