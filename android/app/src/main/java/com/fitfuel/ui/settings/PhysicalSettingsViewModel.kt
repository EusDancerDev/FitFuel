package com.nutrisync.ui.settings

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nutrisync.domain.models.ActivityLevel
import com.nutrisync.domain.models.Gender
import com.nutrisync.domain.models.PhysicalSettings
import com.nutrisync.domain.repositories.UserRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import java.util.Date
import javax.inject.Inject

@HiltViewModel
class PhysicalSettingsViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _height = MutableLiveData<String>()
    val height: LiveData<String> = _height

    private val _weight = MutableLiveData<String>()
    val weight: LiveData<String> = _weight

    private val _gender = MutableLiveData<Gender>()
    val gender: LiveData<Gender> = _gender

    private val _activityLevel = MutableLiveData<ActivityLevel>()
    val activityLevel: LiveData<ActivityLevel> = _activityLevel

    private val _dateOfBirth = MutableLiveData<Date>()
    val dateOfBirth: LiveData<Date> = _dateOfBirth

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _saveSuccess = MutableLiveData<Boolean>()
    val saveSuccess: LiveData<Boolean> = _saveSuccess

    init {
        loadUserData()
    }

    private fun loadUserData() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val user = userRepository.getCurrentUser()
                _height.value = user.height.toString()
                _weight.value = user.weight.toString()
                _gender.value = user.gender
                _activityLevel.value = user.activityLevel
                _dateOfBirth.value = user.dateOfBirth
                _error.value = null
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun updateHeight(height: String) {
        _height.value = height
    }

    fun updateWeight(weight: String) {
        _weight.value = weight
    }

    fun updateGender(gender: Gender) {
        _gender.value = gender
    }

    fun updateActivityLevel(level: ActivityLevel) {
        _activityLevel.value = level
    }

    fun updateDateOfBirth(date: Date) {
        _dateOfBirth.value = date
    }

    fun saveSettings() {
        if (!validateInputs()) return

        viewModelScope.launch {
            _isLoading.value = true
            try {
                val settings = PhysicalSettings(
                    height = _height.value?.toIntOrNull() ?: 0,
                    weight = _weight.value?.toIntOrNull() ?: 0,
                    gender = _gender.value ?: Gender.PREFER_NOT_TO_SAY,
                    activityLevel = _activityLevel.value ?: ActivityLevel.MODERATE,
                    dateOfBirth = _dateOfBirth.value ?: Date()
                )

                userRepository.updatePhysicalSettings(settings)
                _saveSuccess.value = true
                _error.value = null
            } catch (e: Exception) {
                _error.value = e.message
                _saveSuccess.value = false
            } finally {
                _isLoading.value = false
            }
        }
    }

    private fun validateInputs(): Boolean {
        val heightValue = _height.value?.toIntOrNull()
        if (heightValue == null || heightValue <= 0) {
            _error.value = "Please enter a valid height"
            return false
        }

        val weightValue = _weight.value?.toIntOrNull()
        if (weightValue == null || weightValue <= 0) {
            _error.value = "Please enter a valid weight"
            return false
        }

        val birthDate = _dateOfBirth.value
        if (birthDate == null || !isValidAge(birthDate)) {
            _error.value = "You must be at least 13 years old"
            return false
        }

        return true
    }

    private fun isValidAge(birthDate: Date): Boolean {
        val calendar = java.util.Calendar.getInstance()
        val today = calendar.time
        calendar.time = birthDate
        calendar.add(java.util.Calendar.YEAR, 13)
        return calendar.time.before(today)
    }
} 