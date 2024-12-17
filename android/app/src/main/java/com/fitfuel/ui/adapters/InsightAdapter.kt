package com.nutrisync.ui.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.nutrisync.databinding.ItemInsightBinding
import com.nutrisync.domain.models.Insight

class InsightAdapter(
    private val onInsightClicked: (Insight) -> Unit
) : ListAdapter<Insight, InsightAdapter.ViewHolder>(InsightDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemInsightBinding.inflate(
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
        private val binding: ItemInsightBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        init {
            binding.root.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onInsightClicked(getItem(position))
                }
            }
        }

        fun bind(insight: Insight) {
            binding.apply {
                tvInsightTitle.text = insight.title
                tvInsightDescription.text = insight.description
                
                // Set icon based on insight type
                ivInsightIcon.setImageResource(
                    when (insight.type) {
                        "PATTERN" -> com.nutrisync.R.drawable.ic_pattern
                        "IMPROVEMENT" -> com.nutrisync.R.drawable.ic_improvement
                        "WARNING" -> com.nutrisync.R.drawable.ic_warning
                        "ACHIEVEMENT" -> com.nutrisync.R.drawable.ic_achievement
                        else -> com.nutrisync.R.drawable.ic_insight
                    }
                )
            }
        }
    }

    private class InsightDiffCallback : DiffUtil.ItemCallback<Insight>() {
        override fun areItemsTheSame(oldItem: Insight, newItem: Insight): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Insight, newItem: Insight): Boolean {
            return oldItem == newItem
        }
    }
} 