// ETF volume ranking
fetch('/etf-pioneer/api/ranking/volume')
  .then(response => response.json())
  .then(volumeData => {
    volumeData.sort((a, b) => b.today_deal_value - a.today_deal_value);
    let hoverTexts = volumeData.map(item => {
      return `ETF 名稱：${item.etf_name}<br>` +
             `ETF 代號：${item.symbol}<br>` +
             `今日成交值（新臺幣百萬元）：${(item.today_deal_value/1000000).toLocaleString()}<br>` +
             `日均成交值（新臺幣百萬元）（年初至今）：${(item.avg_deal_value/1000000).toLocaleString()}<br>` +
             `日均成交量（百萬股）（年初至今）：${(item.avg_deal_volume/1000000).toLocaleString()}`;
    });
    let volumeChart = {
      x: volumeData.map(item => item.symbol),
      y: volumeData.map(item => item.today_deal_value/1000000),
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
        title: '今日成交值（新臺幣百萬元）'
      },
      hoverlabel:{
        bgcolor: 'lightgrey',
        bordercolor: 'blue'
      }
    };
    let updateTime = volumeData.length > 0 ? volumeData[0].data_updated_date : '未知';
    Plotly.newPlot('volume-chart', [volumeChart], layout);
    document.getElementById('volume-data-updated-time').textContent = `資料來源：臺灣證券交易所，來源資料更新時間：${updateTime}`;
  });

// ETF assets ranking
fetch('/etf-pioneer/api/ranking/assets')
  .then(response => response.json())
  .then(assetsData => {
    assetsData.sort((a, b) => b.today_total_assets - a.today_total_assets);
    let hoverTexts = assetsData.map(item => {
      return `ETF 名稱：${item.etf_name}<br>` +
             `ETF 代號：${item.symbol}<br>` +
             `今日資產規模（新臺幣百萬元）：${(item.today_total_assets/1000000).toLocaleString()}<br>`;
    });
    let assetsChart = {
      x: assetsData.map(item => item.symbol),
      y: assetsData.map(item => item.today_total_assets/1000000),
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
        title: '今日資產規模（新臺幣百萬元）'
      },
       hoverlabel:{
        bgcolor: 'lightgrey',
        bordercolor: 'blue'
      }
    };
    let updateTime = assetsData.length > 0 ? assetsData[0].data_updated_date : '未知';
    Plotly.newPlot('assets-chart', [assetsChart], layout);
    document.getElementById('assets-data-updated-time').textContent = `資料來源：臺灣證券交易所，來源資料更新時間：${updateTime}`;
  });

// ETF holders ranking
fetch('/etf-pioneer/api/ranking/holders')
  .then(response => response.json())
  .then(holdersData => {
    holdersData.sort((a, b) => b.holders - a.holders);
    let hoverTexts = holdersData.map(item => {
      return `ETF 名稱：${item.etf_name}<br>` +
             `ETF 代號：${item.symbol}<br>` +
             `受益人數（千人）：${(item.holders/1000).toLocaleString()}<br>`;
    });
    let holdersChart = {
      x: holdersData.map(item => item.symbol),
      y: holdersData.map(item => item.holders/1000),
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
        title: '受益人數（千人）'
      },
       hoverlabel:{
        bgcolor: 'lightgrey',
        bordercolor: 'blue'
      }
    };
    let updatedTime = holdersData.length > 0 ? holdersData[0].data_updated_date : '未知';
    Plotly.newPlot('holders-chart', [holdersChart], layout);
    document.getElementById('holders-data-updated-time').textContent = `資料來源：臺灣證券交易所，來源資料更新時間：${updatedTime}`;
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
        bgcolor: 'lightgrey',
        bordercolor: 'blue'
      }
    };
    let updatedTime = performanceData.length > 0 ? performanceData[0].data_updated_date : '未知';
    Plotly.newPlot('performance-chart', [performanceChart], layout);
    document.getElementById('performance-data-updated-time').textContent = `資料來源：臺灣證券交易所，來源資料更新時間：${updatedTime}`;
  });


// search and compare ETFs
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('etfSearchForm');
    const compareForm = document.getElementById('etfCompareForm');

    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const symbol = document.getElementById('symbolInput').value;
            if (symbol) {
                window.location.href = `/search-results?symbol=${symbol}`;
            } else {
                alert("請輸入正確的ETF代號");
            }
        });
}
    if (compareForm) {
        compareForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const symbol = document.getElementById('symbolInput').value;
            const compareSymbol = document.getElementById('compareInput').value;
            if (symbol && compareSymbol) {
                window.location.href = `/search-results?symbol=${symbol}&compareSymbol=${compareSymbol}`;
            } else if(compareSymbol){
                window.location.href = `/search-results?symbol=${compareSymbol}`;
            }else{
                alert("請輸入正確的ETF代號");
            }
        }); 
}
});

// plotly drawing functions for ETF search and compare results

function renderPerformanceTable(data, tableId,updateTimeId) {
        
        const numRows = data.length;
        const rowHeight =30;
        const graphHeight = numRows * rowHeight;

        let layout = {
            title: 'ETF 績效表',
            responsive: true,
            height: graphHeight
        };
        let tableData = {
            type: 'table',
            header: {
                values: [["期 間"], ["績 效"]],
                align: "center",
                line: {width: 2, color: 'black'},
                fill: {color: "skyblue"},
                font: {family: "Arial", size: 20, color: "white"},
                width: [1, 1],
                height: 30


            },
            cells: {
                values: [
                    ['今年至今', '1 週', '1 個月', '3 個月', '6 個月', '1 年（年化報酬率）', '2 年（年化報酬率）', '3 年（年化報酬率）', '5 年（年化報酬率）', '10 年（年化報酬率）'],
                    [data.YTD, data['1_week'], data['1_month'], data['3_month'], data['6_month'], data['1_year'], data['2_year'], data['3_year'], data['5_year'], data['10_year']]
                ],
                align: "center",
                line: {color: "blue", width: 2},
                font: {family: "Arial", size: 18, color: ["black"]},
                width: [1, 1],
                height: 30
            }
        };
        let updateTime = '';
        if (data && data.data_updated_date == 'NULL') {
            updateTime = '未知';
        } else if (data) {
            updateTime = data.data_updated_date;
        }   
        Plotly.newPlot(tableId, [tableData], layout);
        document.getElementById(updateTimeId).textContent = `來源資料更新時間：${updateTime}`;
}

function renderTopIndustryChart(data, chartId,updateTimeId) {
        let hoverTexts = data.map(item => {
            return `ETF 代號：${item.symbol}<br>` +
             `產業名稱：${item.industry}<br>`;
    });
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
            type: 'pie',
            hovertext: hoverTexts,
            hoverinfo: 'text',
            hole: 0.6, // donut chart
            name: '產業分布'
        };
        let updateTime = data.length > 0 ? data[0].data_updated_date : '未知';
        Plotly.newPlot(chartId, [industryPieChart], layout);
        document.getElementById(updateTimeId).textContent = `來源資料更新時間：${updateTime}`;
     }

function renderTop10StockChart(data,chartId, updateTimeId) {
        let hoverTexts = data.map(item => {
            return `前十大成分股排行：${item.ranking}<br>` +
             `股票名稱：${item.stock_name}<br>`+
             `佔 ETF 比例：${item.ratio}<br>`;
    });
        let stockData = data.map(item => ({
            label: item.stock_name,
            value: parseFloat(item.ratio)
        }));
        let layout = {
            title: 'ETF 前十大成分股',
            responsive: true
        };
        let topStockPieChart = {
            values: stockData.map(item => item.value),
            labels: stockData.map(item => item.label),
            type: 'pie',
            hovertext: hoverTexts,
            hoverinfo: 'text',
            hole: 0.6, // donut chart
            name: '前十大成分股'
        };
        let updateTime = data.length > 0 ? data[0].data_updated_date : '未知';
        Plotly.newPlot(chartId, [topStockPieChart], layout);
        document.getElementById(updateTimeId).textContent = `來源資料更新時間：${updateTime}`;
    }

// drop down menu
document.addEventListener("DOMContentLoaded", function () {
    setupDropdown("symbolInput", "etfSearchDropdown");
    setupDropdown("compareInput", "etfCompareDropdown");
});

function setupDropdown(inputId, dropdownId) {
    let input = document.getElementById(inputId);
    let dropdown = document.createElement("div");
    dropdown.id = dropdownId;
    dropdown.className = "dropdown-content";
    input.parentNode.insertBefore(dropdown, input.nextSibling);
    
    input.addEventListener("input", function () {
        let searchValue = this.value.toLowerCase();
        dropdown.innerHTML = ""; // Clear previous options
        if (searchValue) {
            // Simulated search results
            let optionsList = ["元大台灣50【0050】",
                                "元大中型100【0051】",
                                "富邦科技【0052】",
                                "元大電子【0053】",
                                "元大MSCI金融【0055】",
                                "元大高股息【0056】",
                                "富邦摩台【0057】",
                                "元大寶滬深【0061】",
                                "元大富櫃50【006201】",
                                "元大MSCI台灣【006203】",
                                "永豐臺灣加權【006204】",
                                "富邦上証【006205】",
                                "元大上證50【006206】",
                                "復華滬深【006207】",
                                "富邦台50【006208】",
                                "富邦上証+R【00625K】",
                                "元大台灣50正2【00631L】",
                                "元大台灣50反1【00632R】",
                                "富邦上証正2【00633L】",
                                "富邦上証反1【00634R】",
                                "期元大S&P黃金【00635U】",
                                "國泰中國A50【00636】",
                                "國泰中國A50+U【00636K】",
                                "元大滬深300正2【00637L】",
                                "元大滬深300反1【00638R】",
                                "富邦深100【00639】",
                                "富邦日本正2【00640L】",
                                "富邦日本反1【00641R】",
                                "期元大S&P石油【00642U】",
                                "群益深証中小【00643】",
                                "群益深証中小+R【00643K】",
                                "富邦日本【00645】",
                                "元大S&P500【00646】",
                                "元大S&P500正2【00647L】",
                                "元大S&P500反1【00648R】",
                                "復華香港正2【00650L】",
                                "復華香港反1【00651R】",
                                "富邦印度【00652】",
                                "富邦印度正2【00653L】",
                                "富邦印度反1【00654R】",
                                "國泰中國A50正2【00655L】",
                                "國泰中國A50反1【00656R】",
                                "國泰日經225【00657】",
                                "國泰日經225+U【00657K】",
                                "元大歐洲50【00660】",
                                "元大日經225【00661】",
                                "富邦NASDAQ【00662】",
                                "國泰臺灣加權正2【00663L】",
                                "國泰臺灣加權反1【00664R】",
                                "富邦恒生國企正2【00665L】",
                                "富邦恒生國企反1【00666R】",
                                "國泰美國道瓊【00668】",
                                "國泰美國道瓊+U【00668K】",
                                "國泰美國道瓊反1【00669R】",
                                "富邦NASDAQ正2【00670L】",
                                "富邦NASDAQ反1【00671R】",
                                "期元大S&P原油反1【00673R】",
                                "期元大S&P黃金反1【00674R】",
                                "富邦臺灣加權正2【00675L】",
                                "富邦臺灣加權反1【00676R】",
                                "群益那斯達克生技【00678】",
                                "元大美債20年【00679B】",
                                "元大美債20正2【00680L】",
                                "元大美債20反1【00681R】",
                                "期元大美元指數【00682U】",
                                "期元大美元指正2【00683L】",
                                "期元大美元指反1【00684R】",
                                "群益臺灣加權正2【00685L】",
                                "群益臺灣加權反1【00686R】",
                                "國泰20年美債【00687B】",
                                "國泰20年美債正2【00688L】",
                                "國泰20年美債反1【00689R】",
                                "兆豐藍籌30【00690】",
                                "富邦公司治理【00692】",
                                "期街口S&P黃豆【00693U】",
                                "富邦美債1-3【00694B】",
                                "富邦美債7-10【00695B】",
                                "富邦美債20年【00696B】",
                                "元大美債7-10【00697B】",
                                "富邦恒生國企【00700】",
                                "國泰股利精選30【00701】",
                                "國泰標普低波高息【00702】",
                                "台新MSCI中國【00703】",
                                "期元大S&P日圓正2【00706L】",
                                "期元大S&P日圓反1【00707R】",
                                "期元大S&P黃金正2【00708L】",
                                "富邦歐洲【00709】",
                                "復華彭博非投等債【00710B】",
                                "復華彭博新興債【00711B】",
                                "復華富時不動產【00712】",
                                "元大台灣高息低波【00613】",
                                "群益道瓊美國地產【00714】",
                                "期街口布蘭特正2【00715L】",
                                "富邦美國特別股【00717】",
                                "富邦中國政策債【00718B】",
                                "元大美債1-3【00719B】",
                                "元大投資級公司債【00720B】",
                                "元大中國債3-5【00721B】",
                                "群益投資級電信債【00722B】",
                                "群益投資級科技債【00723B】",
                                "群益投資級金融債【00724B】",
                                "國泰投資級公司債【00725B】",
                                "國泰5Y+新興債【00726B】",
                                "國泰1-5Y非投等債【00727B】",
                                "第一金工業30【00728】",
                                "富邦臺灣優質高息【00730】",
                                "復華富時高息低波【00731】",
                                "富邦臺灣中小【00733】",
                                "台新JPM新興債【00734B】",
                                "國泰臺韓科技【00735】",
                                "國泰新興市場【00736】",
                                "國泰AI+Robo【00737】",
                                "期元大道瓊白銀【00738U】",
                                "元大MSCIA股【00739】",
                                "富邦全球投等債【00740B】",
                                "富邦全球非投等債【00741B】",
                                "富邦A級公司債【00746B】",
                                "凱基新興債10+【00749B】",
                                "凱基科技債10+【00750B】",
                                "元大AAA至A公司債【00751B】",
                                "中信中國50【00752】",
                                "中信中國50正2【00753L】",
                                "群益AAA-AA公司債【00754B】",
                                "群益投資級公用債【00755B】",
                                "群益投等新興公債【00756B】",
                                "統一FANG+【00757】",
                                "復華能源債【00758B】",
                                "復華製藥債【00759B】",
                                "復華新興企業債【00760B】",
                                "國泰A級公司債【00761B】",
                                "元大全球AI【00762】",
                                "期街口道瓊銅【00763U】",
                                "群益25年美債【00764B】",
                                "復華20年美債【00768B】",
                                "國泰北美科技【00770】",
                                "元大US高息特別股【00771】",
                                "中信高評級公司債【00772B】",
                                "中信優先金融債【00773B】",
                                "新光投等債15+【00775B】",
                                "凱基AAA至A公司債【00777B】",
                                "凱基金融債20+【00778B】",
                                "凱基美債25+【00779B】",
                                "國泰A級金融債【00780B】",
                                "國泰A級科技債【00781B】",
                                "國泰A級公用債【00782B】",
                                "富邦中証500【00783】",
                                "富邦中國投等債【00784B】",
                                "富邦金融投等債【00785B】",
                                "元大10年IG銀行債【00786B】",
                                "元大10年IG醫療債【00787B】",
                                "元大10年IG電能債【00788B】",
                                "復華公司債A3【00789B】",
                                "復華次順位金融債【00790B】",
                                "復華信用債1-5【00791B】",
                                "群益A級公司債【00792B】",
                                "群益AAA-A醫療債【00793B】",
                                "群益7+中國政金債【00794B】",
                                "中信美國公債20年【00795B】",
                                "國泰A級醫療債【00799B】",
                                "國泰費城半導體【00830】",
                                "新光美債1-3【00831B】",
                                "第一金金融債10+【00834B】",
                                "永豐10年A公司債【00836B】",
                                "凱基IG精選15+【00840B】",
                                "凱基AAA-AA公司債【00841B】",
                                "台新美元銀行債【00842B】",
                                "新光15年IG金融債【00844B】",
                                "富邦新興投等債【00845B】",
                                "富邦歐洲銀行債【00846B】",
                                "中信美國市政債【00847B】",
                                "中信新興亞洲債【00848B】",
                                "中信EM主權債0-5【00849B】",
                                "元大臺灣ESG永續【00850】",
                                "台新全球AI【00851】",
                                "國泰美國道瓊正2【00852L】",
                                "統一美債10年Aa-A【00853B】",
                                "永豐1-3年美公債【00856B】",
                                "永豐20年美公債【00857B】",
                                "永豐美國500大【00858】",
                                "群益0-1年美債【00859B】",
                                "群益1-5Y投資級債【00860B】",
                                "元大全球未來通訊【00861】",
                                "中信投資級公司債【00862B】",
                                "中信全球電信債【00863B】",
                                "中信美國公債0-1【00864B】",
                                "國泰US短期公債【00865B】",
                                "新光A-BBB電信債【00867B】",
                                "元大15年EM主權債【00870B】",
                                "國泰網路資安【00875】",
                                "元大全球5G【00876】",
                                "復華中國5G【00877】",
                                "國泰永續高股息【00878】",
                                "國泰台灣5G+【00881】",
                                "中信中國高股息【00882】",
                                "中信ESG投資級債【00883B】",
                                "中信低碳新興債【00884B】",
                                "富邦越南【00885】",
                                "永豐美國科技【00886】",
                                "永豐中國科技50大【00887】",
                                "永豐台灣ESG【00888】",
                                "凱基ESGBBB債15+【00890B】",
                                "中信關鍵半導體【00891】",
                                "富邦台灣半導體【00892】",
                                "國泰智能電動車【00893】",
                                "中信小資高價30【00894】",
                                "富邦未來車【00895】",
                                "中信綠能及電動車【00896】",
                                "富邦基因免疫生技【00897】",
                                "國泰基因免疫革命【00898】",
                                "FT潔淨能源【00899】",
                                "富邦特選高股息30【00900】",
                                "永豐智能車供應鏈【00901】",
                                "中信電池及儲能【00902】",
                                "富邦元宇宙【00903】",
                                "新光臺灣半導體30【00904】",
                                "FT臺灣Smart【00905】",
                                "永豐優息存股【00907】",
                                "富邦入息REITs+【00908】",
                                "國泰數位支付服務【00909】",
                                "第一金太空衛星【00910】",
                                "兆豐洲際半導體【00911】",
                                "中信臺灣智慧50【00912】",
                                "兆豐台灣晶圓製造【00913】",
                                "凱基優選高股息30【00915】",
                                "國泰全球品牌50【00916】",
                                "中信特選金融【00917】",
                                "大華優利高填息30【00918】",
                                "群益台灣精選高息【00919】",
                                "富邦ESG綠色電力【00920】",
                                "兆豐龍頭等權重【00921】",
                                "國泰台灣領袖50【00922】",
                                "群益台ESG低碳50【00923】",
                                "復華S&P500成長【00924】",
                                "新光標普電動車【00925】",
                                "凱基全球菁英55【00926】",
                                "群益半導體收益【00927】",
                                "中信上櫃ESG30【00928】",
                                "復華台灣科技優息【00929】",
                                "永豐ESG低碳高息【00930】",
                                "統一美債20年【00931B】",
                                "兆豐永續高息等權【00932】",
                                "國泰10Y+金融債【00933B】",
                                "中信成長高股息【00934】",
                                "野村臺灣新科技50【00935】",
                                "台新永續高息中小【00936】",
                                "群益ESG投等債20+【00937B】",
                                "統一台灣高息動能【00939】",
                                "元大台灣價值高息【00940】"];


            optionsList.forEach(function (option) {
                if (option.toLowerCase().includes(searchValue)) {
                    let div = document.createElement("div");
                    div.textContent = option;
                    div.onclick = function() {
                        let match = option.match(/【(\d+)】/); // 提取括號內的數字
                        if (match && match[1]) {
                            input.value = match[1]; // 設置輸入框的值為數字代號
                            dropdown.style.display = "none"; // 隱藏下拉選單
                        }
                        };
                    dropdown.appendChild(div);
                }
            });
            dropdown.style.display = "block";
        } else {
            dropdown.style.display = "none";
        }
    });
    
    // Hide dropdown when clicking elsewhere
    document.addEventListener("click", function(event) {
        if (event.target !== input) {
            dropdown.style.display = "none";
        }
    });
}


// stock to ETF page
function fetchStockETFData(){
    console.log("fetchStockETFData called");
    const stockCode = document.getElementById('stockInput').value;
    if (!stockCode) {
        alert("請輸入股票代號");
        return;
    }
    // redirect to the stock to ETF page
    window.location.href = `/etf-pioneer/api/stock-to-etf?stock_code=${stockCode}`;
}


// news page
function fetchNewsTitlesForWordCloud() {
    const startDateInput = document.getElementById('startDate');
    const startDate = startDateInput.value;
    if (!startDate) {
        alert('請選擇日期。');
        return;
    }
    const endDate = new Date(startDate);
    endDate.setDate(endDate.getDate() + 7); // 7 days after the start date
    const formattedEndDate = endDate.toISOString().split('T')[0];
    
    // redirect to the news page
    window.location.href = `/etf-pioneer/api/news-wordcloud?start_date=${startDate}&end_date=${formattedEndDate}`;
}