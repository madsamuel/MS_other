package com.seattledevcamp.rainmaker.di

import androidx.media3.exoplayer.ExoPlayer
import androidx.room.Room
import com.seattledevcamp.rainmaker.audio.RainAudioEngine
import com.seattledevcamp.rainmaker.data.local.RainmakerDatabase
import com.seattledevcamp.rainmaker.data.repository.RecordingRepository
import com.seattledevcamp.rainmaker.domain.DeleteRecordingUseCase
import com.seattledevcamp.rainmaker.domain.GenerateRainSoundUseCase
import com.seattledevcamp.rainmaker.domain.ObserveRecordingsUseCase
import com.seattledevcamp.rainmaker.ui.generator.GeneratorViewModel
import com.seattledevcamp.rainmaker.ui.library.LibraryViewModel
import com.seattledevcamp.rainmaker.ui.library.RainPlayer
import org.koin.androidx.viewmodel.dsl.viewModel
import org.koin.dsl.module

val appModule = module {
    single {
        Room.databaseBuilder(
            get(),
            RainmakerDatabase::class.java,
            "rainmaker.db"
        ).build()
    }

    single { get<RainmakerDatabase>().recordingDao() }

    single { RecordingRepository(get()) }

    // Provide a ModelAudioEngine implementation. Replace the asset name with your .tflite model in assets/.
    single { com.seattledevcamp.rainmaker.audio.model.TfliteModelEngine("rain_model.tflite") as com.seattledevcamp.rainmaker.audio.model.ModelAudioEngine }

    single { RainAudioEngine(get(), get()) }

    single { ExoPlayer.Builder(get()).build() }

    single { RainPlayer(get()) }

    factory { GenerateRainSoundUseCase(get(), get()) }
    factory { ObserveRecordingsUseCase(get()) }
    factory { DeleteRecordingUseCase(get()) }

    viewModel { GeneratorViewModel(get()) }
    viewModel { LibraryViewModel(get(), get(), get()) }
}
