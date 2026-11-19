package com.example.agribandhu.network.models;

import com.google.gson.annotations.SerializedName;

public class DiagnosisRequest {
    @SerializedName("image_base64")
    private String imageBase64;

    @SerializedName("crop_name")
    private String cropName;

    @SerializedName("notes")
    private String notes;

    public DiagnosisRequest(String imageBase64, String cropName, String notes) {
        this.imageBase64 = imageBase64 != null ? imageBase64 : "";
        this.cropName = cropName != null ? cropName : "";
        this.notes = notes != null ? notes : "";
    }

    public String getImageBase64() { return imageBase64; }
    public void setImageBase64(String imageBase64) { this.imageBase64 = imageBase64; }

    public String getCropName() { return cropName; }
    public void setCropName(String cropName) { this.cropName = cropName; }

    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }
}
