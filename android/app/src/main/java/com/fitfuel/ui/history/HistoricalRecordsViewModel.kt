import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nutrisync.data.api.APIService
import com.nutrisync.data.models.HistoricalData
import com.nutrisync.data.models.ChartDataPoint
import kotlinx.coroutines.launch
import java.util.Calendar
import java.util.Date

enum class TimePeriod {
    WEEK, MONTH, YEAR
}

enum class MetricType {
    COMPLIANCE, NUTRITION, TIMING, HEALTH
}

enum class TrendDirection {
    IMPROVING, DECLINING, STABLE, SLIGHTLY_IMPROVING, SLIGHTLY_DECLINING, INSUFFICIENT_DATA
}

data class MonthlyStats(
    val locationSummary: LocationSummary,
    val skippedMeals: Map<String, Int>,
    val averageSimilarity: Map<String, Double>,
    val mealResults: Map<String, MealResult>
)

data class LocationSummary(
    val daysAtHome: Int,
    val daysOutside: Int
)

data class MealResult(
    val passes: Int,
    val fails: Int
)

class HistoricalRecordsViewModel(
    private val apiService: APIService
) : ViewModel() {

    private val _averageCompliance = MutableLiveData<Double>()
    val averageCompliance: LiveData<Double> = _averageCompliance

    private val _consistencyScore = MutableLiveData<Double>()
    val consistencyScore: LiveData<Double> = _consistencyScore

    private val _complianceTrend = MutableLiveData<TrendDirection>()
    val complianceTrend: LiveData<TrendDirection> = _complianceTrend

    private val _consistencyTrend = MutableLiveData<TrendDirection>()
    val consistencyTrend: LiveData<TrendDirection> = _consistencyTrend

    private val _insights = MutableLiveData<List<String>>()
    val insights: LiveData<List<String>> = _insights

    private val _recommendations = MutableLiveData<List<String>>()
    val recommendations: LiveData<List<String>> = _recommendations

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _monthlyStats = MutableLiveData<MonthlyStats>()
    val monthlyStats: LiveData<MonthlyStats> = _monthlyStats

    fun loadData(period: TimePeriod) {
        _isLoading.value = true
        
        val endDate = Date()
        val startDate = Calendar.getInstance().apply {
            time = endDate
            when (period) {
                TimePeriod.WEEK -> add(Calendar.DAY_OF_YEAR, -7)
                TimePeriod.MONTH -> add(Calendar.MONTH, -1)
                TimePeriod.YEAR -> add(Calendar.YEAR, -1)
            }
        }.time

        viewModelScope.launch {
            try {
                val data = apiService.fetchHistoricalData(startDate, endDate)
                updateUI(data)
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun getChartData(metric: MetricType): List<ChartDataPoint> {
        return when (metric) {
            MetricType.COMPLIANCE -> complianceChartData
            MetricType.NUTRITION -> nutritionChartData
            MetricType.TIMING -> timingChartData
            MetricType.HEALTH -> healthChartData
        }
    }

    private fun updateUI(data: HistoricalData) {
        _averageCompliance.value = data.complianceTrends.overallCompliance
        _consistencyScore.value = data.timingPatterns.consistencyScore
        _complianceTrend.value = mapTrendDirection(data.complianceTrends.trend)
        _consistencyTrend.value = mapTrendDirection(data.timingPatterns.trend)
        _insights.value = generateInsights(data)
        _recommendations.value = data.recommendations
        _monthlyStats.value = formatMonthlyStats(data.monthlyStats)
    }

    private fun mapTrendDirection(trend: String): TrendDirection {
        return when (trend) {
            "improving" -> TrendDirection.IMPROVING
            "declining" -> TrendDirection.DECLINING
            "stable" -> TrendDirection.STABLE
            "slightly_improving" -> TrendDirection.SLIGHTLY_IMPROVING
            "slightly_declining" -> TrendDirection.SLIGHTLY_DECLINING
            else -> TrendDirection.INSUFFICIENT_DATA
        }
    }

    private fun generateInsights(data: HistoricalData): List<String> {
        val insights = mutableListOf<String>()

        // Compliance insights
        if (data.complianceTrends.overallCompliance > 80) {
            insights.add("Great job maintaining high compliance!")
        }

        // Nutritional insights
        data.nutritionalTrends.gaps.firstOrNull()?.let {
            insights.add("Consider increasing ${it.nutrient} intake")
        }

        // Timing insights
        if (data.timingPatterns.consistencyScore > 0.8) {
            insights.add("Excellent meal timing consistency")
        }

        // Health correlation insights
        data.healthCorrelations.energyLevels.maxByOrNull { it.value }?.let {
            insights.add("${it.key} has the most positive impact on your energy")
        }

        return insights
    }

    private fun formatMonthlyStats(stats: MonthlyStats): List<String> {
        return listOf(
            "Days at home: ${stats.locationSummary.daysAtHome}",
            "Days outside: ${stats.locationSummary.daysOutside}",
            "Skipped meals: " + stats.skippedMeals.entries.joinToString { 
                "${it.key} (${it.value})" 
            },
            "Average similarity: " + stats.averageSimilarity.entries.joinToString { 
                "${it.key} (${String.format("%.1f", it.value)}%)" 
            },
            "Results: " + stats.mealResults.entries.joinToString { 
                "${it.key} (${it.value.passes}/${it.value.fails})" 
            }
        )
    }
} 