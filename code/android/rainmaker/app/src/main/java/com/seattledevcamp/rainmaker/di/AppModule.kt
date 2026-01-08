package com.seattledevcamp.rainmaker.di

import android.app.Application
import android.content.Context
import androidx.media3.exoplayer.ExoPlayer
import androidx.room.Room
import com.seattledevcamp.rainmaker.GeneratorViewModel
import com.seattledevcamp.rainmaker.audio.RainAudioEngine
import com.seattledevcamp.rainmaker.audio.model.TfliteModelEngine
import com.seattledevcamp.rainmaker.audio.model.ModelAudioEngine
import com.seattledevcamp.rainmaker.data.local.RainmakerDatabase
import com.seattledevcamp.rainmaker.data.repository.RecordingRepository
import com.seattledevcamp.rainmaker.domain.DeleteRecordingUseCase
import com.seattledevcamp.rainmaker.domain.GenerateRainSoundUseCase
import com.seattledevcamp.rainmaker.domain.ObserveRecordingsUseCase
import com.seattledevcamp.rainmaker.ui.library.LibraryViewModel
import com.seattledevcamp.rainmaker.ui.library.RainPlayer
import org.koin.androidx.viewmodel.dsl.viewModel
import org.koin.dsl.module

val appModule = module {
    single {
        Room.databaseBuilder(
            get<Context>(),
            RainmakerDatabase::class.java,
            "rainmaker.db"
        ).build()
    }

    single { get<RainmakerDatabase>().recordingDao() }

    single { RecordingRepository(get()) }

    // Bind ModelAudioEngine to the TfliteModelEngine that will load rain_model.tflite from assets
    single<ModelAudioEngine> { TfliteModelEngine("rain_model.tflite") }

    // RainAudioEngine needs a Context and a ModelAudioEngine; make get() types explicit so Koin can resolve them
    single { RainAudioEngine(get<Context>(), get<ModelAudioEngine>()) }

    single { ExoPlayer.Builder(get<Context>()).build() }

    single { RainPlayer(get()) }

    factory { GenerateRainSoundUseCase(get(), get()) }
    factory { ObserveRecordingsUseCase(get()) }
    factory { DeleteRecordingUseCase(get()) }

    // Provide GeneratorViewModel (AndroidViewModel in root package) with injected Application and RainAudioEngine
    viewModel { GeneratorViewModel(get<Application>(), get()) }
    viewModel { LibraryViewModel(get(), get(), get()) }
}
