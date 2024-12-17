import SwiftUI

struct MenuView: View {
    @StateObject private var viewModel = MenuViewModel()
    
    var body: some View {
        NavigationView {
            Group {
                if viewModel.meals.isEmpty {
                    EmptyMenuView()
                } else {
                    MealList(
                        meals: viewModel.meals,
                        onMealTapped: { meal in
                            // Navigate to meal details
                        },
                        onSkipMeal: viewModel.skipMeal,
                        onReplaceMeal: viewModel.replaceMeal
                    )
                }
            }
            .navigationTitle("Menu")
            .refreshable {
                await viewModel.refreshMenu()
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

private struct MealList: View {
    let meals: [Meal]
    let onMealTapped: (Meal) -> Void
    let onSkipMeal: (String) -> Void
    let onReplaceMeal: (String) -> Void
    
    var body: some View {
        ScrollView {
            LazyVStack(spacing: 16) {
                ForEach(meals) { meal in
                    MealCard(
                        meal: meal,
                        onTap: { onMealTapped(meal) },
                        onSkip: { onSkipMeal(meal.id) },
                        onReplace: { onReplaceMeal(meal.id) }
                    )
                }
            }
            .padding()
        }
    }
}

private struct MealCard: View {
    let meal: Meal
    let onTap: () -> Void
    let onSkip: () -> Void
    let onReplace: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            VStack(alignment: .leading, spacing: 12) {
                // Meal Image
                if let imageUrl = meal.imageUrl {
                    AsyncImage(url: URL(string: imageUrl)) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                    } placeholder: {
                        Color.gray.opacity(0.3)
                    }
                    .frame(height: 200)
                    .clipped()
                }
                
                VStack(alignment: .leading, spacing: 8) {
                    // Meal Name and Time
                    HStack {
                        Text(meal.name)
                            .font(.headline)
                        Spacer()
                        Text(meal.scheduledTime.formatted(date: .omitted, time: .shortened))
                            .foregroundColor(.secondary)
                    }
                    
                    // Ingredients
                    Text(meal.ingredients.joined(separator: ", "))
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    
                    // Action Buttons
                    HStack {
                        Button(action: onSkip) {
                            Text("Skip")
                        }
                        .buttonStyle(.borderless)
                        
                        Button(action: onReplace) {
                            Text("Replace")
                        }
                        .buttonStyle(.borderless)
                    }
                }
                .padding()
            }
            .background(Color(.systemBackground))
            .cornerRadius(12)
            .shadow(radius: 2)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

private struct EmptyMenuView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "fork.knife.circle")
                .font(.system(size: 60))
                .foregroundColor(.secondary)
            
            Text("No Meals Planned")
                .font(.headline)
            
            Text("Pull to refresh")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    MenuView()
} 