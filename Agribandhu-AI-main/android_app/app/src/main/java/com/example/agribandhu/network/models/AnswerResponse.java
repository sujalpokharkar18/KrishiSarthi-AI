package com.example.agribandhu.network.models;

import com.google.gson.annotations.SerializedName;

public class AnswerResponse {

    @SerializedName("reply")
    private String reply;

    @SerializedName("answer")
    private String answer;

    @SerializedName("label")
    private String label;

    @SerializedName("confidence")
    private Double confidence;

    @SerializedName("question")
    private String question;

    public String getReply() {
        if (reply != null && !reply.isEmpty()) {
            return reply;
        }
        return answer != null ? answer : "";
    }

    public String getAnswer() {
        return getReply();
    }

    public String getLabel() {
        return label != null ? label : "";
    }

    public Double getConfidence() {
        return confidence != null ? confidence : 0.0;
    }

    public String getQuestion() {
        return question != null ? question : "";
    }
}
