package com.nutrisync.ui.history

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import com.nutrisync.databinding.ActivityHistoricalRecordsBinding
import com.nutrisync.ui.adapters.InsightAdapter
import com.nutrisync.ui.adapters.RecommendationAdapter
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class HistoricalRecordsActivity : AppCompatActivity() {
    private lateinit var binding: ActivityHistoricalRecordsBinding
    private val viewModel: HistoricalRecordsViewModel by viewModels()
    
    private val insightAdapter = InsightAdapter { insight ->
        viewModel.onInsightClicked(insight)
    }
    
    private val recommendationAdapter = RecommendationAdapter { recommendation ->
        viewModel.onRecommendationClicked(recommendation)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityHistoricalRecordsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupUI()
        setupObservers()
        viewModel.loadData()
    }

    private fun setupUI() {
        binding.apply {
            // Setup RecyclerViews
            rvInsights.apply {
                layoutManager = LinearLayoutManager(this@HistoricalRecordsActivity)
                adapter = insightAdapter
            }
            
            rvRecommendations.apply {
                layoutManager = LinearLayoutManager(this@HistoricalRecordsActivity)
                adapter = recommendationAdapter
            }

            // Setup TabLayout listener
            tabLayout.addOnTabSelectedListener(viewModel.tabSelectedListener)

            // Setup SwipeRefreshLayout
            swipeRefresh.setOnRefreshListener {
                viewModel.refreshData()
            }
        }
    }

    private fun setupObservers() {
        viewModel.apply {
            insights.observe(this@HistoricalRecordsActivity) { insights ->
                insightAdapter.submitList(insights)
            }
            
            recommendations.observe(this@HistoricalRecordsActivity) { recommendations ->
                recommendationAdapter.submitList(recommendations)
            }
            
            monthlyStats.observe(this@HistoricalRecordsActivity) { stats ->
                updateStatsUI(stats)
            }
            
            isLoading.observe(this@HistoricalRecordsActivity) { loading ->
                binding.swipeRefresh.isRefreshing = loading
            }
        }
    }

    private fun updateStatsUI(stats: MonthlyStats) {
        binding.apply {
            // Location stats
            tvDaysAtHome.text = getString(R.string.days_at_home, stats.locationSummary.daysAtHome)
            tvDaysOutside.text = getString(R.string.days_outside, stats.locationSummary.daysOutside)

            // Skipped meals
            tvSkippedMeals.text = formatSkippedMeals(stats.skippedMeals)

            // Similarity percentages
            tvSimilarityPercentages.text = formatSimilarityPercentages(stats.averageSimilarity)

            // Pass/Fail stats
            tvPassFailStats.text = formatPassFailStats(stats.mealResults)
        }
    }

    private fun formatSkippedMeals(skippedMeals: Map<String, Int>): String {
        return getString(R.string.skipped_meals_format, 
            skippedMeals.entries.joinToString { "${it.key} (${it.value})" }
        )
    }

    private fun formatSimilarityPercentages(similarities: Map<String, Double>): String {
        return getString(R.string.similarity_percentages_format,
            similarities.entries.joinToString { 
                "${it.key} (${String.format("%.1f", it.value)}%)" 
            }
        )
    }

    private fun formatPassFailStats(results: Map<String, MealResult>): String {
        return getString(R.string.pass_fail_stats_format,
            results.entries.joinToString { 
                "${it.key} (${it.value.passes}/${it.value.fails})" 
            }
        )
    }
} 