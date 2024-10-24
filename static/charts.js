async function fetchTorMetrics() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data && data.dates && data.values) {
            const chartData = {
                categories: data.dates,
                values: [
                    data.values.torusers,
                    data.values.onionservicebandwidth,
                    data.values.onionsites,
                    data.values.torrelays,
                    data.values.torbridges,
                    data.values.torrelayusers,
                    data.values.torbridgeusers,
                    data.values.tornetworkadvertisedbandwidth,
                    data.values.tornetworkconsumedbandwidth
                ]
            };

            createAllCharts(chartData);
        }
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}


function normalizeData(values) {
    const maxValue = Math.max(...values);
    return values.map(value => (value / maxValue) * 100);
}

const chartConfigs = [
    { id: "chart1", color: '#27AE60', name: 'Tor Users' },
    { id: "chart3", color: '#7F00FF', name: 'Onion Service Bandwidth' },
    { id: "chart2", color: '#F39C12', name: 'Onion Sites' },
    { id: "chart4", color: '#FF5733', name: 'Tor Relays' },
    { id: "chart5", color: '#3498DB', name: 'Tor Bridges' },
    { id: "chart6", color: '#005F60', name: 'Tor Relay Users' },
    { id: "chart7", color: '#7D1007', name: 'Tor Bridge Users' },
    { id: "chart8", color: ['#FF69B4', '#6667AB'], name: ['Tor Advertised Bandwidth', 'Tor Consumed Bandwidth'] }

];


function createChart(containerId, categories, values, color, seriesName) {
    const options = {
        series: Array.isArray(seriesName) ? seriesName.map((name, i) => ({
            name: name,
            data: values[i]
        })) : [{
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
            categories: categories.map(date => new Date(date).getTime()),
        },
        tooltip: {
            x: { format: 'dd/MM/yy HH:mm' },
        },
        colors: Array.isArray(color) ? color : [color],
    };

    new ApexCharts(document.querySelector(`#${containerId}`), options).render();
}


function createAllCharts(chartData) {
    chartConfigs.forEach((config, index) => {
        if (config.id === "chart8") {

            const advertisedBandwidth = normalizeData(chartData.values[7]);
            const consumedBandwidth = normalizeData(chartData.values[8]);
            createChart(config.id, chartData.categories, [advertisedBandwidth, consumedBandwidth], config.color, config.name);
        } else {
            createChart(config.id, chartData.categories, chartData.values[index], config.color, config.name);
        }
    });
}

document.addEventListener('DOMContentLoaded', fetchTorMetrics);