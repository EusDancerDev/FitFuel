import Foundation
import Combine

enum TimePeriod: String, CaseIterable, Identifiable {
    case week = "Week"
    case month = "Month"
    case year = "Year"
    
    var id: String { self.rawValue }
}

enum MetricType: String, CaseIterable, Identifiable {
    case compliance = "Compliance"
    case nutrition = "Nutrition"
    case timing = "Timing"
    case health = "Health"
    
    var id: String { self.rawValue }
}

enum TrendDirection {
    case improving
    case declining
    case stable
    case slightlyImproving
    case slightlyDeclining
    case insufficientData
}

struct MonthlyStats {
    let locationSummary: LocationSummary
    let skippedMeals: [String: Int]
    let averageSimilarity: [String: Double]
    let mealResults: [String: MealResult]
}

struct LocationSummary {
    let daysAtHome: Int
    let daysOutside: Int
}

struct MealResult {
    let passes: Int
    let fails: Int
}

class HistoricalRecordsViewModel: ObservableObject {
    @Published var averageCompliance: Double = 0.0
    @Published var consistencyScore: Double = 0.0
    @Published var complianceTrend: TrendDirection = .stable
    @Published var consistencyTrend: TrendDirection = .stable
    @Published var insights: [String] = []
    @Published var recommendations: [String] = []
    @Published var isLoading: Bool = false
    @Published var error: String?
    @Published var monthlyStats: MonthlyStats?
    
    private var cancellables = Set<AnyCancellable>()
    private let apiService: APIService
    
    init(apiService: APIService) {
        self.apiService = apiService
    }
    
    func loadData(period: TimePeriod) {
        isLoading = true
        
        let endDate = Date()
        let startDate: Date
        
        switch period {
        case .week:
            startDate = Calendar.current.date(byAdding: .day, value: -7, to: endDate)!
        case .month:
            startDate = Calendar.current.date(byAdding: .month, value: -1, to: endDate)!
        case .year:
            startDate = Calendar.current.date(byAdding: .year, value: -1, to: endDate)!
        }
        
        apiService.fetchHistoricalData(startDate: startDate, endDate: endDate)
            .receive(on: DispatchQueue.main)
            .sink { completion in
                self.isLoading = false
                if case .failure(let error) = completion {
                    self.error = error.localizedDescription
                }
            } receiveValue: { data in
                self.updateUI(with: data)
            }
            .store(in: &cancellables)
    }
    
    func chartData(for metric: MetricType) -> [ChartDataPoint] {
        // Implementation depends on the specific chart library being used
        switch metric {
        case .compliance:
            return complianceChartData
        case .nutrition:
            return nutritionChartData
        case .timing:
            return timingChartData
        case .health:
            return healthChartData
        }
    }
    
    private func updateUI(with data: HistoricalData) {
        averageCompliance = data.complianceTrends.overallCompliance
        consistencyScore = data.timingPatterns.consistencyScore
        complianceTrend = mapTrendDirection(data.complianceTrends.trend)
        consistencyTrend = mapTrendDirection(data.timingPatterns.trend)
        insights = generateInsights(from: data)
        recommendations = data.recommendations
        monthlyStats = data.monthlyStats
    }
    
    private func mapTrendDirection(_ trend: String) -> TrendDirection {
        switch trend {
        case "improving": return .improving
        case "declining": return .declining
        case "stable": return .stable
        case "slightly_improving": return .slightlyImproving
        case "slightly_declining": return .slightlyDeclining
        default: return .insufficientData
        }
    }
    
    private func generateInsights(from data: HistoricalData) -> [String] {
        var insights: [String] = []
        
        // Compliance insights
        if data.complianceTrends.overallCompliance > 80 {
            insights.append("Great job maintaining high compliance!")
        }
        
        // Nutritional insights
        if let nutritionalGaps = data.nutritionalTrends.gaps.first {
            insights.append("Consider increasing \(nutritionalGaps.nutrient) intake")
        }
        
        // Timing insights
        if data.timingPatterns.consistencyScore > 0.8 {
            insights.append("Excellent meal timing consistency")
        }
        
        // Health correlation insights
        if let bestMeal = data.healthCorrelations.energyLevels.max(by: { $0.value < $1.value }) {
            insights.append("\(bestMeal.key) has the most positive impact on your energy")
        }
        
        return insights
    }
} 