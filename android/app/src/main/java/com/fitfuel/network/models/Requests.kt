package com.fitfuel.network.models

data class LoginRequest(
    val email: String,
    val password: String
)

data class RegisterRequest(
    val email: String,
    val password: String,
    val name: String,
    val height: Int,
    val weight: Int,
    val gender: String,
    val activityLevel: String,
    val dateOfBirth: String,
    val dietaryPreferences: List<String>
)

data class MenuPreferences(
    val mealTypes: List<String>,
    val excludeIngredients: List<String>,
    val calorieRange: Range,
    val proteinRange: Range
)

data class Range(
    val min: Int,
    val max: Int
) 