plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.madsamuel.youtube3x"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.madsamuel.youtube3x"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.10.1")
    implementation("androidx.activity:activity-ktx:1.8.0")
    testImplementation("junit:junit:4.13.2")
}
