import Foundation

// Request Models
struct LoginRequest: Encodable {
    let email: String
    let password: String
}

struct RegisterRequest: Encodable {
    let email: String
    let password: String
    let name: String
    let height: Int
    let weight: Int
    let gender: String
    let activityLevel: String
    let dateOfBirth: String
    let dietaryPreferences: [String]
}

struct MenuPreferences: Encodable {
    let mealTypes: [String]
    let excludeIngredients: [String]
    let calorieRange: Range
    let proteinRange: Range
}

struct Range: Encodable {
    let min: Int
    let max: Int
}

// Response Models
struct LoginResponse: Decodable {
    let token: String
    let user: UserData
}

struct RegisterResponse: Decodable {
    let token: String
    let user: UserData
}

struct MenuResponse: Decodable {
    let meals: [Meal]
    let generatedAt: String
    let validUntil: String
}

struct StatisticsResponse: Decodable {
    let monthlyStats: MonthlyStats
    let insights: [Insight]
    let recommendations: [Recommendation]
}

struct SyncResponse: Decodable {
    let success: Bool
    let syncedAt: String
    let summary: ActivitySummary
} 