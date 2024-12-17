package com.nutrisync.ui.menu

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.snackbar.Snackbar
import com.nutrisync.databinding.ActivityMenuBinding
import com.nutrisync.ui.adapters.MealAdapter
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MenuActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMenuBinding
    private val viewModel: MenuViewModel by viewModels()
    
    private val mealAdapter = MealAdapter(
        onMealClicked = { meal ->
            // Navigate to meal details
            startActivity(MealDetailsActivity.createIntent(this, meal.id))
        },
        onSkipClicked = { meal ->
            viewModel.skipMeal(meal.id)
        },
        onReplaceClicked = { meal ->
            viewModel.replaceMeal(meal.id)
        }
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMenuBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupUI()
        setupObservers()
    }

    private fun setupUI() {
        // Setup toolbar
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        
        // Setup RecyclerView
        binding.rvMeals.apply {
            layoutManager = LinearLayoutManager(this@MenuActivity)
            adapter = mealAdapter
        }
        
        // Setup SwipeRefreshLayout
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.refreshMenu()
        }
    }

    private fun setupObservers() {
        viewModel.meals.observe(this) { meals ->
            mealAdapter.submitList(meals)
            binding.emptyView.isVisible = meals.isEmpty()
        }
        
        viewModel.isLoading.observe(this) { isLoading ->
            binding.swipeRefresh.isRefreshing = isLoading
        }
        
        viewModel.error.observe(this) { error ->
            error?.let { showError(it) }
        }
    }

    private fun showError(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG).show()
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
} 