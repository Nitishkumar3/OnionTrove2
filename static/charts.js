// Data for the charts
const chartData = {
    categories: [
        "2023-01-17 00:00:00", "2023-01-16 00:00:00", "2023-01-15 00:00:00",
        "2023-01-14 00:00:00", "2023-01-13 00:00:00", "2023-01-12 00:00:00",
        "2023-01-11 00:00:00", "2023-01-10 00:00:00", "2023-01-09 00:00:00",
        "2023-01-08 00:00:00"
    ],
    values: [
        [8720, 8715, 8715, 8712, 8720, 8720, 8725, 8725, 8725, 8720],
        [2460, 2454, 2458, 2460, 2459, 2455, 2460, 2458, 2458, 2460],
        [5050052, 5050053, 5050055, 5050055, 5050050, 5050055, 5050057, 5050056, 5050057, 5050055],
        [798120, 798090, 798040, 798025, 798060, 798080, 798070, 798090, 798110, 798130]
    ]
};

// Configuration for the charts
const chartConfigs = [
    { id: "chart1", color: '#FF5733', name: 'Orange Series' },
    { id: "chart2", color: '#3498DB', name: 'Blue Series' },
    { id: "chart3", color: '#27AE60', name: 'Green Series' },
    { id: "chart4", color: '#F39C12', name: 'Yellow Series' }
];

// Function to create a single chart
function createChart(containerId, categories, values, color, seriesName) {
    const options = {
        series: [{
            name: seriesName,
            data: values,
        }],
        chart: {
            height: 350,
            type: 'area',
            foreColor: '#333',
            toolbar: { show: false },
        },
        dataLabels: { enabled: false },
        stroke: {
            curve: 'smooth',
            width: 3,
        },
        xaxis: {
            type: 'datetime',
            categories: categories.map(date => new Date(date).toISOString()),
        },
        tooltip: {
            x: { format: 'dd/MM/yy HH:mm' },
        },
        colors: [color],
    };

    new ApexCharts(document.querySelector(`#${containerId}`), options).render();
}

// Function to create all charts
function createAllCharts() {
    chartConfigs.forEach((config, index) => {
        createChart(config.id, chartData.categories, chartData.values[index], config.color, config.name);
    });
}

// Initialize charts
document.addEventListener('DOMContentLoaded', createAllCharts);