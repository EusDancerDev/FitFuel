package com.fitfuel.network

import com.fitfuel.models.*
import retrofit2.http.*

interface ApiService {
    @POST("auth/login")
    suspend fun login(@Body credentials: LoginRequest): LoginResponse
    
    @POST("auth/register")
    suspend fun register(@Body userData: RegisterRequest): RegisterResponse
    
    @GET("menu")
    suspend fun getMenu(): MenuResponse
    
    @POST("menu/generate")
    suspend fun generateMenu(@Body preferences: MenuPreferences): MenuResponse
    
    @GET("statistics")
    suspend fun getStatistics(): StatisticsResponse
    
    @POST("watch-data/sync")
    suspend fun syncWatchData(@Body data: WatchData): SyncResponse
} 