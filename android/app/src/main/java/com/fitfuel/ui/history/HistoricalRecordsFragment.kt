import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.github.mikephil.charting.data.Entry
import com.github.mikephil.charting.data.LineData
import com.github.mikephil.charting.data.LineDataSet
import com.google.android.material.tabs.TabLayout
import com.nutrisync.R
import com.nutrisync.databinding.FragmentHistoricalRecordsBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class HistoricalRecordsFragment : Fragment() {
    private var _binding: FragmentHistoricalRecordsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: HistoricalRecordsViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHistoricalRecordsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupUI()
        setupObservers()
        
        // Load initial data
        viewModel.loadData(TimePeriod.WEEK)
    }

    private fun setupUI() {
        // Setup TabLayout listener
        binding.tabLayout.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                when (tab?.position) {
                    0 -> viewModel.loadData(TimePeriod.WEEK)
                    1 -> viewModel.loadData(TimePeriod.MONTH)
                    2 -> viewModel.loadData(TimePeriod.YEAR)
                }
            }
            override fun onTabUnselected(tab: TabLayout.Tab?) {}
            override fun onTabReselected(tab: TabLayout.Tab?) {}
        })

        // Setup chart
        binding.complianceChart.apply {
            description.isEnabled = false
            axisRight.isEnabled = false
            legend.isEnabled = false
            setTouchEnabled(true)
            setPinchZoom(true)
        }
    }

    private fun setupObservers() {
        // Observe monthly stats
        viewModel.monthlyStats.observe(viewLifecycleOwner) { stats ->
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

        // Observe chart data
        viewModel.chartData.observe(viewLifecycleOwner) { data ->
            updateChart(data)
        }
    }

    private fun formatSkippedMeals(skippedMeals: Map<String, Int>): String {
        return "Skipped meals: " + skippedMeals.entries.joinToString { 
            "${it.key} (${it.value})" 
        }
    }

    private fun formatSimilarityPercentages(similarities: Map<String, Double>): String {
        return "Average similarity: " + similarities.entries.joinToString { 
            "${it.key} (${String.format("%.1f", it.value)}%)" 
        }
    }

    private fun formatPassFailStats(results: Map<String, MealResult>): String {
        return "Results: " + results.entries.joinToString { 
            "${it.key} (${it.value.passes}/${it.value.fails})" 
        }
    }

    private fun updateChart(data: List<ChartDataPoint>) {
        val entries = data.mapIndexed { index, point ->
            Entry(index.toFloat(), point.value.toFloat())
        }

        val dataSet = LineDataSet(entries, "Progress").apply {
            color = requireContext().getColor(R.color.primary)
            setDrawCircles(false)
            lineWidth = 2f
            mode = LineDataSet.Mode.CUBIC_BEZIER
        }

        binding.complianceChart.apply {
            this.data = LineData(dataSet)
            invalidate()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
} 