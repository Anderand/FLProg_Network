/* The editor launches a companion; it never owns its COM port or lifecycle. */
document.getElementById('launchBridge').addEventListener('click', async function () {
  this.disabled = true;
  try {
    const response = await fetch('/api/bridge/launch', {
      method: 'POST', headers: {'X-FLProg-Bridge': '1', 'Content-Type': 'application/json'}, body: '{}'
    });
    const result = await response.json();
    if (!response.ok) throw Error(result.error || 'Не удалось запустить мост');
    note('Открыта отдельная программа «Мост связи». Выберите COM-порт в её окне.');
  } catch (error) { note(error.message); }
  finally { this.disabled = false; }
});
document.getElementById('exportBridge').addEventListener('click',async function(){
  this.disabled=true;
  try{
    const result=await request('/api/bridge/export',model);
    model.bridgeExport=true;scheduleProjectDraft();
    note('Веб-проект: '+result.site+'. Заголовок '+result.include+' обновлён в библиотеке проекта. После изменения макета пересоберите прошивку.');
  }catch(error){note('Ошибка экспорта моста: '+error.message)}
  finally{this.disabled=false}
});
