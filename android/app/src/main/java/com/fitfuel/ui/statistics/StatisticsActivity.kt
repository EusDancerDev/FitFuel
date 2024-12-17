package com.nutrisync.ui.statistics

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.snackbar.Snackbar
import com.nutrisync.databinding.ActivityStatisticsBinding
import com.nutrisync.ui.adapters.InsightAdapter
import com.nutrisync.ui.adapters.RecommendationAdapter
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class StatisticsActivity : AppCompatActivity() {
    private lateinit var binding: ActivityStatisticsBinding
    private val viewModel: StatisticsViewModel by viewModels()
    
    private val insightAdapter = InsightAdapter { insight ->
        viewModel.onInsightClicked(insight)
    }
    
    private val recommendationAdapter = RecommendationAdapter { recommendation ->
        viewModel.onRecommendationApplied(recommendation)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityStatisticsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupUI()
        setupObservers()
    }

    private fun setupUI() {
        // Setup toolbar
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        
        // Setup RecyclerViews
        binding.rvInsights.apply {
            layoutManager = LinearLayoutManager(this@StatisticsActivity)
            adapter = insightAdapter
        }
        
        binding.rvRecommendations.apply {
            layoutManager = LinearLayoutManager(this@StatisticsActivity)
            adapter = recommendationAdapter
        }
        
        // Setup SwipeRefreshLayout
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.refreshData()
        }
    }

    private fun setupObservers() {
        viewModel.monthlyStats.observe(this) { stats ->
            updateStatsUI(stats)
        }
        
        viewModel.insights.observe(this) { insights ->
            insightAdapter.submitList(insights)
        }
        
        viewModel.recommendations.observe(this) { recommendations ->
            recommendationAdapter.submitList(recommendations)
        }
        
        viewModel.isLoading.observe(this) { isLoading ->
            binding.swipeRefresh.isRefreshing = isLoading
        }
        
        viewModel.error.observe(this) { error ->
            error?.let { showError(it) }
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

    private fun showError(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG).show()
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
} 
} 