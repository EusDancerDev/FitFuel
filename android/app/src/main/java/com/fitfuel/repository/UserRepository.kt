package com.fitfuel.repository

import com.fitfuel.network.ApiService
import com.fitfuel.network.models.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class UserRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun login(email: String, password: String): LoginResponse {
        return apiService.login(LoginRequest(email, password))
    }
    
    suspend fun register(request: RegisterRequest): RegisterResponse {
        return apiService.register(request)
    }
    
    suspend fun getMenu(): MenuResponse {
        return apiService.getMenu()
    }
    
    suspend fun generateMenu(preferences: MenuPreferences): MenuResponse {
        return apiService.generateMenu(preferences)
    }
    
    suspend fun getStatistics(): StatisticsResponse {
        return apiService.getStatistics()
    }
    
    suspend fun syncWatchData(data: WatchData): SyncResponse {
        return apiService.syncWatchData(data)
    }
} 