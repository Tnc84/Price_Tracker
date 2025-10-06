package com.ro.pricetracker

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * Application class for Romanian Price Tracker
 * 
 * @HiltAndroidApp triggers Hilt's code generation for dependency injection
 */
@HiltAndroidApp
class PriceTrackerApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // Application initialization
    }
}

