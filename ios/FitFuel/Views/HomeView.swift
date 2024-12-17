import SwiftUI
import Charts

struct HomeView: View {
    @StateObject private var viewModel = HomeViewModel()
    @Environment(\.colorScheme) var colorScheme
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Today's Progress Card
                    DailyProgressCard(progress: viewModel.todayProgress)
                    
                    // Next Meal Card
                    if let nextMeal = viewModel.nextMeal {
                        NextMealCard(meal: nextMeal) {
                            viewModel.handleMealAction(meal: nextMeal)
                        }
                    }
                    
                    // Weekly Stats Chart
                    WeeklyStatsCard(data: viewModel.weeklyStats)
                    
                    // Recent Insights
                    InsightsCard(insights: viewModel.recentInsights)
                    
                    // Recommendations
                    RecommendationsCard(recommendations: viewModel.recommendations)
                }
                .padding()
            }
            .navigationTitle("Home")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: viewModel.refreshData) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
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

// MARK: - Subviews
private struct DailyProgressCard: View {
    let progress: DailyProgress
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Today's Progress")
                .font(.headline)
            
            HStack {
                CircularProgressView(
                    progress: progress.overallProgress,
                    color: .accentColor
                )
                .frame(width: 60, height: 60)
                
                VStack(alignment: .leading, spacing: 8) {
                    ProgressRow(
                        label: "Meals",
                        count: progress.completedMeals,
                        total: progress.totalMeals
                    )
                    ProgressRow(
                        label: "Compliance",
                        value: progress.complianceRate,
                        format: "%.0f%%"
                    )
                }
                .padding(.leading)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

private struct NextMealCard: View {
    let meal: ScheduledMeal
    let action: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Next Meal")
                .font(.headline)
            
            VStack(alignment: .leading, spacing: 8) {
                Text(meal.name)
                    .font(.title3)
                    .bold()
                
                Text(meal.scheduledTime.formatted(date: .omitted, time: .shortened))
                    .foregroundColor(.secondary)
                
                if !meal.ingredients.isEmpty {
                    Text("Main ingredients: " + meal.ingredients.joined(separator: ", "))
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
            }
            
            Button(action: action) {
                Text("View Details")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

private struct WeeklyStatsCard: View {
    let data: [DayStats]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Weekly Overview")
                .font(.headline)
            
            Chart(data) { day in
                BarMark(
                    x: .value("Day", day.date, unit: .day),
                    y: .value("Compliance", day.complianceRate)
                )
                .foregroundStyle(by: .value("Status", day.status))
            }
            .frame(height: 200)
            .chartForegroundStyleScale([
                "At Home": Color.green,
                "Outside": Color.orange,
                "Skipped": Color.red
            ])
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

private struct InsightsCard: View {
    let insights: [Insight]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Insights")
                .font(.headline)
            
            ForEach(insights) { insight in
                HStack {
                    Image(systemName: insight.iconName)
                        .foregroundColor(.accentColor)
                    
                    VStack(alignment: .leading) {
                        Text(insight.title)
                            .font(.subheadline)
                            .bold()
                        Text(insight.description)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.vertical, 4)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

private struct RecommendationsCard: View {
    let recommendations: [Recommendation]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recommendations")
                .font(.headline)
            
            ForEach(recommendations) { recommendation in
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: recommendation.iconName)
                            .foregroundColor(.accentColor)
                        Text(recommendation.title)
                            .font(.subheadline)
                            .bold()
                    }
                    
                    Text(recommendation.description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 4)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

// MARK: - Helper Views
private struct CircularProgressView: View {
    let progress: Double
    let color: Color
    
    var body: some View {
        ZStack {
            Circle()
                .stroke(color.opacity(0.2), lineWidth: 8)
            
            Circle()
                .trim(from: 0, to: progress)
                .stroke(color, style: StrokeStyle(
                    lineWidth: 8,
                    lineCap: .round
                ))
                .rotationEffect(.degrees(-90))
            
            Text("\(Int(progress * 100))%")
                .font(.caption)
                .bold()
        }
    }
}

private struct ProgressRow: View {
    let label: String
    var count: Int?
    var total: Int?
    var value: Double?
    var format: String?
    
    var body: some View {
        HStack {
            Text(label)
                .foregroundColor(.secondary)
            Spacer()
            if let count = count, let total = total {
                Text("\(count)/\(total)")
                    .bold()
            } else if let value = value, let format = format {
                Text(String(format: format, value))
                    .bold()
            }
        }
    }
}

#Preview {
    HomeView()
} 