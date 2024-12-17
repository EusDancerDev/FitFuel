import Foundation
import Combine

class HomeViewModel: ObservableObject {
    @Published var userData: UserData?
    @Published var todaysMeals: [Meal] = []
    @Published var isLoading = false
    
    func loadDashboard() {
        // Dashboard loading implementation
    }
} 