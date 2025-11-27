package com.seattledevcamp.rainmaker

import android.app.Application
import com.seattledevcamp.rainmaker.di.appModule
import org.koin.android.ext.koin.androidContext
import org.koin.core.context.startKoin

class RainmakerApp : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@RainmakerApp)
            modules(appModule)
        }
    }
}

