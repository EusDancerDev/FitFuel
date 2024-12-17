package com.nutrisync.ui.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.nutrisync.databinding.ItemRecommendationBinding
import com.nutrisync.domain.models.Recommendation

class RecommendationAdapter(
    private val onRecommendationClicked: (Recommendation) -> Unit
) : ListAdapter<Recommendation, RecommendationAdapter.ViewHolder>(RecommendationDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemRecommendationBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class ViewHolder(
        private val binding: ItemRecommendationBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        init {
            binding.btnApplyRecommendation.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onRecommendationClicked(getItem(position))
                }
            }
        }

        fun bind(recommendation: Recommendation) {
            binding.apply {
                tvRecommendationType.text = recommendation.type
                tvRecommendationText.text = recommendation.description
                tvConfidenceScore.text = "${recommendation.confidenceScore}% confidence"
                
                // Set icon based on recommendation type
                ivRecommendationIcon.setImageResource(
                    when (recommendation.type) {
                        "MEAL_TIMING" -> com.nutrisync.R.drawable.ic_time
                        "PORTION_SIZE" -> com.nutrisync.R.drawable.ic_portion
                        "NUTRITION" -> com.nutrisync.R.drawable.ic_nutrition
                        "HABIT" -> com.nutrisync.R.drawable.ic_habit
                        else -> com.nutrisync.R.drawable.ic_recommendation
                    }
                )

                // Disable apply button if recommendation is already applied
                btnApplyRecommendation.isEnabled = !recommendation.isApplied
            }
        }
    }

    private class RecommendationDiffCallback : DiffUtil.ItemCallback<Recommendation>() {
        override fun areItemsTheSame(oldItem: Recommendation, newItem: Recommendation): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Recommendation, newItem: Recommendation): Boolean {
            return oldItem == newItem
        }
    }
} 