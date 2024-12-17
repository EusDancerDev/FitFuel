package com.nutrisync.ui.settings

import android.os.Bundle
import android.widget.ArrayAdapter
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.datepicker.MaterialDatePicker
import com.nutrisync.R
import com.nutrisync.databinding.ActivityPhysicalSettingsBinding
import com.nutrisync.domain.models.ActivityLevel
import com.nutrisync.domain.models.Gender
import dagger.hilt.android.AndroidEntryPoint
import java.util.Date

@AndroidEntryPoint
class PhysicalSettingsActivity : AppCompatActivity() {
    private lateinit var binding: ActivityPhysicalSettingsBinding
    private val viewModel: PhysicalSettingsViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPhysicalSettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
        setupObservers()
    }

    private fun setupUI() {
        // Setup toolbar
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = getString(R.string.physical_settings)

        // Setup gender spinner
        ArrayAdapter.createFromResource(
            this,
            R.array.genders,
            android.R.layout.simple_spinner_item
        ).also { adapter ->
            adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
            binding.spinnerGender.adapter = adapter
        }

        // Setup activity level spinner
        ArrayAdapter.createFromResource(
            this,
            R.array.activity_levels,
            android.R.layout.simple_spinner_item
        ).also { adapter ->
            adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
            binding.spinnerActivityLevel.adapter = adapter
        }

        // Setup date picker
        binding.btnDateOfBirth.setOnClickListener {
            showDatePicker()
        }

        // Setup text change listeners
        binding.etHeight.addTextChangedListener { text ->
            viewModel.updateHeight(text.toString())
        }

        binding.etWeight.addTextChangedListener { text ->
            viewModel.updateWeight(text.toString())
        }

        // Setup spinners
        binding.spinnerGender.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>, view: View?, pos: Int, id: Long) {
                val gender = when (pos) {
                    0 -> Gender.MALE
                    1 -> Gender.FEMALE
                    2 -> Gender.OTHER
                    else -> Gender.PREFER_NOT_TO_SAY
                }
                viewModel.updateGender(gender)
            }

            override fun onNothingSelected(parent: AdapterView<*>) {}
        }

        binding.spinnerActivityLevel.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>, view: View?, pos: Int, id: Long) {
                val level = when (pos) {
                    0 -> ActivityLevel.SEDENTARY
                    1 -> ActivityLevel.LIGHT
                    2 -> ActivityLevel.MODERATE
                    3 -> ActivityLevel.ACTIVE
                    else -> ActivityLevel.VERY_ACTIVE
                }
                viewModel.updateActivityLevel(level)
            }

            override fun onNothingSelected(parent: AdapterView<*>) {}
        }

        // Setup save button
        binding.btnSave.setOnClickListener {
            viewModel.saveSettings()
        }
    }

    private fun setupObservers() {
        viewModel.height.observe(this) { height ->
            binding.etHeight.setText(height)
        }

        viewModel.weight.observe(this) { weight ->
            binding.etWeight.setText(weight)
        }

        viewModel.gender.observe(this) { gender ->
            val position = when (gender) {
                Gender.MALE -> 0
                Gender.FEMALE -> 1
                Gender.OTHER -> 2
                Gender.PREFER_NOT_TO_SAY -> 3
            }
            binding.spinnerGender.setSelection(position)
        }

        viewModel.activityLevel.observe(this) { level ->
            val position = when (level) {
                ActivityLevel.SEDENTARY -> 0
                ActivityLevel.LIGHT -> 1
                ActivityLevel.MODERATE -> 2
                ActivityLevel.ACTIVE -> 3
                ActivityLevel.VERY_ACTIVE -> 4
            }
            binding.spinnerActivityLevel.setSelection(position)
        }

        viewModel.dateOfBirth.observe(this) { date ->
            binding.btnDateOfBirth.text = date.format()
        }

        viewModel.isLoading.observe(this) { isLoading ->
            binding.progressBar.isVisible = isLoading
            binding.btnSave.isEnabled = !isLoading
        }

        viewModel.error.observe(this) { error ->
            error?.let {
                showError(it)
            }
        }

        viewModel.saveSuccess.observe(this) { success ->
            if (success) {
                showSuccess()
                finish()
            }
        }
    }

    private fun showDatePicker() {
        val picker = MaterialDatePicker.Builder.datePicker()
            .setTitleText("Select date of birth")
            .setSelection(viewModel.dateOfBirth.value?.time ?: MaterialDatePicker.todayInUtcMilliseconds())
            .build()

        picker.addOnPositiveButtonClickListener { selection ->
            viewModel.updateDateOfBirth(Date(selection))
        }

        picker.show(supportFragmentManager, "date_picker")
    }

    private fun showError(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG).show()
    }

    private fun showSuccess() {
        Toast.makeText(this, R.string.settings_saved, Toast.LENGTH_SHORT).show()
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
} 