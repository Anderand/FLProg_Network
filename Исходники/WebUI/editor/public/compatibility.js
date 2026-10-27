function showCompatibility(report){
  const list=$('compatibilityRows');list.replaceChildren();
  $('compatibilitySummary').textContent=`Ошибок: ${report.summary.errors}. Предупреждений: ${report.summary.warnings}.`;
  const labels={ok:'OK',info:'Информация',warning:'Внимание',error:'Ошибка'};
  for(const item of report.checks){const row=document.createElement('li');row.className=item.status;
    const message=document.createElement('p');message.textContent=labels[item.status]+': '+item.message;row.append(message);
    if(item.path){const path=document.createElement('code');path.textContent=item.path;row.append(path)}list.append(row)}
  if(!$('compatibilityDialog').open)$('compatibilityDialog').showModal();
}
async function checkCompatibility(data,show=true){
  const report=await request('/api/compatibility',data);
  if(show||!report.ok)showCompatibility(report);
  return report;
}
document.addEventListener('DOMContentLoaded',()=>{
  const run=async()=>{try{await checkCompatibility(copyModel())}catch(error){note('Ошибка проверки совместимости: '+error.message)}};
  $('compatibilityCheck').onclick=run;$('compatibilityAgain').onclick=run;
  $('compatibilityClose').onclick=()=>$('compatibilityDialog').close();
});
