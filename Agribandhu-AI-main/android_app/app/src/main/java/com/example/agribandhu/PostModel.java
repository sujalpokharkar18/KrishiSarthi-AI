package com.example.agribandhu;

public class PostModel {
    private String farmerName;
    private String description;
    private String imageUri;
    private String postId;
    private String userKey;
    private String userEmail;

    public PostModel() {}

    public PostModel(String farmerName, String description, String imageUri) {
        this.farmerName = farmerName;
        this.description = description;
        this.imageUri = imageUri;
        this.postId = "";
        this.userKey = "";
        this.userEmail = "";
    }

    public PostModel(String farmerName, String description, String imageUri, String postId, String userKey, String userEmail) {
        this.farmerName = farmerName;
        this.description = description;
        this.imageUri = imageUri;
        this.postId = postId != null ? postId : "";
        this.userKey = userKey != null ? userKey : "";
        this.userEmail = userEmail != null ? userEmail : "";
    }

    public String getFarmerName() {
        return farmerName != null ? farmerName : "";
    }

    public String getDescription() {
        return description != null ? description : "";
    }

    public String getImageUri() {
        return imageUri != null ? imageUri : "";
    }

    public String getPostId() {
        return postId != null ? postId : "";
    }

    public String getUserKey() {
        return userKey != null ? userKey : "";
    }

    public String getUserEmail() {
        return userEmail != null ? userEmail : "";
    }

    public boolean isOwnedBy(String email) {
        if (email == null || email.isEmpty()) return false;
        String normalizedEmail = email.trim().toLowerCase();
        String normalizedUserKey = normalizedEmail.replace(".", "_");
        String authorPrefix = normalizedEmail.split("@")[0];

        if (this.userEmail != null && this.userEmail.trim().equalsIgnoreCase(normalizedEmail)) {
            return true;
        }
        if (this.userKey != null && this.userKey.trim().equalsIgnoreCase(normalizedUserKey)) {
            return true;
        }
        if (this.farmerName != null && this.farmerName.trim().equalsIgnoreCase(authorPrefix)) {
            return true;
        }
        return false;
    }
}
