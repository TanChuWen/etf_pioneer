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
        // data = { ratio: [array_of_values], industry: [array_of_labels] }
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

// Table for ETF reverse lookup function is called when the user clicks the "Search" button

function fetchETFData(){
    fetchETFOverview();
    fetchTopIndustry();
}