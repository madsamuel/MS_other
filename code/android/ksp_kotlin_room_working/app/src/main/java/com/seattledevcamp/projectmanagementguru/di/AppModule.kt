// app/src/main/java/com/seattledevcamp/projectmanagementguru/di/AppModule.kt
package com.seattledevcamp.projectmanagementguru.di

import android.content.Context
import androidx.room.Room
import com.seattledevcamp.projectmanagementguru.data.AppDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "project_management_db")
            .fallbackToDestructiveMigration()
            .build()

    @Provides
    fun provideLessonDao(db: AppDatabase) = db.lessonDao()

    @Provides
    fun provideTopicDao(db: AppDatabase) = db.topicDao()

    @Provides
    fun provideQuestionDao(db: AppDatabase) = db.questionDao()
}
