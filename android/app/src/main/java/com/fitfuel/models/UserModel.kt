package com.fitfuel.models

import java.util.Date

data class UserData(
    val id: Int,
    val name: String,
    val email: String,
    val height: Int,
    val weight: Int,
    val gender: Gender,
    val activityLevel: ActivityLevel,
    val dateOfBirth: Date,
    val dietaryPreferences: List<String>,
    val mealStats: MealStats?
)

data class MealStats(
    val totalMeals: Int,
    val compliantMeals: Int,
    val averageCompliance: Double
)

data class Meal(
    val id: Int,
    val name: String,
    val ingredients: List<String>,
    val nutritionalInfo: NutritionalInfo,
    val preparationTime: Int,
    val difficulty: String,
    val mealType: String,
    val scheduledTime: Date
)

data class NutritionalInfo(
    val calories: Int,
    val protein: Double,
    val carbs: Double,
    val fat: Double
) 