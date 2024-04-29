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
            const isValidOption = optionsList.some(option => option.includes(symbol));
            if (!symbol) {
                alert("請輸入正確的ETF代號");
            } else if (!isValidOption) {
                alert("請輸入正確的ETF代號");
            } else {
                window.location.href = `/search-results?symbol=${symbol}`;
            }
        });
}
    if (compareForm) {
        compareForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const symbol = document.getElementById('symbolInput').value;
            const compareSymbol = document.getElementById('compareInput').value;
            const isValidOption = optionsList.some(option => option.includes(symbol));
            const isValidCompareOption = optionsList.some(option => option.includes(compareSymbol));
            if (symbol && compareSymbol) {
              if (isValidOption && isValidCompareOption) {
                window.location.href = `/search-results?symbol=${symbol}&compareSymbol=${compareSymbol}`;
            } else {
                alert("請輸入正確的ETF代號");
            }
            }else if (symbol && isValidOption) {
                window.location.href = `/search-results?symbol=${symbol}`;
            } else if (compareSymbol && isValidCompareOption) {
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
let optionsList = ["元大台灣50【0050】","元大中型100【0051】", "富邦科技【0052】","元大電子【0053】","元大MSCI金融【0055】","元大高股息【0056】","富邦摩台【0057】","元大寶滬深【0061】","元大富櫃50【006201】",
"元大MSCI台灣【006203】","永豐臺灣加權【006204】","富邦上証【006205】","元大上證50【006206】","復華滬深【006207】","富邦台50【006208】","富邦上証+R【00625K】",
"元大台灣50正2【00631L】","元大台灣50反1【00632R】","富邦上証正2【00633L】","富邦上証反1【00634R】","期元大S&P黃金【00635U】","國泰中國A50【00636】","國泰中國A50+U【00636K】","元大滬深300正2【00637L】",
"元大滬深300反1【00638R】","富邦深100【00639】","富邦日本正2【00640L】","富邦日本反1【00641R】","期元大S&P石油【00642U】","群益深証中小【00643】","群益深証中小+R【00643K】","富邦日本【00645】",
"元大S&P500【00646】","元大S&P500正2【00647L】","元大S&P500反1【00648R】","復華香港正2【00650L】","復華香港反1【00651R】","富邦印度【00652】","富邦印度正2【00653L】","富邦印度反1【00654R】",
"國泰中國A50正2【00655L】","國泰中國A50反1【00656R】","國泰日經225【00657】","國泰日經225+U【00657K】","元大歐洲50【00660】","元大日經225【00661】","富邦NASDAQ【00662】","國泰臺灣加權正2【00663L】",
"國泰臺灣加權反1【00664R】","富邦恒生國企正2【00665L】","富邦恒生國企反1【00666R】","國泰美國道瓊【00668】","國泰美國道瓊+U【00668K】","國泰美國道瓊反1【00669R】","富邦NASDAQ正2【00670L】","富邦NASDAQ反1【00671R】",
"期元大S&P原油反1【00673R】","期元大S&P黃金反1【00674R】","富邦臺灣加權正2【00675L】","富邦臺灣加權反1【00676R】","群益那斯達克生技【00678】","元大美債20年【00679B】","元大美債20正2【00680L】","元大美債20反1【00681R】",
"期元大美元指數【00682U】","期元大美元指正2【00683L】","期元大美元指反1【00684R】","群益臺灣加權正2【00685L】","群益臺灣加權反1【00686R】","國泰20年美債【00687B】","國泰20年美債正2【00688L】",
"國泰20年美債反1【00689R】","兆豐藍籌30【00690】","富邦公司治理【00692】","期街口S&P黃豆【00693U】","富邦美債1-3【00694B】","富邦美債7-10【00695B】","富邦美債20年【00696B】","元大美債7-10【00697B】",
"富邦恒生國企【00700】","國泰股利精選30【00701】","國泰標普低波高息【00702】","台新MSCI中國【00703】","期元大S&P日圓正2【00706L】","期元大S&P日圓反1【00707R】","期元大S&P黃金正2【00708L】","富邦歐洲【00709】",
"復華彭博非投等債【00710B】","復華彭博新興債【00711B】","復華富時不動產【00712】","元大台灣高息低波【00613】","群益道瓊美國地產【00714】","期街口布蘭特正2【00715L】","富邦美國特別股【00717】","富邦中國政策債【00718B】",
"元大美債1-3【00719B】","元大投資級公司債【00720B】","元大中國債3-5【00721B】","群益投資級電信債【00722B】","群益投資級科技債【00723B】","群益投資級金融債【00724B】","國泰投資級公司債【00725B】","國泰5Y+新興債【00726B】",
"國泰1-5Y非投等債【00727B】","第一金工業30【00728】","富邦臺灣優質高息【00730】","復華富時高息低波【00731】","富邦臺灣中小【00733】","台新JPM新興債【00734B】","國泰臺韓科技【00735】","國泰新興市場【00736】",
"國泰AI+Robo【00737】","期元大道瓊白銀【00738U】","元大MSCIA股【00739】","富邦全球投等債【00740B】","富邦全球非投等債【00741B】","富邦A級公司債【00746B】","凱基新興債10+【00749B】","凱基科技債10+【00750B】",
"元大AAA至A公司債【00751B】","中信中國50【00752】","中信中國50正2【00753L】","群益AAA-AA公司債【00754B】","群益投資級公用債【00755B】","群益投等新興公債【00756B】","統一FANG+【00757】","復華能源債【00758B】",
"復華製藥債【00759B】","復華新興企業債【00760B】","國泰A級公司債【00761B】","元大全球AI【00762】","期街口道瓊銅【00763U】","群益25年美債【00764B】","復華20年美債【00768B】","國泰北美科技【00770】",
"元大US高息特別股【00771】","中信高評級公司債【00772B】","中信優先金融債【00773B】","新光投等債15+【00775B】","凱基AAA至A公司債【00777B】","凱基金融債20+【00778B】","凱基美債25+【00779B】","國泰A級金融債【00780B】",
"國泰A級科技債【00781B】","國泰A級公用債【00782B】","富邦中証500【00783】","富邦中國投等債【00784B】","富邦金融投等債【00785B】","元大10年IG銀行債【00786B】","元大10年IG醫療債【00787B】","元大10年IG電能債【00788B】",
"復華公司債A3【00789B】","復華次順位金融債【00790B】","復華信用債1-5【00791B】","群益A級公司債【00792B】","群益AAA-A醫療債【00793B】","群益7+中國政金債【00794B】","中信美國公債20年【00795B】","國泰A級醫療債【00799B】",
"國泰費城半導體【00830】","新光美債1-3【00831B】","第一金金融債10+【00834B】","永豐10年A公司債【00836B】","凱基IG精選15+【00840B】","凱基AAA-AA公司債【00841B】","台新美元銀行債【00842B】","新光15年IG金融債【00844B】",
"富邦新興投等債【00845B】","富邦歐洲銀行債【00846B】","中信美國市政債【00847B】","中信新興亞洲債【00848B】","中信EM主權債0-5【00849B】","元大臺灣ESG永續【00850】","台新全球AI【00851】","國泰美國道瓊正2【00852L】",
"統一美債10年Aa-A【00853B】","永豐1-3年美公債【00856B】","永豐20年美公債【00857B】","永豐美國500大【00858】","群益0-1年美債【00859B】","群益1-5Y投資級債【00860B】","元大全球未來通訊【00861】","中信投資級公司債【00862B】",
"中信全球電信債【00863B】","中信美國公債0-1【00864B】","國泰US短期公債【00865B】","新光A-BBB電信債【00867B】","元大15年EM主權債【00870B】","國泰網路資安【00875】","元大全球5G【00876】","復華中國5G【00877】",
"國泰永續高股息【00878】","國泰台灣5G+【00881】","中信中國高股息【00882】","中信ESG投資級債【00883B】","中信低碳新興債【00884B】","富邦越南【00885】","永豐美國科技【00886】","永豐中國科技50大【00887】",
"永豐台灣ESG【00888】","凱基ESGBBB債15+【00890B】","中信關鍵半導體【00891】","富邦台灣半導體【00892】","國泰智能電動車【00893】","中信小資高價30【00894】","富邦未來車【00895】","中信綠能及電動車【00896】",
"富邦基因免疫生技【00897】","國泰基因免疫革命【00898】","FT潔淨能源【00899】","富邦特選高股息30【00900】","永豐智能車供應鏈【00901】","中信電池及儲能【00902】","富邦元宇宙【00903】","新光臺灣半導體30【00904】",
"FT臺灣Smart【00905】","永豐優息存股【00907】","富邦入息REITs+【00908】","國泰數位支付服務【00909】","第一金太空衛星【00910】","兆豐洲際半導體【00911】","中信臺灣智慧50【00912】","兆豐台灣晶圓製造【00913】",
"凱基優選高股息30【00915】","國泰全球品牌50【00916】","中信特選金融【00917】","大華優利高填息30【00918】","群益台灣精選高息【00919】","富邦ESG綠色電力【00920】","兆豐龍頭等權重【00921】","國泰台灣領袖50【00922】",
"群益台ESG低碳50【00923】","復華S&P500成長【00924】","新光標普電動車【00925】","凱基全球菁英55【00926】","群益半導體收益【00927】","中信上櫃ESG30【00928】","復華台灣科技優息【00929】","永豐ESG低碳高息【00930】",
"統一美債20年【00931B】","兆豐永續高息等權【00932】","國泰10Y+金融債【00933B】","中信成長高股息【00934】","野村臺灣新科技50【00935】","台新永續高息中小【00936】","群益ESG投等債20+【00937B】","統一台灣高息動能【00939】",
"元大台灣價值高息【00940】"];
function setupDropdown(inputId, dropdownId) {
    let input = document.getElementById(inputId);
    let dropdown = document.createElement("div");
    dropdown.id = dropdownId;
    dropdown.className = "dropdown-content";
    input.parentNode.insertBefore(dropdown, input.nextSibling);
    
    input.addEventListener("input", function () {
        let searchValue = this.value.toLowerCase();
        dropdown.innerHTML = ""; // clear previous options
        if (searchValue) {
            optionsList.forEach(function (option) {
                if (option.toLowerCase().includes(searchValue)) {
                    let div = document.createElement("div");
                    div.textContent = option;
                    div.onclick = function() {
                        let match = option.match(/【(.*?)】/); // extract the content in the brackets
                        if (match && match[1]) {
                            input.value = match[1]; // set input value to the number
                            dropdown.style.display = "none"; // hide dropdown list
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
    
    // hide dropdown when clicking elsewhere
    document.addEventListener("click", function(event) {
        if (event.target !== input) {
            dropdown.style.display = "none";
        }
    });
}


let stockOptionsList = ["1101 台泥","1102 亞泥","1103 嘉泥","1104 環泥","1108 幸福","1109 信大","1110 東泥","1201 味全","1203 味王","1210 大成","1213 大飲","1215 卜蜂","1216 統一","1217 愛之味","1218 泰山","1219 福壽","1220 台榮","1225 福懋油","1227 佳格","1229 聯華","1231 聯華食","1232 大統益","1233 天仁","1234 黑松","1235 興泰","1236 宏亞","1256 鮮活果汁-KY","1301 台塑","1303 南亞","1304 台聚","1305 華夏","1307 三芳","1308 亞聚","1309 台達化","1310 台苯","1312 國喬","1313 聯成","1314 中石化","1315 達新","1316 上曜","1319 東陽","1321 大洋","1323 永裕","1324 地球","1325 恆大","1326 台化","1337 再生-KY","1338 廣華-KY","1339 昭輝","1340 勝悅-KY","1341 富林-KY","1342 八貫","1402 遠東新","1409 新纖","1410 南染","1413 宏洲","1414 東和","1416 廣豐","1417 嘉裕","1418 東華","1419 新紡","1423 利華","1432 大魯閣","1434 福懋","1435 中福","1436 華友聯","1437 勤益控","1438 三地開發","1439 雋揚","1440 南紡","1441 大東","1442 名軒","1443 立益物流","1444 力麗","1445 大宇","1446 宏和","1447 力鵬","1449 佳和","1451 年興","1452 宏益","1453 大將","1454 台富","1455 集盛","1456 怡華","1457 宜進","1459 聯發","1460 宏遠","1463 強盛","1464 得力","1465 偉全","1466 聚隆","1467 南緯","1468 昶和","1470 大統新創","1471 首利","1472 三洋實業","1473 台南","1474 弘裕","1475 業旺","1476 儒鴻","1477 聚陽","1503 士電","1504 東元","1506 正道","1512 瑞利","1513 中興電","1514 亞力","1515 力山","1516 川飛","1517 利奇","1519 華城","1521 大億","1522 堤維西","1524 耿鼎","1525 江申","1526 日馳","1527 鑽全","1528 恩德","1529 樂事綠能","1530 亞崴","1531 高林股","1532 勤美","1533 車王電","1535 中宇","1536 和大","1537 廣隆","1538 正峰","1539 巨庭","1540 喬福","1541 錩泰","1558 伸興","1560 中砂","1568 倉佑","1582 信錦","1583 程泰","1587 吉茂","1589 永冠-KY","1590 亞德客-KY","1597 直得","1598 岱宇","1603 華電","1604 聲寶","1605 華新","1608 華榮","1609 大亞","1611 中電","1612 宏泰","1614 三洋電","1615 大山","1616 億泰","1617 榮星","1618 合機","1626 艾美特-KY","1701 中化","1702 南僑","1707 葡萄王","1708 東鹼","1709 和益","1710 東聯","1711 永光","1712 興農","1713 國化","1714 和桐","1717 長興","1718 中纖","1720 生達","1721 三晃","1722 台肥","1723 中碳","1725 元禎","1726 永記","1727 中華化","1730 花仙子","1731 美吾華","1732 毛寶","1733 五鼎","1734 杏輝","1735 日勝化","1736 喬山","1737 臺鹽","1752 南光","1760 寶齡富錦","1762 中化生","1773 勝一","1776 展宇","1783 和康生","1786 科妍","1789 神隆","1795 美時","1802 台玻","1805 寶徠","1806 冠軍","1808 潤隆","1809 中釉","1810 和成","1817 凱撒衛","1903 士紙","1904 正隆","1905 華紙","1906 寶隆","1907 永豐餘","1909 榮成","2002 中鋼","2006 東和鋼鐵","2007 燁興","2008 高興昌","2009 第一銅","2010 春源","2012 春雨","2013 中鋼構","2014 中鴻","2015 豐興","2017 官田鋼","2020 美亞","2022 聚亨","2023 燁輝","2024 志聯","2025 千興","2027 大成鋼","2028 威致","2029 盛餘","2030 彰源","2031 新光鋼","2032 新鋼","2033 佳大","2034 允強","2038 海光","2049 上銀","2059 川湖","2062 橋椿","2069 運錩","2101 南港","2102 泰豐","2103 台橡","2104 國際中橡","2105 正新","2106 建大","2107 厚生","2108 南帝","2109 華豐","2114 鑫永銓","2115 六暉-KY","2201 裕隆","2204 中華","2206 三陽工業","2207 和泰車","2208 台船","2211 長榮鋼","2227 裕日車","2228 劍麟","2231 為升","2233 宇隆","2236 百達-KY","2239 英利-KY","2241 艾姆勒","2243 宏旭-KY","2247 汎德永業","2250 IKKA-KY","2301 光寶科","2302 麗正","2303 聯電","2305 全友","2308 台達電","2312 金寶","2313 華通","2314 台揚","2316 楠梓電","2317 鴻海","2321 東訊","2323 中環","2324 仁寶","2327 國巨","2328 廣宇","2329 華泰","2330 台積電","2331 精英","2332 友訊","2337 旺宏","2338 光罩","2340 台亞","2342 茂矽","2344 華邦電","2345 智邦","2347 聯強","2348 海悅","2349 錸德","2351 順德","2352 佳世達","2353 宏碁","2354 鴻準","2355 敬鵬","2356 英業達","2357 華碩","2358 廷鑫","2359 所羅門","2360 致茂","2362 藍天","2363 矽統","2364 倫飛","2365 昆盈","2367 燿華","2368 金像電","2369 菱生","2371 大同","2373 震旦行","2374 佳能","2375 凱美","2376 技嘉","2377 微星","2379 瑞昱","2380 虹光","2382 廣達","2383 台光電","2385 群光","2387 精元","2388 威盛","2390 云辰","2392 正崴","2393 億光","2395 研華","2397 友通","2399 映泰","2401 凌陽","2402 毅嘉","2404 漢唐","2405 輔信","2406 國碩","2408 南亞科","2409 友達","2412 中華電","2413 環科","2414 精技","2415 錩新","2417 圓剛","2419 仲琦","2420 新巨","2421 建準","2423 固緯","2424 隴華","2425 承啟","2426 鼎元","2427 三商電","2428 興勤","2429 銘旺科","2430 燦坤","2431 聯昌","2433 互盛電","2434 統懋","2436 偉詮電","2438 翔耀","2439 美律","2440 太空梭","2441 超豐","2442 新美齊","2443 昶虹","2444 兆勁","2449 京元電子","2450 神腦","2451 創見","2453 凌群","2454 聯發科","2455 全新","2457 飛宏","2458 義隆","2459 敦吉","2460 建通","2461 光群雷","2462 良得電","2464 盟立","2465 麗臺","2466 冠西電","2467 志聖","2468 華經","2471 資通","2472 立隆電","2474 可成","2476 鉅祥","2477 美隆電","2478 大毅","2480 敦陽科","2481 強茂","2482 連宇","2483 百容","2484 希華","2485 兆赫","2486 一詮","2488 漢平","2489 瑞軒","2491 吉祥全","2492 華新科","2493 揚博","2495 普安","2496 卓越","2497 怡利電","2498 宏達電","2501 國建","2504 國產","2505 國揚","2506 太設","2509 全坤建","2511 太子","2514 龍邦","2515 中工","2516 新建","2520 冠德","2524 京城","2527 宏璟","2528 皇普","2530 華建","2534 宏盛","2535 達欣工","2536 宏普","2537 聯上發","2538 基泰","2539 櫻花建","2540 愛山林","2542 興富發","2543 皇昌","2545 皇翔","2546 根基","2547 日勝生","2548 華固","2597 潤弘","2601 益航","2603 長榮","2605 新興","2606 裕民","2607 榮運","2608 嘉里大榮","2609 陽明","2610 華航","2611 志信","2612 中航","2613 中櫃","2614 東森","2615 萬海","2616 山隆","2617 台航","2618 長榮航","2630 亞航","2633 台灣高鐵","2634 漢翔","2636 台驊投控","2637 慧洋-KY","2642 宅配通","2645 長榮航太","2701 萬企","2702 華園","2704 國賓","2705 六福","2706 第一店","2707 晶華","2712 遠雄來","2722 夏都","2723 美食-KY","2727 王品","2731 雄獅","2739 寒舍","2748 雲品","2753 八方雲集","2762 世界健身-KY","2801 彰銀","2809 京城銀","2812 台中銀","2816 旺旺保","2820 華票","2832 台產","2834 臺企銀","2836 高雄銀","2838 聯邦銀","2845 遠東銀","2849 安泰銀","2850 新產","2851 中再保","2852 第一保","2855 統一證","2867 三商壽","2880 華南金","2881 富邦金","2882 國泰金","2883 開發金","2884 玉山金","2885 元大金","2886 兆豐金","2887 台新金","2888 新光金","2889 國票金","2890 永豐金","2891 中信金","2892 第一金","2897 王道銀行","2901 欣欣","2903 遠百","2904 匯僑","2905 三商","2906 高林","2908 特力","2910 統領","2911 麗嬰房","2912 統一超","2913 農林","2915 潤泰全","2923 鼎固-KY","2929 淘帝-KY","2939 凱羿-KY","2945 三商家購","3002 歐格","3003 健和興","3004 豐達科","3005 神基","3006 晶豪科","3008 大立光","3010 華立","3011 今皓","3013 晟銘電","3014 聯陽","3015 全漢","3016 嘉晶","3017 奇鋐","3018 隆銘綠能","3019 亞光","3021 鴻名","3022 威強電","3023 信邦","3024 憶聲","3025 星通","3026 禾伸堂","3027 盛達","3028 增你強","3029 零壹","3030 德律","3031 佰鴻","3032 偉訓","3033 威健","3034 聯詠","3035 智原","3036 文曄","3037 欣興","3038 全台","3040 遠見","3041 揚智","3042 晶技","3043 科風","3044 健鼎","3045 台灣大","3046 建碁","3047 訊舟","3048 益登","3049 精金","3050 鈺德","3051 力特","3052 夆典","3054 立萬利","3055 蔚華科","3056 富華新","3057 喬鼎","3058 立德","3059 華晶科","3060 銘異","3062 建漢","3090 日電貿","3092 鴻碩","3094 聯傑","3130 一零四","3138 耀登","3149 正達","3164 景岳","3167 大量","3168 眾福科","3189 景碩","3209 全科","3229 晟鈦","3231 緯創","3257 虹冠電","3266 昇陽","3296 勝德","3305 昇貿","3308 聯德","3311 閎暉","3312 弘憶股","3321 同泰","3338 泰碩","3346 麗清","3356 奇偶","3376 新日興","3380 明泰","3406 玉晶光","3413 京鼎","3416 融程電","3419 譁裕","3432 台端","3437 榮創","3443 創意","3447 展達","3450 聯鈞","3454 晶睿","3481 群創","3494 誠研","3501 維熹","3504 揚明光","3515 華擎","3518 柏騰","3528 安馳","3530 晶相光","3532 台勝科","3533 嘉澤","3535 晶彩科","3543 州巧","3545 敦泰","3550 聯穎","3557 嘉威","3563 牧德","3576 聯合再生","3583 辛耘","3588 通嘉","3591 艾笛森","3592 瑞鼎","3593 力銘","3596 智易","3605 宏致","3607 谷崧","3617 碩天","3622 洋華","3645 達邁","3652 精聯","3653 健策","3661 世芯-KY","3665 貿聯-KY","3669 圓展","3673 TPK-KY","3679 新至陞","3686 達能","3694 海華","3701 大眾控","3702 大聯大","3703 欣陸","3704 合勤控","3705 永信","3706 神達","3708 上緯投控","3711 日月光投控","3712 永崴投控","3714 富采","3715 定穎投控","4104 佳醫","4106 雃博","4108 懷特","4119 旭富","4133 亞諾法","4137 麗豐-KY","4142 國光生","4148 全宇生技-KY","4155 訊映","4164 承業醫","4190 佐登-KY","4306 炎洲","4414 如興","4426 利勤","4438 廣越","4439 冠星-KY","4440 宜新實業","4526 東台","4532 瑞智","4536 拓凱","4540 全球傳動","4545 銘鈺","4551 智伸科","4552 力達-KY","4555 氣立","4557 永新-KY","4560 強信-KY","4562 穎漢","4564 元翎","4566 時碩工業","4569 六方科-KY","4571 鈞興-KY","4572 駐龍","4576 大銀微系統","4581 光隆精密-KY","4583 台灣精銳","4588 玖鼎電力","4720 德淵","4722 國精化","4736 泰博","4737 華廣","4739 康普","4746 台耀","4755 三福化","4763 材料-KY","4764 雙鍵","4766 南寶","4770 上品","4771 望隼","4807 日成-KY","4904 遠傳","4906 正文","4912 聯德控股-KY","4915 致伸","4916 事欣科","4919 新唐","4927 泰鼎-KY","4930 燦星網","4934 太極","4935 茂林-KY","4938 和碩","4942 嘉彰","4943 康控-KY","4952 凌通","4956 光鋐","4958 臻鼎-KY","4960 誠美材","4961 天鈺","4967 十銓","4968 立積","4976 佳凌","4977 眾達-KY","4989 榮科","4994 傳奇","4999 鑫禾","5007 三星","5203 訊連","5215 科嘉-KY","5222 全訊","5225 東科-KY","5234 達興材料","5243 乙盛-KY","5244 弘凱","5258 虹堡","5269 祥碩","5283 禾聯碩","5284 jpp-KY","5285 界霖","5288 豐祥-KY","5292 華懋","5306 桂盟","5388 中磊","5434 崇越","5469 瀚宇博","5471 松翰","5484 慧友","5515 建國","5519 隆大","5521 工信","5522 遠雄","5525 順天","5531 鄉林","5533 皇鼎","5534 長虹","5538 東明-KY","5546 永固-KY","5607 遠雄港","5608 四維航","5706 鳳凰","5871 中租-KY","5876 上海商銀","5880 合庫金","5906 台南-KY","5907 大洋-KY","6005 群益證","6024 群益期","6108 競國","6112 邁達特","6115 鎰勝","6116 彩晶","6117 迎廣","6120 達運","6128 上福","6133 金橋","6136 富爾特","6139 亞翔","6141 柏承","6142 友勁","6152 百一","6153 嘉聯益","6155 鈞寶","6164 華興","6165 浪凡","6166 凌華","6168 宏齊","6176 瑞儀","6177 達麗","6183 關貿","6184 大豐電","6189 豐藝","6191 精成科","6192 巨路","6196 帆宣","6197 佳必琪","6201 亞弘電","6202 盛群","6205 詮欣","6206 飛捷","6209 今國光","6213 聯茂","6214 精誠","6215 和椿","6216 居易","6224 聚鼎","6225 天瀚","6226 光鼎","6230 尼得科超眾","6235 華孚","6239 力成","6243 迅杰","6257 矽格","6269 台郡","6271 同欣電","6277 宏正","6278 台表科","6281 全國電","6282 康舒","6283 淳安","6285 啟碁","6288 聯嘉","6405 悅城","6409 旭隼","6412 群電","6414 樺漢","6415 矽力*-KY","6416 瑞祺電通","6426 統新","6431 光麗-KY","6438 迅得","6442 光聖","6443 元晶","6446 藥華藥","6449 鈺邦","6451 訊芯-KY","6456 GIS-KY","6464 台數科","6472 保瑞","6477 安集","6491 晶碩","6504 南六","6505 台塑化","6515 穎崴","6525 捷敏-KY","6526 達發","6531 愛普*","6533 晶心科","6541 泰福-KY","6550 北極星藥業-KY","6552 易華電","6558 興能高","6573 虹揚-KY","6579 研揚","6581 鋼聯","6582 申豐","6585 鼎基","6591 動力-KY","6592 和潤企業","6598 ABC-KY","6605 帝寶","6606 建德工業","6625 必應","6641 基士德-KY","6655 科定","6657 華安","6658 聯策","6666 羅麗芬-KY","6668 中揚光","6669 緯穎","6670 復盛應用","6671 三能-KY","6672 騰輝電子-KY","6674 鋐寶科技","6689 伊雲谷","6691 洋基工程","6695 芯鼎","6698 旭暉應材","6706 惠特","6715 嘉基","6719 力智","6742 澤米","6743 安普新","6753 龍德造船","6754 匯僑設計","6756 威鋒電子","6768 志強-KY","6770 力積電","6776 展碁國際","6781 AES-KY","6782 視陽","6789 采鈺","6790 永豐實","6792 詠業","6796 晉弘","6799 來頡","6805 富世達","6806 森崴能源","6807 峰源-KY","6830 汎銓","6834 天二科技","6835 圓裕","6861 睿生光電","6863 永道-KY","6901 鑽石投資","6906 現觀科","6916 華凌","6933 AMAX-KY","6937 天虹","8011 台通","8016 矽創","8021 尖點","8028 昇陽半導體","8033 雷虎","8039 台虹","8046 南電","8070 長華*","8072 陞泰","8081 致新","8101 華冠","8103 瀚荃","8104 錸寶","8105 凌巨","8110 華東","8112 至上","8114 振樺電","8131 福懋科","8150 南茂","8163 達方","8201 無敵","8210 勤誠","8213 志超","8215 明基材","8222 寶一","8249 菱光","8261 富鼎","8271 宇瞻","8341 日友","8367 建新國際","8374 羅昇","8404 百和興業-KY","8411 福貞-KY","8422 可寧衛","8429 金麗-KY","8438 昶昕","8442 威宏-KY","8443 阿瘦","8454 富邦媒","8462 柏文","8463 潤泰材","8464 億豐","8466 美吉吉-KY","8467 波力-KY","8473 山林水","8476 台境","8478 東哥遊艇","8481 政伸","8482 商億-KY","8488 吉源-KY","8499 鼎炫-KY","8926 台汽電","8940 新天地","8996 高力","9802 鈺齊-KY","9902 台火","9904 寶成","9905 大華","9906 欣巴巴","9907 統一實","9908 大台北","9910 豐泰","9911 櫻花","9912 偉聯","9914 美利達","9917 中保科","9918 欣天然","9919 康那香","9921 巨大","9924 福興","9925 新保","9926 新海","9927 泰銘","9928 中視","9929 秋雨","9930 中聯資源","9931 欣高","9933 中鼎","9934 成霖","9935 慶豐富","9937 全國","9938 百和","9939 宏全","9940 信義","9941 裕融","9942 茂順","9943 好樂迪","9944 新麗","9945 潤泰新","9946 三發地產","9955 佳龍","9958 世紀鋼"];

// stock to ETF page
document.addEventListener('DOMContentLoaded', function() {
    setupDropdownStock("stockInput", "stockSearchDropdown", stockOptionsList);

    const stockSearchForm = document.getElementById('stockSearchForm');
    if (stockSearchForm) {
        stockSearchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const stockCode = document.getElementById('stockInput').value;
            const isValidStockCode = stockOptionsList.some(option => option.startsWith(stockCode));
            if (!stockCode) {
                alert("請輸入正確的股票代號");
            }
            else if (!isValidStockCode) {
                alert("請輸入正確的股票代號");
            } else {
                window.location.href = `/etf-pioneer/api/stock-to-etf?stock_code=${stockCode}`;
            }
        });
    }
});

function setupDropdownStock(inputId, dropdownId, optionsList) {
    var input = document.getElementById(inputId);
    var dropdown = document.createElement("div");
    dropdown.id = dropdownId;
    dropdown.className = "dropdown-content"; // for css styling
    input.parentNode.insertBefore(dropdown, input.nextSibling);

    input.addEventListener("input", function () {
        var searchValue = this.value.toLowerCase();
        dropdown.innerHTML = ""; // clear the dropdown
        if (searchValue) {
            optionsList.forEach(function (option) {
                if (option.toLowerCase().includes(searchValue)) {
                    var div = document.createElement("div");
                    div.textContent = option;
                    div.onclick = function () {
                        var match = option.match(/(\d+)/); // get the stock code
                        if (match && match[1]) {
                            input.value = match[1];
                        }
                        dropdown.style.display = "none";
                    };
                    dropdown.appendChild(div);
                }
            });
            dropdown.style.display = "block";
        } else {
            dropdown.style.display = "none";
        }
    });

    document.addEventListener("click", function(event) {
        if (event.target !== input) {
            dropdown.style.display = "none";
        }
    });
}


// news page
document.addEventListener('DOMContentLoaded', function() {
    const newsSearchForm = document.getElementById('newsSearchForm');
    if (newsSearchForm) {
        newsSearchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const startDateInput = document.getElementById('startDate');
            const endDateInput = document.getElementById('endDate');
            if (!startDateInput || !endDateInput) {
                alert('請選擇開始和結束日期。');
                return
            } 
            else if (startDateInput.value > endDateInput.value) {
            alert('開始日期不能晚於結束日期。');
            return;
            }
            else {
                setDefaultDate(startDateInput, endDateInput);
                window.location.href = `/etf-pioneer/api/news-wordcloud?start_date=${startDateInput.value}&end_date=${endDateInput.value}`;
            }
        });
    }
  });




// function fetchNewsTitlesForWordCloud() {
//     const startDateInput = document.getElementById('startDate');
//     const startDate = startDateInput.value;
//     if (!startDate) {
//         alert('請選擇日期。');
//         return;
//     }
//     const endDate = new Date(startDate);
//     endDate.setDate(endDate.getDate() + 7); // 7 days after the start date
//     const formattedEndDate = endDate.toISOString().split('T')[0];
    
//     // redirect to the news page
//     window.location.href = `/etf-pioneer/api/news-wordcloud?start_date=${startDate}&end_date=${formattedEndDate}`;
// }


// footer display
window.addEventListener('scroll', function() {
  var footer = document.querySelector('.site-footer');
  if ((window.innerHeight + window.pageYOffset) >= document.body.offsetHeight) {
    footer.style.display = 'block';
  } else {
    footer.style.display = 'none'; 
  }
});
