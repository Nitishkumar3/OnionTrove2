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
            displayData(chartData);
        }
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

function displayData(displayData) {
    const activetorrelaystoday = displayData["values"][3][0];
    const activetorrelaysyesterday = displayData["values"][3][1];

    const activetorbridgestoday = displayData["values"][4][0];
    const activetorbridgesyesterday = displayData["values"][4][1];

    const activetoruserstoday = displayData["values"][0][0];
    const activetorusersyesterday = displayData["values"][0][1];

    const activeonionsitestoday = displayData["values"][2][0];
    const activeonionsitesyesterday = displayData["values"][2][1];

    const activetorrelayspercentagechange = (((activetorrelaystoday - activetorrelaysyesterday) / activetorrelaysyesterday) * 100).toFixed(2);
    const activetorbridgespercentagechange = (((activetorbridgestoday - activetorbridgesyesterday) / activetorbridgesyesterday) * 100).toFixed(2);
    const activetoruserspercentagechange = (((activetoruserstoday - activetorusersyesterday) / activetorusersyesterday) * 100).toFixed(2);
    const activeonionsitespercentagechange = (((activeonionsitestoday - activeonionsitesyesterday) / activeonionsitesyesterday) * 100).toFixed(2);

    document.getElementById("activeTorRelays").innerText = activetorrelaystoday.toLocaleString();
    document.getElementById("relayChange").innerText = `${activetorrelayspercentagechange}%`;
    document.getElementById("activeTorBridges").innerText = activetorbridgestoday.toLocaleString();
    document.getElementById("bridgeChange").innerText = `${activetorbridgespercentagechange}%`;
    document.getElementById("activeTorUsers").innerText = activetoruserstoday.toLocaleString();
    document.getElementById("userChange").innerText = `${activetoruserspercentagechange}%`;
    document.getElementById("activeOnionSites").innerText = activeonionsitestoday.toLocaleString();
    document.getElementById("onionChange").innerText = `${activeonionsitespercentagechange}%`;

    const setColor = (id, percentage) => {
        const element = document.getElementById(id);
        element.className = percentage > 0 ? "text-xs font-medium text-green-600" : "text-xs font-medium text-rose-600";
    };

    setColor("relayChange", activetorrelayspercentagechange);
    setColor("bridgeChange", activetorbridgespercentagechange);
    setColor("userChange", activetoruserspercentagechange);
    setColor("onionChange", activeonionsitespercentagechange);
}


function normalizeData(data) {
    const min = Math.min(...data);
    const max = Math.max(...data);

    return data.map(value => {
        const normalizedValue = (value - min) / (max - min);
        return parseFloat(normalizedValue.toFixed(2));
    });
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
            y: {
                formatter: function(value) {
                    return value.toFixed(2);
                }
            }
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
        } else if (config.id === "chart3") {
            // Format each value in chartData.values[1] to 2 decimal places
            const onionServiceBandwidth = chartData.values[1].map(value => parseFloat(value).toFixed(2));
        
            createChart(config.id, chartData.categories, onionServiceBandwidth, config.color, config.name);        
        } else {
            createChart(config.id, chartData.categories, chartData.values[index], config.color, config.name);
        }
    });
}

document.addEventListener('DOMContentLoaded', fetchTorMetrics);