package com.example.agribandhu.network.models;

import com.google.gson.annotations.SerializedName;

public class DiagnosisResponse {

    @SerializedName("status")
    private String status;

    @SerializedName("diagnosis")
    private DiagnosisDetail diagnosis;

    public String getStatus() {
        return status != null ? status : "";
    }

    public DiagnosisDetail getDiagnosis() {
        return diagnosis;
    }

    public static class DiagnosisDetail {
        @SerializedName("crop")
        private String crop;

        @SerializedName("disease_name")
        private String diseaseName;

        @SerializedName("confidence")
        private Integer confidence;

        @SerializedName("symptoms")
        private String symptoms;

        @SerializedName("immediate_action")
        private String immediateAction;

        @SerializedName("organic_treatment")
        private String organicTreatment;

        @SerializedName("chemical_treatment")
        private String chemicalTreatment;

        @SerializedName("prevention")
        private String prevention;

        @SerializedName("report")
        private String report;

        public String getCrop() {
            return crop != null ? crop : "";
        }

        public String getDiseaseName() {
            return diseaseName != null ? diseaseName : "";
        }

        public Integer getConfidence() {
            return confidence != null ? confidence : 0;
        }

        public String getSymptoms() {
            return symptoms != null ? symptoms : "";
        }

        public String getImmediateAction() {
            return immediateAction != null ? immediateAction : "";
        }

        public String getOrganicTreatment() {
            return organicTreatment != null ? organicTreatment : "";
        }

        public String getChemicalTreatment() {
            return chemicalTreatment != null ? chemicalTreatment : "";
        }

        public String getPrevention() {
            return prevention != null ? prevention : "";
        }

        public String getReport() {
            return report != null ? report : "";
        }
    }
}
