package com.nutrisync.ui.menu

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nutrisync.domain.models.Meal
import com.nutrisync.domain.repositories.MenuRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MenuViewModel @Inject constructor(
    private val menuRepository: MenuRepository
) : ViewModel() {

    private val _meals = MutableLiveData<List<Meal>>()
    val meals: LiveData<List<Meal>> = _meals

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    init {
        loadMenu()
    }

    fun loadMenu() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val menu = menuRepository.getWeeklyMenu()
                _meals.value = menu
                _error.value = null
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun skipMeal(mealId: String) {
        viewModelScope.launch {
            try {
                menuRepository.skipMeal(mealId)
                // Refresh menu after skipping meal
                loadMenu()
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }

    fun replaceMeal(mealId: String) {
        viewModelScope.launch {
            try {
                menuRepository.generateAlternativeMeal(mealId)
                // Refresh menu after replacing meal
                loadMenu()
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }

    fun refreshMenu() {
        loadMenu()
    }
} 