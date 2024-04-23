// ETF volume ranking
fetch('/etf-pioneer/api/ranking/volume')
  .then(response => response.json())
  .then(volumeData => {
    volumeData.sort((a, b) => b.today_deal_value - a.today_deal_value);
    let volumeChart = {
      x: volumeData.map(item => item.etf_name),
      y: volumeData.map(item => item.today_deal_value),
      type: 'bar',
      marker: {
        color: 'skyblue'
      },
      name: '成交量'
    };
    Plotly.newPlot('volume-chart', [volumeChart], {title: 'ETF 成交量排名'});
  });

// ETF assets ranking
fetch('/etf-pioneer/api/ranking/assets')
  .then(response => response.json())
  .then(assetsData => {
    assetsData.sort((a, b) => b.today_total_assets - a.today_total_assets);
    let assetsChart = {
      x: assetsData.map(item => item.etf_name),
      y: assetsData.map(item => item.today_total_assets),
      type: 'bar',
      marker: {
        color: 'skyblue'
      },
      name: '資產總額'
    };
    Plotly.newPlot('assets-chart', [assetsChart], {title: 'ETF 資產總額排名'});
  });

// ETF holders ranking
fetch('/etf-pioneer/api/ranking/holders')
  .then(response => response.json())
  .then(holdersData => {
    holdersData.sort((a, b) => b.holders - a.holders);
    let holdersChart = {
      x: holdersData.map(item => item.etf_name),
      y: holdersData.map(item => item.holders),
      type: 'bar',
      marker: {
        color: 'skyblue'
      },
      name: '持有 ETF 受益人'
    };
    Plotly.newPlot('holders-chart', [holdersChart], {title: 'ETF 持有人排名'});
  });

// ETF performance ranking
fetch('/etf-pioneer/api/ranking/performance')
  .then(response => response.json())
  .then(performanceData => {
    performanceData.sort((a, b) => b.YTD_performance_rate - a.YTD_performance_rate);
    let performanceChart = {
      x: performanceData.map(item => item.etf_name),
      y: performanceData.map(item => item.YTD_performance_rate),
      type: 'bar',
      marker: {
        color: 'skyblue'
      },
      name: '績效表現'
    };
    Plotly.newPlot('performance-chart', [performanceChart], {title: 'ETF 年初至今績效排名（%）'});
  });


