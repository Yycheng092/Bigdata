function callAjax() {
    const cate = $('#cate-selected').val()
    const topk = $('#topk-selected').val()

    $.ajax({
        url: '/top_keyword/api_get_cate_topword/',
        type: 'POST',
        data: {
            news_category: cate,
            topk: topk
        },
        success: function (received) {
            showTopKeys(received.wf_pairs)
            showChart(received.chart_data)
        }
    })
}

function showTopKeys(items) {
    const container = $('#topkeys-container');
    container.empty();

    const itemsPerColumn = 10;
    const columnCount = Math.ceil(items.length / itemsPerColumn);

    for (let col = 0; col < columnCount; col++) {
        const ul = document.createElement('ul');
        // 自行調整 UL 的樣式，避免跑版
        ul.style.margin = '0';
        ul.style.marginRight = '2rem';
        ul.style.paddingLeft = '1rem';
        ul.style.listStyleType = 'disc';

        for (let i = col * itemsPerColumn; i < Math.min((col + 1) * itemsPerColumn, items.length); i++) {
            const [word, count] = items[i];
            const li = document.createElement('li');
            // 避免自動換行
            li.style.whiteSpace = 'nowrap';
            li.textContent = `${word} , ${count}`;
            ul.appendChild(li);
        }

        container[0].appendChild(ul);
    }

    // 超過 40 筆時，不換行，並出現水平捲軸
    if (items.length > 40) {
        container.css({
            "flex-wrap": "nowrap",
            "overflow-x": "auto",
            "padding-left": "1rem"  // 或視情況調整成 "2rem"
        });
    } else {
        container.css({
            "flex-wrap": "wrap",
            "overflow-x": "visible",
            "padding-left": "0" // 或原本的設定
        });
    }
}


let barchart;

function showChart(chart_data) {
    const ctx = document.getElementById("mychart");

    if (window.barchart) {
        window.barchart.destroy();
    }

    window.barchart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: chart_data.labels,
            datasets: [
                {
                    label: chart_data.category,
                    data: chart_data.values,
                    backgroundColor: randomColors(chart_data.values.length)
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function randomColors(n) {
    const colors = []
    for (let i = 0; i < n; i++) {
        const r = Math.floor(Math.random() * 255)
        const g = Math.floor(Math.random() * 255)
        const b = Math.floor(Math.random() * 255)
        colors.push(`rgba(${r}, ${g}, ${b}, 0.5)`)
    }
    return colors
}

$('#btn-ok').on('click', callAjax)
$(document).ready(callAjax)
