// ETF volume ranking
fetch('/etf-pioneer/data/etf_ranking_volume')
  .then(response => response.json())
  .then(volumeData => {
    let volumeChart = {
      x: volumeData.map(item => item.etf_name),
      y: volumeData.map(item => item.today_deal_value),
      type: 'bar',
      name: '成交量'
    };
    Plotly.newPlot('volume-chart', [volumeChart]);
  });

// ETF assets ranking
fetch('/etf-pioneer/data/etf_ranking_assets')
  .then(response => response.json())
  .then(assetsData => {
    let assetsChart = {
      x: assetsData.map(item => item.etf_name),
      y: assetsData.map(item => item.today_total_assets),
      type: 'bar',
      name: '資產總額'
    };
    Plotly.newPlot('assets-chart', [assetsChart]);
  });

// ETF holders ranking
fetch('/etf-pioneer/data/etf_ranking_holders')
  .then(response => response.json())
  .then(holdersData => {
    let holdersChart = {
      x: holdersData.map(item => item.etf_name),
      y: holdersData.map(item => item.holders),
      type: 'bar',
      name: '持有 ETF 受益人'
    };
    Plotly.newPlot('holders-chart', [holdersChart]);
  });

// ETF performance ranking
fetch('/etf-pioneer/data/etf_ranking_performance')
  .then(response => response.json())
  .then(performanceData => {
    let performanceChart = {
      x: performanceData.map(item => item.etf_name),
      y: performanceData.map(item => item.YTD_performance_rate),
      type: 'bar',
      name: '績效表現'
    };
    Plotly.newPlot('performance-chart', [performanceChart]);
  });

