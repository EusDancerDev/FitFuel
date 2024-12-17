package com.nutrisync.ui.meal

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.nutrisync.databinding.ActivityMealSkipBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MealSkipActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMealSkipBinding
    private val viewModel: MealSkipViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMealSkipBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setupUI()
        setupObservers()
    }

    private fun setupUI() {
        binding.btnConfirmSkip.setOnClickListener {
            viewModel.confirmSkip(binding.etReason.text.toString())
        }

        binding.btnCancel.setOnClickListener {
            finish()
        }
    }

    private fun setupObservers() {
        viewModel.skipResult.observe(this) { success ->
            if (success) {
                finish()
            }
        }
    }
} 