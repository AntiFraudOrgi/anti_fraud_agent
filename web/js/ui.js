export function renderResults(data, targetElement) {
    // 根據風險級別決定顏色
    let riskColor, riskBg;
    switch(data.risk_level) {
      case "high":
        riskColor = "red";
        riskBg = "bg-red-100 text-red-800";
        break;
      case "medium":
        riskColor = "yellow";
        riskBg = "bg-yellow-100 text-yellow-800";
        break;
      case "low":
        riskColor = "green";
        riskBg = "bg-green-100 text-green-800";
        break;
    }
    
    // 轉換風險級別文字
    const riskLevelText = {
      high: "高度風險",
      medium: "中度風險",
      low: "低度風險"
    };
    
    const html = `
      <div class="card border-l-4 border-${riskColor}-500">
        <div class="flex justify-between items-start mb-6">
          <div>
            <h3 class="text-xl font-bold">詐騙風險評估結果</h3>
            <p class="text-gray-600">基於您提供的資訊，我們的 AI 系統評估如下</p>
          </div>
          <div class="${riskBg} font-semibold px-4 py-2 rounded-full">
            ${riskLevelText[data.risk_level]}
          </div>
        </div>
        
        <div class="mb-8">
          <h4 class="font-semibold mb-3">風險警示摘要</h4>
          <p class="text-gray-700">
            ${data.warning_summary}
          </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="p-4 bg-red-50 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <i class="fa-solid fa-triangle-exclamation text-red-600"></i>
              <h5 class="font-medium">高風險元素</h5>
            </div>
            <ul class="text-sm space-y-2">
              ${data.high_risk_elements.map(item => `<li>• ${item}</li>`).join('')}
            </ul>
          </div>
          
          <div class="p-4 bg-yellow-50 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <i class="fa-solid fa-bell text-yellow-600"></i>
              <h5 class="font-medium">可疑行為</h5>
            </div>
            <ul class="text-sm space-y-2">
              ${data.suspicious_behaviors.map(item => `<li>• ${item}</li>`).join('')}
            </ul>
          </div>
          
          <div class="p-4 bg-green-50 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <i class="fa-solid fa-check-circle text-green-600"></i>
              <h5 class="font-medium">安全建議</h5>
            </div>
            <ul class="text-sm space-y-2">
              ${data.safety_recommendations.map(item => `<li>• ${item}</li>`).join('')}
            </ul>
          </div>
        </div>
        
        <div class="mb-8">
          <h4 class="font-semibold mb-3">詳細分析</h4>
          <div class="space-y-4 text-gray-700">
            ${data.detailed_analysis.map(para => `<p>${para}</p>`).join('')}
          </div>
        </div>
        
        <div>
          <h4 class="font-semibold mb-3">專家建議</h4>
          <div class="p-5 border border-blue-100 bg-blue-50 rounded-lg">
            <div class="flex gap-3 mb-3">
              <img src="/api/placeholder/48/48" class="w-12 h-12 rounded-full" />
              <div>
                <p class="font-medium">${data.expert_advice.name}</p>
                <p class="text-sm text-gray-600">${data.expert_advice.title}</p>
              </div>
            </div>
            <div class="space-y-3">
              ${data.expert_advice.advice.map(para => `<p class="text-slate-700">${para}</p>`).join('')}
            </div>
          </div>
        </div>
      </div>
    `;
    
    targetElement.innerHTML = html;
  }