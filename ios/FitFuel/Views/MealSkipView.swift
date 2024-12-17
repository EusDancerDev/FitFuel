import SwiftUI

struct MealSkipView: View {
    @StateObject private var viewModel = MealSkipViewModel()
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Skip Meal")) {
                    TextField("Reason (optional)", text: $viewModel.skipReason)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                Section {
                    Button(action: {
                        Task {
                            await viewModel.confirmSkip()
                            dismiss()
                        }
                    }) {
                        Text("Confirm Skip")
                            .frame(maxWidth: .infinity)
                            .foregroundColor(.white)
                    }
                    .listRowBackground(Color.accentColor)
                    .disabled(viewModel.isProcessing)
                    
                    Button(action: {
                        dismiss()
                    }) {
                        Text("Cancel")
                            .frame(maxWidth: .infinity)
                            .foregroundColor(.red)
                    }
                    .listRowBackground(Color.clear)
                }
            }
            .navigationTitle("Skip Meal")
            .navigationBarTitleDisplayMode(.inline)
            .alert("Error", isPresented: $viewModel.showError) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage)
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
    MealSkipView()
} 