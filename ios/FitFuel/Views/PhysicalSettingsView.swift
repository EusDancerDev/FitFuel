import SwiftUI

struct PhysicalSettingsView: View {
    @StateObject private var viewModel = PhysicalSettingsViewModel()
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            Form {
                // Basic Measurements
                Section(header: Text("Basic Measurements")) {
                    TextField("Height (cm)", text: $viewModel.height)
                        .keyboardType(.numberPad)
                    
                    TextField("Weight (kg)", text: $viewModel.weight)
                        .keyboardType(.numberPad)
                }
                
                // Personal Information
                Section(header: Text("Personal Information")) {
                    Picker("Gender", selection: $viewModel.gender) {
                        ForEach(Gender.allCases) { gender in
                            Text(gender.rawValue)
                                .tag(gender)
                        }
                    }
                    
                    DatePicker(
                        "Date of Birth",
                        selection: $viewModel.dateOfBirth,
                        in: ...Date(),
                        displayedComponents: .date
                    )
                }
                
                // Activity Level
                Section(
                    header: Text("Activity Level"),
                    footer: Text(viewModel.activityLevel.description)
                ) {
                    Picker("Activity Level", selection: $viewModel.activityLevel) {
                        ForEach(ActivityLevel.allCases) { level in
                            Text(level.rawValue)
                                .tag(level)
                        }
                    }
                }
                
                // Save Button
                Section {
                    Button(action: {
                        viewModel.saveSettings()
                    }) {
                        Text("Save Changes")
                            .frame(maxWidth: .infinity)
                            .foregroundColor(.white)
                    }
                    .listRowBackground(Color.accentColor)
                    .disabled(viewModel.isProcessing)
                }
            }
            .navigationTitle("Physical Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
            .alert("Error", isPresented: $viewModel.showError) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage)
            }
            .alert("Success", isPresented: $viewModel.showSuccessAlert) {
                Button("OK") {
                    dismiss()
                }
            } message: {
                Text("Your physical settings have been updated successfully.")
            }
            .overlay {
                if viewModel.isProcessing {
                    ProgressView()
                        .scaleEffect(1.5)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .background(Color.black.opacity(0.2))
                }
            }
        }
    }
}

#Preview {
    PhysicalSettingsView()
} 