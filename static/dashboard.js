// ETF volume ranking
fetch('/etf-pioneer/api/ranking/volume')
  .then(response => response.json())
  .then(volumeData => {
    volumeData.sort((a, b) => b.today_deal_value - a.today_deal_value);
    let hoverTexts = volumeData.map(item => {
      return `ETF 名稱：${item.etf_name}<br>` +
             `ETF 代號：${item.symbol}<br>` +
             `今日成交值（新臺幣元）：${item.today_deal_value.toLocaleString()}<br>` +
             `日均成交值（新臺幣元）（年初至今）：${item.avg_deal_value.toLocaleString()}<br>` +
             `日均成交量（股）（年初至今）：${item.avg_deal_volume.toLocaleString()}`;
    });
    let volumeChart = {
      x: volumeData.map(item => item.symbol),
      y: volumeData.map(item => item.today_deal_value),
      type: 'bar',
      marker: {
        color: 'skyblue'
      },
      hovertext: hoverTexts,
      hoverinfo: 'text',
      name: '成交量'
    };
    let layout={
      title: 'ETF 成交金額排行',
      xaxis:{
        type: 'category',
        title: 'ETF 代號'
      },
      yaxis:{
        title: '今日成交值（新臺幣元）'
      },
      hoverlabel:{
        bgcolor: 'yellow',
        bordercolor: 'blue'
      }
    };
    Plotly.newPlot('volume-chart', [volumeChart], layout);
  });

// ETF assets ranking
fetch('/etf-pioneer/api/ranking/assets')
  .then(response => response.json())
  .then(assetsData => {
    assetsData.sort((a, b) => b.today_total_assets - a.today_total_assets);
    let hoverTexts = assetsData.map(item => {
      return `ETF 名稱：${item.etf_name}<br>` +
             `ETF 代號：${item.symbol}<br>` +
             `今日資產規模（新臺幣元）：${item.today_total_assets.toLocaleString()}<br>`;
    });
    let assetsChart = {
      x: assetsData.map(item => item.symbol),
      y: assetsData.map(item => item.today_total_assets),
      type: 'bar',
      marker: {
        color: 'skyblue'
      },
      hovertext: hoverTexts,
      hoverinfo: 'text',
      name: '資產總額'
    };
    let layout={
      title: 'ETF 資產規模排行',
      xaxis:{
        type: 'category',
        title: 'ETF 代號'
      },
      yaxis:{
        title: '今日資產規模（新臺幣元）'
      },
       hoverlabel:{
        bgcolor: 'yellow',
        bordercolor: 'blue'
      }
    };
    Plotly.newPlot('assets-chart', [assetsChart], layout);
  });

// ETF holders ranking
fetch('/etf-pioneer/api/ranking/holders')
  .then(response => response.json())
  .then(holdersData => {
    holdersData.sort((a, b) => b.holders - a.holders);
    let hoverTexts = holdersData.map(item => {
      return `ETF 名稱：${item.etf_name}<br>` +
             `ETF 代號：${item.symbol}<br>` +
             `受益人數（人）：${item.holders.toLocaleString()}<br>`;
    });
    let holdersChart = {
      x: holdersData.map(item => item.symbol),
      y: holdersData.map(item => item.holders),
      type: 'bar',
      marker: {
        color: 'skyblue'
      },
      hovertext: hoverTexts,
      hoverinfo: 'text',
      name: '持有 ETF 受益人'
    };
    let layout={
      title: 'ETF 持有（受益）人數排行',
      xaxis:{
        type: 'category',
        title: 'ETF 代號'
      },
      yaxis:{
        title: '受益人數（人）'
      },
       hoverlabel:{
        bgcolor: 'yellow',
        bordercolor: 'blue'
      }
    };
    Plotly.newPlot('holders-chart', [holdersChart], layout);
  });

// ETF performance ranking
fetch('/etf-pioneer/api/ranking/performance')
  .then(response => response.json())
  .then(performanceData => {
    performanceData.sort((a, b) => b.YTD_performance_rate - a.YTD_performance_rate);
    let hoverTexts = performanceData.map(item => {
      return `ETF 名稱：${item.etf_name}<br>` +
             `ETF 代號：${item.symbol}<br>` +
             `年初至今績效：${item.YTD_performance_rate + "%"} <br>`;
    });
    let performanceChart = {
      x: performanceData.map(item => item.symbol),
      y: performanceData.map(item => item.YTD_performance_rate),
      type: 'bar',
      marker: {
        color: 'skyblue'
      },
      hovertext: hoverTexts,
      hoverinfo: 'text',
      name: '績效表現'
    };
    let layout={
      title: 'ETF 年初至今績效排名（%）',
      xaxis:{
        type: 'category',
        title: 'ETF 代號'
      },
      yaxis:{
        title: '年初至今績效排名（%）'
      },
       hoverlabel:{
        bgcolor: 'yellow',
        bordercolor: 'blue'
      }
    };
    Plotly.newPlot('performance-chart', [performanceChart], layout);
  });


