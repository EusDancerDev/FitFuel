import SwiftUI
import Charts

struct HistoricalRecordsView: View {
    @ObservedObject var viewModel: HistoricalRecordsViewModel
    @State private var selectedPeriod: TimePeriod = .week
    @State private var selectedMetric: MetricType = .compliance
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Period Selection
                    Picker("Time Period", selection: $selectedPeriod) {
                        ForEach(TimePeriod.allCases) { period in
                            Text(period.rawValue).tag(period)
                        }
                    }
                    .pickerStyle(SegmentedPickerStyle())
                    .padding()
                    
                    // Metric Selection
                    Picker("Metric", selection: $selectedMetric) {
                        ForEach(MetricType.allCases) { metric in
                            Text(metric.rawValue).tag(metric)
                        }
                    }
                    .pickerStyle(SegmentedPickerStyle())
                    .padding(.horizontal)
                    
                    // Main Chart
                    ChartView(data: viewModel.chartData(for: selectedMetric))
                        .frame(height: 250)
                        .padding()
                    
                    // Statistics Cards
                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 16) {
                        StatCard(
                            title: "Compliance",
                            value: viewModel.averageCompliance,
                            trend: viewModel.complianceTrend
                        )
                        StatCard(
                            title: "Consistency",
                            value: viewModel.consistencyScore,
                            trend: viewModel.consistencyTrend
                        )
                    }
                    .padding()
                    
                    // Insights Section
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Insights")
                            .font(.headline)
                        
                        ForEach(viewModel.insights, id: \.self) { insight in
                            InsightRow(insight: insight)
                        }
                    }
                    .padding()
                    
                    // Recommendations
                    if !viewModel.recommendations.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Recommendations")
                                .font(.headline)
                            
                            ForEach(viewModel.recommendations, id: \.self) { recommendation in
                                RecommendationRow(recommendation: recommendation)
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("Historical Records")
            .onAppear {
                viewModel.loadData(period: selectedPeriod)
            }
            .onChange(of: selectedPeriod) { newPeriod in
                viewModel.loadData(period: newPeriod)
            }
        }
    }
}

struct StatCard: View {
    let title: String
    let value: Double
    let trend: TrendDirection
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            HStack(alignment: .bottom) {
                Text(String(format: "%.1f%%", value))
                    .font(.title2)
                    .bold()
                
                TrendIndicator(direction: trend)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

struct InsightRow: View {
    let insight: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "lightbulb.fill")
                .foregroundColor(.yellow)
            
            Text(insight)
                .font(.subheadline)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }
}

struct RecommendationRow: View {
    let recommendation: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "arrow.up.right.circle.fill")
                .foregroundColor(.green)
            
            Text(recommendation)
                .font(.subheadline)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }
}

struct MonthlyStatsView: View {
    let stats: MonthlyStats
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Monthly Statistics")
                .font(.headline)
                .padding(.bottom, 4)
            
            // Location Stats
            HStack {
                Text("Days at home: \(stats.locationSummary.daysAtHome)")
                    .frame(maxWidth: .infinity, alignment: .leading)
                Text("Days outside: \(stats.locationSummary.daysOutside)")
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            
            // Skipped Meals
            Text("Skipped meals: " + stats.skippedMeals.map { 
                "\($0.key) (\($0.value))" 
            }.joined(separator: ", "))
            
            // Similarity Percentages
            Text("Average similarity: " + stats.averageSimilarity.map {
                "\($0.key) (\(String(format: "%.1f", $0.value))%)"
            }.joined(separator: ", "))
            
            // Pass/Fail Stats
            Text("Results: " + stats.mealResults.map {
                "\($0.key) (\($0.value.passes)/\($0.value.fails))"
            }.joined(separator: ", "))
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(10)
        .shadow(radius: 2)
    }
} 