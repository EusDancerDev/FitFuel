import Foundation
import Combine

class MenuViewModel: ObservableObject {
    @Published var meals: [Meal] = []
    @Published var isLoading = false
    @Published var error: String?
    
    private var cancellables = Set<AnyCancellable>()
    
    func loadMenu() {
        // Menu loading implementation
    }
    
    func refreshMenu() {
        // Menu refresh implementation
    }
} 