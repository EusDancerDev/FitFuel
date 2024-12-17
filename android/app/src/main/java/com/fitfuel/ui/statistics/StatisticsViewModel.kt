package com.nutrisync.ui.statistics

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nutrisync.domain.models.Insight
import com.nutrisync.domain.models.MonthlyStats
import com.nutrisync.domain.models.Recommendation
import com.nutrisync.domain.repositories.StatisticsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class StatisticsViewModel @Inject constructor(
    private val statisticsRepository: StatisticsRepository
) : ViewModel() {

    private val _monthlyStats = MutableLiveData<MonthlyStats>()
    val monthlyStats: LiveData<MonthlyStats> = _monthlyStats

    private val _insights = MutableLiveData<List<Insight>>()
    val insights: LiveData<List<Insight>> = _insights

    private val _recommendations = MutableLiveData<List<Recommendation>>()
    val recommendations: LiveData<List<Recommendation>> = _recommendations

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    init {
        loadStatistics()
    }

    fun loadStatistics() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val stats = statisticsRepository.getMonthlyStats()
                _monthlyStats.value = stats
                
                val insights = statisticsRepository.getInsights()
                _insights.value = insights
                
                val recommendations = statisticsRepository.getRecommendations()
                _recommendations.value = recommendations
                
                _error.value = null
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun onInsightClicked(insight: Insight) {
        viewModelScope.launch {
            try {
                statisticsRepository.markInsightAsRead(insight.id)
                // Refresh insights after marking as read
                val updatedInsights = statisticsRepository.getInsights()
                _insights.value = updatedInsights
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }

    fun onRecommendationApplied(recommendation: Recommendation) {
        viewModelScope.launch {
            try {
                statisticsRepository.applyRecommendation(recommendation.id)
                // Refresh recommendations after applying
                val updatedRecommendations = statisticsRepository.getRecommendations()
                _recommendations.value = updatedRecommendations
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }

    fun refreshData() {
        loadStatistics()
    }
} 