import Foundation

struct UserData: Codable {
    let id: Int
    let name: String
    let email: String
    let height: Int
    let weight: Int
    let gender: Gender
    let activityLevel: ActivityLevel
    let dateOfBirth: Date
    let dietaryPreferences: [String]
    let mealStats: MealStats?
    
    struct MealStats: Codable {
        let totalMeals: Int
        let compliantMeals: Int
        let averageCompliance: Double
    }
}

struct Meal: Codable, Identifiable {
    let id: Int
    let name: String
    let ingredients: [String]
    let nutritionalInfo: NutritionalInfo
    let preparationTime: Int
    let difficulty: String
    let mealType: String
    let scheduledTime: Date
    
    struct NutritionalInfo: Codable {
        let calories: Int
        let protein: Double
        let carbs: Double
        let fat: Double
    }
} 