function fetchETFData() {
    const symbol = document.getElementById('symbolInput').value;
    if (symbol) {
        fetchDataAndDisplay(symbol, 'resultsContainer', 'performance-table', 'industry-chart', 'stock-chart', 'performance-data-updated-time', 'industry-data-updated-time', 'stock-data-updated-time');
    } else {
        alert("請輸入ETF代號");
    }
}

function fetchCompareETFData() {
    const symbol = document.getElementById('compareInput').value;
    if (symbol) {
        // show the second ETF container
        document.getElementById('etf2-container').style.display = 'block';
        
        fetchDataAndDisplay(symbol, 'resultsContainer2', 'performance-table2', 'industry-chart2', 'stock-chart2', 'performance-data-updated-time2', 'industry-data-updated-time2', 'stock-data-updated-time2');
    } else {
        alert("請輸入要比較的第二個ETF代號");
    }
}


function fetchDataAndDisplay(symbol, resultsId, perfTableId, industryChartId, stockChartId, perfUpdateTimeId, industryUpdateTimeId, stockUpdateTimeId) {
    fetch(`/etf-pioneer/api/overview`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ symbol: symbol })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById(resultsId).innerHTML = `
            <h1>ETF: ${data.symbol}</h1>
            <p>ETF 名稱: ${data.etf_name}</p>
            <p>ETF 代號: ${data.symbol}</p>
            <p>今天價格: ${data.price_today}</p>
            <p>與前一個交易日價格差距: ${data.up_down_change}</p>
            <p>與前一個交易日價格差距百分比: ${data.up_down_percentage}</p>
            <p>來源資料更新時間: ${data.data_updated_date}</p>
        `;
    })
    .catch(error => {
        console.error('Error fetching ETF overview:', error);
        document.getElementById(resultsId).innerHTML = '無法讀取ETF概覽數據。';
    });
    fetchPerformance(symbol, perfTableId, perfUpdateTimeId);
    fetchTopIndustry(symbol, industryChartId, industryUpdateTimeId);
    fetchTop10Stock(symbol, stockChartId, stockUpdateTimeId);
}

function fetchPerformance(symbol, tableId, updateTimeId) {
    fetch(`/etf-pioneer/api/performance`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ symbol: symbol })
    })
    .then(response => response.json())
    .then(data => {
        const numRows = data.length;
        const rowHeight =50;
        const graphHeight = numRows * rowHeight;

        let layout = {
            title: 'ETF 績效表',
            responsive: true,
            height: graphHeight
        };
        let tableData = {
            type: 'table',
            header: {
                values: [["期間"], ["績效"]],
                align: "center",
                line: {width: 1, color: 'black'},
                fill: {color: "skyblue"},
                font: {family: "Arial", size: 12, color: "white"}
            },
            cells: {
                values: [
                    ['今年至今', '1 Week', '1 Month', '3 Months', '6 Months', '1 Year', '2 Years', '3 Years', '5 Years', '10 Years'],
                    [data.YTD, data['1_week'], data['1_month'], data['3_month'], data['6_month'], data['1_year'], data['2_year'], data['3_year'], data['5_year'], data['10_year']]
                ],
                align: "center",
                line: {color: "blue", width: 1},
                font: {family: "Arial", size: 11, color: ["black"]}
            }
        };
        Plotly.newPlot(tableId, [tableData], layout);
        document.getElementById(updateTimeId).textContent = `來源資料更新時間：${data.data_updated_date}`;
    })
    .catch(error => {
        console.error('Error fetching performance data:', error);
        document.getElementById(tableId).innerHTML = '績效數據讀取失敗。';
    });
}

function fetchTopIndustry(symbol, chartId, updateTimeId) {
    fetch(`/etf-pioneer/api/top-industry`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ symbol: symbol })
    })
    .then(response => response.json())
    .then(data => {
        let industryData = data.map(item => ({
            label: item.industry,
            value: parseFloat(item.ratio)
        }));
        let layout = {
            title: 'ETF 產業分布',
            responsive: true,
            autosize: true
        };
        let industryPieChart = {
            values: industryData.map(item => item.value),
            labels: industryData.map(item => item.label),
            type: 'pie'
        };
        Plotly.newPlot(chartId, [industryPieChart], layout);
        let updateTime = data.length > 0 ? data[0].data_updated_date : '未知';
        document.getElementById(updateTimeId).textContent = `來源資料更新時間：${updateTime}`;
    })
    .catch(error => {
        console.error('Error fetching industry data:', error);
        document.getElementById(chartId).innerHTML = '產業分布數據讀取失敗。';
        document.getElementById(updateTimeId).textContent = '來源資料更新時間：無法獲取';
    });
}

function fetchTop10Stock(symbol, chartId, updateTimeId) {
    fetch(`/etf-pioneer/api/top10-stock`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ symbol: symbol })
    })
    .then(response => response.json())
    .then(data => {
        let stockData = data.map(item => ({
            label: item.stock_name,
            value: parseFloat(item.ratio)
        }));
        let layout = {
            title: 'ETF 前十大持股',
            responsive: true
        };
        let topStockPieChart = {
            values: stockData.map(item => item.value),
            labels: stockData.map(item => item.label),
            type: 'pie'
        };
        Plotly.newPlot(chartId, [topStockPieChart], layout);
        let updateTime = data.length > 0 ? data[0].data_updated_date : '未知';
        document.getElementById(updateTimeId).textContent = `來源資料更新時間：${updateTime}`;
    })
    .catch(error => {
        console.error('Error fetching top 10 stocks data:', error);
        document.getElementById(chartId).innerHTML = '前十大持股數據讀取失敗。';
        document.getElementById(updateTimeId).textContent = '來源資料更新時間：無法獲取';
    });
}


function fetchStockETFData(){
    const stockSymbol = document.getElementById('stockInput').value;
    if (stockSymbol){
        fetch(`/etf-pioneer/api/stock`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ stockSymbol: stockSymbol })
    })
    .then(response => response.json())
    .then(data => {
        const sortedData = data.sort((a, b) => {
            const ratioA = parseFloat(a.ratio.replace('%', ''));
            const ratioB = parseFloat(b.ratio.replace('%', ''));
            return ratioB - ratioA; // sort in descending order
        });
        const numRows = sortedData.length;
        const rowHeight =50;
        const graphHeight = numRows * rowHeight;

        let layout = {
            title: '股票對應 ETF 佔比表',
            responsive: true,
            height: graphHeight
        };
        let tableData = {
                type: 'table',
                autosize: true,
                columnwidth:[20,20,20,30,25],
                header: {
                    values: [["輸入股票名稱"],["輸入股票代號"],["ETF 代號"],["輸入股票佔 ETF 比例"], ["來源資料更新時間"]],
                    align: "center",
                    line: {width: 1, color: 'black'},
                    fill: {color: "skyblue"},
                    font: {family: "Arial", size: 12, color: "white"}
                },
                cells: {
                    values: [
                        sortedData.map(item => item.stock_name),
                        sortedData.map(item => item.stock_code),
                        sortedData.map(item => item.symbol),
                        sortedData.map(item => item.ratio),
                        sortedData.map(item => item.data_updated_date)
                    ],
                    align: "center",
                    line: {color: "blue", width: 1},
                    font: {family: "Arial", size: 11, color: ["black"]}
                }
            };
            Plotly.newPlot("stock-to-ETF-table", [tableData], layout);
        })
        .catch(error => {
            console.error('Error fetching stock data:', error);
            document.getElementById("stock-to-ETF-table").innerHTML = '數據讀取失敗。';
        });
    }
}
