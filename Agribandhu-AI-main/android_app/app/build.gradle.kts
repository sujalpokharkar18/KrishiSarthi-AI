plugins {
    alias(libs.plugins.android.application)
    id("com.google.gms.google-services")
}

android {
    namespace = "com.example.agribandhu"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.example.agribandhu"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        // Stable HTTP/2 Public HTTPS backend URL
        buildConfigField(
            "String",
            "BACKEND_BASE_URL",
            "\"https://give-memo-foundation-semi.trycloudflare.com/\""
        )

        buildConfigField(
            "String",
            "WEATHER_API_KEY",
            "\"CZ8VZ5PCCXU7RHHSYR4GT2QK9\""
        )

        buildConfigField(
            "String",
            "LOCATIONIQ_API_KEY",
            "\"pk.84838c131bfac08c74fb98c5c37aee00\""
        )

        buildConfigField(
            "String",
            "GEMINI_API_KEY",
            "\"AIzaSyAIJUcZHRLKhR1QcYgfrJUp_eH8L_zmkKM\""
        )
    }

    buildFeatures {
        buildConfig = true
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    implementation(libs.appcompat)
    implementation(libs.material)
    implementation(libs.activity)
    implementation(libs.constraintlayout)

    // Firebase BOM and managed services
    implementation(platform("com.google.firebase:firebase-bom:33.8.0"))
    implementation("com.google.firebase:firebase-analytics")
    implementation("com.google.firebase:firebase-auth")
    implementation("com.google.firebase:firebase-database")
    implementation("com.google.firebase:firebase-storage")

    // Networking & JSON
    implementation("com.squareup.okhttp3:okhttp:5.2.1")
    implementation("com.google.code.gson:gson:2.13.2")
    implementation("com.squareup.retrofit2:retrofit:2.11.0")
    implementation("com.squareup.retrofit2:converter-gson:2.11.0")

    // Image Loading
    implementation("com.github.bumptech.glide:glide:4.16.0")

    // Chart library for graphs
    implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")
    testImplementation(libs.junit)
    androidTestImplementation(libs.ext.junit)
    androidTestImplementation(libs.espresso.core)
}
