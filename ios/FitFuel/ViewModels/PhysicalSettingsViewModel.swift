import Foundation
import Combine

class PhysicalSettingsViewModel: ObservableObject {
    @Published var height: String = ""
    @Published var weight: String = ""
    @Published var gender: Gender = .preferNotToSay
    @Published var activityLevel: ActivityLevel = .moderate
    @Published var dateOfBirth: Dahete = Calendar.current.date(byAdding: .year, value: -18, to: Date()) ?? Date()
    
    @Published var showError = false
    @Published var errorMessage = ""
    @Published var isProcessing = false
    @Published var showSuccessAlert = false
    
    private var cancellables = Set<AnyCancellable>()
    private let userService: UserService
    
    init(userService: UserService = UserService()) {
        self.userService = userService
        loadUserData()
    }
    
    func loadUserData() {
        isProcessing = true
        
        userService.getCurrentUser()
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isProcessing = false
                if case .failure(let error) = completion {
                    self?.showError = true
                    self?.errorMessage = error.localizedDescription
                }
            } receiveValue: { [weak self] user in
                self?.height = String(user.height)
                self?.weight = String(user.weight)
                self?.gender = user.gender
                self?.activityLevel = user.activityLevel
                self?.dateOfBirth = user.dateOfBirth
            }
            .store(in: &cancellables)
    }
    
    func saveSettings() {
        guard validateInputs() else { return }
        
        isProcessing = true
        
        let settings = PhysicalSettings(
            height: Int(height) ?? 0,
            weight: Int(weight) ?? 0,
            gender: gender,
            activityLevel: activityLevel,
            dateOfBirth: dateOfBirth
        )
        
        userService.updatePhysicalSettings(settings)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isProcessing = false
                if case .failure(let error) = completion {
                    self?.showError = true
                    self?.errorMessage = error.localizedDescription
                }
            } receiveValue: { [weak self] _ in
                self?.showSuccessAlert = true
            }
            .store(in: &cancellables)
    }
    
    private func validateInputs() -> Bool {
        guard let heightValue = Int(height), heightValue > 0 else {
            showError = true
            errorMessage = "Please enter a valid height"
            return false
        }
        
        guard let weightValue = Int(weight), weightValue > 0 else {
            showError = true
            errorMessage = "Please enter a valid weight"
            return false
        }
        
        let calendar = Calendar.current
        let ageComponents = calendar.dateComponents([.year], from: dateOfBirth, to: Date())
        guard let age = ageComponents.year, age >= 13 else {
            showError = true
            errorMessage = "You must be at least 13 years old"
            return false
        }
        
        return true
    }
}

enum Gender: String, CaseIterable, Identifiable {
    case male = "Male"
    case female = "Female"
    case other = "Other"
    case preferNotToSay = "Prefer not to say"
    
    var id: String { self.rawValue }
}

enum ActivityLevel: String, CaseIterable, Identifiable {
    case sedentary = "Sedentary"
    case light = "Light"
    case moderate = "Moderate"
    case active = "Active"
    case veryActive = "Very Active"
    
    var id: String { self.rawValue }
    
    var description: String {
        switch self {
        case .sedentary: return "Little to no exercise"
        case .light: return "Light exercise 1-3 times/week"
        case .moderate: return "Moderate exercise 3-5 times/week"
        case .active: return "Active exercise 6-7 times/week"
        case .veryActive: return "Very active exercise daily"
        }
    }
}

struct PhysicalSettings {
    let height: Int
    let weight: Int
    let gender: Gender
    let activityLevel: ActivityLevel
    let dateOfBirth: Date
} 