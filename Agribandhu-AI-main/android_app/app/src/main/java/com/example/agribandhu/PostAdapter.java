package com.example.agribandhu;

import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.util.Base64;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageReference;

import java.util.List;

public class PostAdapter extends RecyclerView.Adapter<PostAdapter.ViewHolder> {

    private final Context context;
    private final List<PostModel> postList;
    private String currentUserEmail;

    public PostAdapter(Context context, List<PostModel> postList) {
        this(context, postList, null);
    }

    public PostAdapter(Context context, List<PostModel> postList, String currentUserEmail) {
        this.context = context;
        this.postList = postList;
        this.currentUserEmail = currentUserEmail;

        if (this.currentUserEmail == null || this.currentUserEmail.isEmpty()) {
            if (FirebaseAuth.getInstance().getCurrentUser() != null && FirebaseAuth.getInstance().getCurrentUser().getEmail() != null) {
                this.currentUserEmail = FirebaseAuth.getInstance().getCurrentUser().getEmail();
            }
        }
        if (this.currentUserEmail == null || this.currentUserEmail.isEmpty()) {
            SharedPreferences sp = context.getSharedPreferences("AgriBandhuSession", Context.MODE_PRIVATE);
            this.currentUserEmail = sp.getString("saved_email", "farmer@krishisarthi.com");
        }
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.post_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        PostModel post = postList.get(position);
        holder.farmerName.setText(post.getFarmerName());
        holder.description.setText(post.getDescription());

        String imageData = post.getImageUri();

        if (imageData != null && !imageData.isEmpty()) {
            try {
                // 1. Remote HTTP/HTTPS URL (Firebase Storage) -> Load via Glide
                if (imageData.startsWith("http://") || imageData.startsWith("https://")) {
                    Glide.with(context)
                            .load(imageData)
                            .placeholder(android.R.drawable.ic_menu_gallery)
                            .error(android.R.drawable.ic_menu_report_image)
                            .centerCrop()
                            .into(holder.imageView);

                // 2. Local content or file URI
                } else if (imageData.startsWith("content://") || imageData.startsWith("file://")) {
                    holder.imageView.setImageURI(Uri.parse(imageData));

                // 3. Backwards compatibility: Decode legacy Base64 string
                } else {
                    byte[] decodedBytes = Base64.decode(imageData, Base64.DEFAULT);
                    Bitmap decodedBitmap = BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
                    if (decodedBitmap != null) {
                        holder.imageView.setImageBitmap(decodedBitmap);
                    } else {
                        holder.imageView.setImageResource(android.R.drawable.ic_menu_gallery);
                    }
                }
            } catch (Exception e) {
                e.printStackTrace();
                holder.imageView.setImageResource(android.R.drawable.ic_menu_gallery);
            }
        } else {
            holder.imageView.setImageResource(android.R.drawable.ic_menu_gallery);
        }

        // Consult AI Doctor Button
        if (holder.btnAskAiPost != null) {
            holder.btnAskAiPost.setOnClickListener(v -> {
                Intent chatIntent = new Intent(context, Ai_chat.class);
                chatIntent.putExtra("image_uri", post.getImageUri());
                String snippet = post.getDescription() != null ? post.getDescription() : "";
                chatIntent.putExtra("diagnosis_report", "Crop observation from " + post.getFarmerName() + ":\n" + snippet);
                context.startActivity(chatIntent);
            });
        }

        // Delete Post Button: Visible if user owns the post or if active logged in user
        boolean isOwner = post.isOwnedBy(currentUserEmail);
        if (isOwner || (currentUserEmail != null && !currentUserEmail.isEmpty())) {
            holder.btnDeletePost.setVisibility(View.VISIBLE);
            holder.btnDeletePost.setOnClickListener(v -> confirmDeletePost(post, holder.getBindingAdapterPosition()));
        } else {
            holder.btnDeletePost.setVisibility(View.GONE);
        }
    }

    private void confirmDeletePost(PostModel post, int position) {
        new AlertDialog.Builder(context)
                .setTitle("🗑️ Delete Post")
                .setMessage("Are you sure you want to remove this post from the community feed?")
                .setPositiveButton("Delete", (dialog, which) -> deletePostFromFirebase(post, position))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void deletePostFromFirebase(PostModel post, int position) {
        String userKey = post.getUserKey();
        String postId = post.getPostId();

        if (userKey.isEmpty() && currentUserEmail != null) {
            userKey = currentUserEmail.replace(".", "_");
        }

        if (!userKey.isEmpty() && !postId.isEmpty()) {
            DatabaseReference postRef = FirebaseDatabase.getInstance()
                    .getReference("users")
                    .child(userKey)
                    .child("post")
                    .child(postId);

            postRef.removeValue().addOnSuccessListener(aVoid -> {
                removePostFromList(position);
                Toast.makeText(context, "✅ Post deleted successfully!", Toast.LENGTH_SHORT).show();

                // Delete image from Firebase Storage if applicable
                String imgUri = post.getImageUri();
                if (imgUri != null && imgUri.startsWith("https://firebasestorage.googleapis.com")) {
                    try {
                        StorageReference storageRef = FirebaseStorage.getInstance().getReferenceFromUrl(imgUri);
                        storageRef.delete();
                    } catch (Exception ignored) {}
                }
            }).addOnFailureListener(e -> {
                Toast.makeText(context, "Failed to delete post: " + e.getMessage(), Toast.LENGTH_SHORT).show();
            });
        } else {
            removePostFromList(position);
            Toast.makeText(context, "Post removed from list.", Toast.LENGTH_SHORT).show();
        }
    }

    private void removePostFromList(int position) {
        if (position >= 0 && position < postList.size()) {
            postList.remove(position);
            notifyItemRemoved(position);
            notifyItemRangeChanged(position, postList.size());
        }
    }

    @Override
    public int getItemCount() {
        return postList.size();
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView farmerName, description;
        ImageView imageView;
        Button btnAskAiPost;
        ImageButton btnDeletePost;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            farmerName = itemView.findViewById(R.id.farmerName);
            description = itemView.findViewById(R.id.postDescription);
            imageView = itemView.findViewById(R.id.postImage);
            btnAskAiPost = itemView.findViewById(R.id.btnAskAiPost);
            btnDeletePost = itemView.findViewById(R.id.btnDeletePost);
        }
    }
}
