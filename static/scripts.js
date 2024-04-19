// fetchETFOverview function is called when the user clicks the "Search" button
function fetchETFOverview() {
    const symbol = document.getElementById('symbolInput').value;
    fetch(`/etf-pioneer/api/overview`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json',},
        body: JSON.stringify({ symbol: symbol })})
    .then(response => response.json())
    .then(data => {
        document.getElementById('resultsContainer').innerHTML = `
            <h1>ETF: ${data.symbol}</h1>
            <p>ETF名稱: ${data.etf_name}</p>
            <p>ETF代號: ${data.symbol}</p>
            <p>今天價格: ${data.price_today}</p>
            <p>與前一個交易日價格差距: ${data.up_down_change}</p>
            <p>與前一個交易日價格差距百分比: ${data.up_down_percentage}</p>
            <p>來源資料更新時間: ${data.data_updated_date}</p>
        `;
    })
    .catch(error => console.error('Error:', error));
}

// Table for ETF performance function is called when the user clicks the "Search" button
function fetchPerformance() {
    const symbol = document.getElementById('symbolInput').value;
    fetch(`/etf-pioneer/api/performance`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ symbol: symbol })
    })
    .then(response => response.json())
    .then(data => {
        let tableData = [{
            type: 'table',
            columnwidth: [400, 500],
            header: {
                values: [["<b>期間</b>"], ["<b>績效</b>"]],
                align: "center",
                line: {width: 1, color: 'black'},
                fill: {color: "skyblue"},
                font: {family: "Arial", size: 12, color: "white"}
            },
            cells: {
                values: [
                    ['今年至今', '1 Week', '1 Month', '3 Months', '6 Months', '1 Year', '2 Years', '3 Years', '5 Years', '10 Years'],
                    [data['YTD'], data['1_week'], data['1_month'], data['3_month'], data['6_month'], data['1_year'],
                     data['2_year'], data['3_year'], data['5_year'], data['10_year']]
                ],
                align: "center",
                line: {color: "blue", width: 1},
                font: {family: "Arial", size: 11, color: ["black"]}
            }
            
        }];

        Plotly.newPlot('performance-table', tableData,{title: 'ETF 績效表現'});
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('performance-table').innerHTML = '表格加載失敗。';
    });
}


// PieChart for top_industry function is called when the user clicks the "Search" button
function fetchTopIndustry() {
    const symbol = document.getElementById('symbolInput').value;
    fetch(`/etf-pioneer/api/top-industry`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ symbol: symbol })
    })
    .then(response => response.json())
    .then(data => {
        let industryPieChart = {
            values: data.map(item => parseFloat(item.ratio)),  // each item has a 'ratio' property
            labels: data.map(item => item.industry), // each item has an 'industry' property
            type: 'pie'
        };

        Plotly.newPlot('industry-chart', [industryPieChart], {title: 'ETF 產業分布'});
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('industry-chart').innerHTML = '圖表加載失敗。';
    });
}

// PieChart for top10_stock function is called when the user clicks the "Search" button
function fetchTop10Stock() {
    const symbol = document.getElementById('symbolInput').value;
    fetch(`/etf-pioneer/api/top10-stock`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ symbol: symbol })
    })
    .then(response => response.json())
    .then(data => {
        let topStockPieChart = {
            values: data.map(item => parseFloat(item.ratio)),  // each item has a 'ratio' property
            labels: data.map(item => item.stock_name), // each item has a 'stock_name' property
            type: 'pie'
        };

        Plotly.newPlot('stock-chart', [topStockPieChart], {title: 'ETF 前十大持股'});
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('stock-chart').innerHTML = '圖表加載失敗。';
    });
}


function fetchETFData(){
    fetchETFOverview();
    fetchPerformance();
    fetchTopIndustry();
    fetchTop10Stock();
}