export function renderResults(data, container) {
  // Assuming data structure has risk level and insights
  const { riskLevel, insights, riskScore } = data;
  
  // Risk level badge class mapping
  const riskClasses = {
    low: "risk-low",
    medium: "risk-medium",
    high: "risk-high"
  };
  
  // Risk indicator with score
  const scorePercentage = Math.min(riskScore, 100);
  
  container.innerHTML = `
    <div class="border-b border-slate-200 pb-4 mb-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-lg font-semibold">風險評估結果</h3>
        <span class="${riskClasses[riskLevel]} uppercase">${riskLevel === 'low' ? '低風險' : riskLevel === 'medium' ? '中度風險' : '高風險'}</span>
      </div>
      
      <div class="bg-slate-100 rounded-full h-2 w-full mt-2">
        <div class="h-2 rounded-full ${riskLevel === 'low' ? 'bg-emerald-500' : riskLevel === 'medium' ? 'bg-amber-500' : 'bg-rose-500'}" 
             style="width: ${scorePercentage}%"></div>
      </div>
      <div class="flex justify-between text-xs text-slate-500 mt-1">
        <span>安全</span>
        <span>危險</span>
      </div>
    </div>
    
    <div>
      <h4 class="font-medium mb-3">風險分析</h4>
      <ul class="space-y-3">
        ${insights.map(insight => `
          <li class="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
            <span class="mt-1 ${insight.type === 'warning' ? 'text-amber-500' : insight.type === 'danger' ? 'text-rose-500' : 'text-emerald-500'}">
              <i class="fa-solid ${insight.type === 'warning' ? 'fa-triangle-exclamation' : insight.type === 'danger' ? 'fa-ban' : 'fa-circle-check'}"></i>
            </span>
            <div>
              <p class="font-medium">${insight.title}</p>
              <p class="text-slate-600 text-sm mt-1">${insight.description}</p>
            </div>
          </li>
        `).join('')}
      </ul>
      
      <div class="mt-6 flex justify-between">
        <a href="knowledge.html#${riskLevel}-risks" class="btn-secondary text-sm">
          <i class="fa-solid fa-book mr-1"></i> 詳細風險資訊
        </a>
        <a href="consultation.html" class="btn-primary text-sm">
          <i class="fa-solid fa-user-tie mr-1"></i> 專業諮詢
        </a>
      </div>
    </div>
  `;
}