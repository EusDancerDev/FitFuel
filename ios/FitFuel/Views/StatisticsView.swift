import SwiftUI
import Charts

struct StatisticsView: View {
    @StateObject private var viewModel = StatisticsViewModel()
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Monthly Stats Card
                    MonthlyStatsCard(stats: viewModel.monthlyStats)
                    
                    // Insights Section
                    InsightsSection(
                        insights: viewModel.insights,
                        onInsightTapped: viewModel.onInsightClicked
                    )
                    
                    // Recommendations Section
                    RecommendationsSection(
                        recommendations: viewModel.recommendations,
                        onRecommendationApplied: viewModel.onRecommendationApplied
                    )
                }
                .padding()
            }
            .navigationTitle("Statistics")
            .refreshable {
                await viewModel.refreshData()
            }
            .overlay {
                if viewModel.isLoading {
                    ProgressView()
                        .scaleEffect(1.5)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .background(Color.black.opacity(0.2))
                }
            }
            .alert("Error", isPresented: $viewModel.showError) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage)
            }
        }
    }
}

private struct MonthlyStatsCard: View {
    let stats: MonthlyStats
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Monthly Statistics")
                .font(.headline)
            
            VStack(alignment: .leading, spacing: 8) {
                StatRow(
                    label: "Days at Home",
                    value: "\(stats.locationSummary.daysAtHome)"
                )
                
                StatRow(
                    label: "Days Outside",
                    value: "\(stats.locationSummary.daysOutside)"
                )
                
                StatRow(
                    label: "Skipped Meals",
                    value: formatSkippedMeals(stats.skippedMeals)
                )
                
                StatRow(
                    label: "Average Similarity",
                    value: formatSimilarityPercentages(stats.averageSimilarity)
                )
                
                StatRow(
                    label: "Pass/Fail Ratio",
                    value: formatPassFailStats(stats.mealResults)
                )
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
    
    private func formatSkippedMeals(_ meals: [String: Int]) -> String {
        meals.map { "\($0.key) (\($0.value))" }.joined(separator: ", ")
    }
    
    private func formatSimilarityPercentages(_ similarities: [String: Double]) -> String {
        similarities.map { 
            "\($0.key) (\(String(format: "%.1f", $0.value))%)" 
        }.joined(separator: ", ")
    }
    
    private func formatPassFailStats(_ results: [String: MealResult]) -> String {
        results.map { 
            "\($0.key) (\($0.value.passes)/\($0.value.fails))" 
        }.joined(separator: ", ")
    }
}

private struct StatRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .foregroundColor(.secondary)
            Spacer()
            Text(value)
                .bold()
        }
    }
}

private struct InsightsSection: View {
    let insights: [Insight]
    let onInsightTapped: (Insight) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Insights")
                .font(.headline)
            
            ForEach(insights) { insight in
                InsightRow(insight: insight)
                    .onTapGesture {
                        onInsightTapped(insight)
                    }
            }
        }
    }
}

private struct RecommendationsSection: View {
    let recommendations: [Recommendation]
    let onRecommendationApplied: (Recommendation) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recommendations")
                .font(.headline)
            
            ForEach(recommendations) { recommendation in
                RecommendationRow(
                    recommendation: recommendation,
                    onApply: {
                        onRecommendationApplied(recommendation)
                    }
                )
            }
        }
    }
}

#Preview {
    StatisticsView()
} 