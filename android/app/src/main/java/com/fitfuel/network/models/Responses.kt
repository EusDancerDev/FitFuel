package com.fitfuel.network.models

data class LoginResponse(
    val token: String,
    val user: UserData
)

data class RegisterResponse(
    val token: String,
    val user: UserData
)

data class MenuResponse(
    val meals: List<Meal>,
    val generatedAt: String,
    val validUntil: String
)

data class StatisticsResponse(
    val monthlyStats: MonthlyStats,
    val insights: List<Insight>,
    val recommendations: List<Recommendation>
)

data class SyncResponse(
    val success: Boolean,
    val syncedAt: String,
    val summary: ActivitySummary
) 