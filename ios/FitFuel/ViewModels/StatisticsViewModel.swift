import Foundation
import Combine

class StatisticsViewModel: ObservableObject {
    @Published var monthlyStats: MonthlyStats?
    @Published var insights: [Insight] = []
    @Published var recommendations: [Recommendation] = []
    @Published var isLoading = false
    @Published var error: String?
    
    private var cancellables = Set<AnyCancellable>()
    private let statisticsService: StatisticsService
    
    init(statisticsService: StatisticsService = StatisticsService()) {
        self.statisticsService = statisticsService
        loadStatistics()
    }
    
    func loadStatistics() {
        isLoading = true
        
        statisticsService.getStatistics()
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isLoading = false
                if case .failure(let error) = completion {
                    self?.error = error.localizedDescription
                }
            } receiveValue: { [weak self] data in
                self?.monthlyStats = data.monthlyStats
                self?.insights = data.insights
                self?.recommendations = data.recommendations
            }
            .store(in: &cancellables)
    }
    
    func onInsightClicked(_ insight: Insight) {
        statisticsService.markInsightAsRead(insight.id)
            .receive(on: DispatchQueue.main)
            .sink { completion in
                // Handle completion
            } receiveValue: { [weak self] _ in
                self?.loadStatistics()
            }
            .store(in: &cancellables)
    }
} 