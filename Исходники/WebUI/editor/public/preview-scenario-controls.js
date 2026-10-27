let scenarioDocument=null,scenarioState=null,savedScenario=null,scenarioRecorder=null;
let scenarioPlaying=false,scenarioEpoch=0,scenarioRequest=0,scenarioRun=0,scenarioDelayCancel=null;
const scenarioRequests=new Map();
function scenarioReady(){return previewActive&&scenarioDocument&&scenarioState}
function scenarioDescription(step){
  if(step.action==='restart')return 'Перезапуск';
  if(step.action==='online')return step.value?'Связь включена':'Потеря связи';
  if(step.action==='automatic')return 'Авто busy/result: '+(step.value?'включено':'выключено');
  return (step.action==='command'?'Команда: ':'Значение: ')+step.id+' = '+JSON.stringify(step.value);
}
function scenarioControls(){
  const locked=scenarioPlaying||!!scenarioRecorder,ready=!!scenarioReady();
  for(const id of ['scenarioCapture','scenarioRecord','scenarioLoad'])$(id).disabled=!ready||locked;
  $('scenarioPlay').disabled=!ready||locked||!savedScenario;
  $('scenarioSave').disabled=locked||!savedScenario;
  $('scenarioStop').disabled=!locked;
  for(const node of document.querySelectorAll('#previewChannels input,#previewChannels button,#previewOnline,#previewAutomatic,#previewRestart'))node.disabled=!ready||scenarioPlaying;
  $('previewFrame').style.pointerEvents=scenarioPlaying?'none':'';
  $('previewFrame').tabIndex=scenarioPlaying?-1:0;
  const list=$('scenarioSteps');list.replaceChildren();
  if(savedScenario){
    const intro=document.createElement('li');intro.textContent='Начальный снимок: '+Object.keys(savedScenario.initial.values).length+' каналов; '+(savedScenario.initial.online?'связь включена':'связь отключена');list.append(intro);
    let elapsed=0;for(const step of savedScenario.steps){elapsed+=step.afterMs;const item=document.createElement('li');item.textContent=(elapsed/1000).toFixed(2)+' с · '+scenarioDescription(step);list.append(item)}
  }
}
function scenarioAsk(message){
  if(!previewActive)return Promise.reject(Error('Предпросмотр закрыт'));
  const id='scenario-'+scenarioEpoch+'-'+(++scenarioRequest);
  return new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{scenarioRequests.delete(id);reject(Error('Нет ответа симулятора; команда не повторялась'))},3000);
    scenarioRequests.set(id,{resolve,reject,timer});previewSend({...message,requestId:id});
  });
}
function scenarioWait(ms,run){
  if(run!==scenarioRun)return Promise.reject(Error('Остановлено'));
  return new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{scenarioDelayCancel=null;resolve()},ms);
    scenarioDelayCancel=()=>{clearTimeout(timer);scenarioDelayCancel=null;reject(Error('Остановлено'))};
  });
}
function scenarioFinishRecording(message='Запись завершена'){
  if(!scenarioRecorder)return;
  try{savedScenario=scenarioRecorder.finish();$('scenarioStatus').textContent=message+': '+savedScenario.steps.length+' шагов'}
  catch(error){$('scenarioStatus').textContent='Ошибка записи: '+error.message;savedScenario=null}
  scenarioRecorder=null;scenarioControls();
}
function scenarioStop(){
  if(scenarioRecorder){scenarioFinishRecording();return}
  if(!scenarioPlaying)return;
  scenarioRun++;scenarioPlaying=false;
  if(scenarioDelayCancel)scenarioDelayCancel();
  for(const pending of scenarioRequests.values()){clearTimeout(pending.timer);pending.reject(Error('Остановлено'))}scenarioRequests.clear();
  if(previewActive)previewSend({action:'playback',value:false,cancelPending:true,requestId:'stop-'+scenarioEpoch+'-'+(++scenarioRequest)});
  $('scenarioStatus').textContent='Остановлено. Выполненные шаги сохранены в модели; оставшиеся отменены.';scenarioControls();
}
function scenarioPreviewStarted(doc){
  scenarioEpoch++;scenarioDocument=JSON.parse(JSON.stringify(doc));scenarioState=null;scenarioRecorder=null;scenarioPlaying=false;
  if(savedScenario)try{savedScenario=PreviewScenarios.validate(scenarioDocument,savedScenario)}catch(_){savedScenario=null}
  $('scenarioStatus').textContent=savedScenario?'Сценарий готов к повтору':'Дождитесь запуска модели, затем создайте снимок или начните запись';scenarioControls();
}
function scenarioPreviewClosed(){
  scenarioStop();scenarioEpoch++;scenarioDocument=null;scenarioState=null;
  for(const pending of scenarioRequests.values()){clearTimeout(pending.timer);pending.reject(Error('Предпросмотр закрыт'))}scenarioRequests.clear();
}
window.addEventListener('message',event=>{
  if(!previewActive||event.source!==$('previewFrame').contentWindow||!event.data?.preview)return;
  const data=event.data;
  if(data.values&&scenarioDocument){
    const first=!scenarioState;
    scenarioState={values:data.values,online:data.online,automatic:data.automatic};
    if(first&&!savedScenario)$('scenarioStatus').textContent='Модель готова: создайте снимок значений или начните запись действий';
    $('previewOnline').checked=data.online;$('previewAutomatic').checked=data.automatic;
    if(!scenarioPlaying&&!scenarioRecorder)scenarioControls();
  }
  if(data.acceptedAction&&scenarioRecorder&&!data.replay){
    try{
      if(scenarioRecorder.accept(data.acceptedAction)){
        savedScenario=scenarioRecorder.data;$('scenarioStatus').textContent='Запись: '+savedScenario.steps.length+' шагов';scenarioControls();
      }else previewLog('Пароль не включён в сценарий');
    }catch(error){scenarioFinishRecording('Запись остановлена');previewLog(error.message)}
  }
  const pending=scenarioRequests.get(data.requestId);
  if(pending){clearTimeout(pending.timer);scenarioRequests.delete(data.requestId);data.ok?pending.resolve():pending.reject(Error(data.error||'Действие отклонено'))}
});
$('scenarioCapture').onclick=()=>{
  try{savedScenario=PreviewScenarios.create(scenarioDocument,scenarioState);$('scenarioStatus').textContent='Снимок значений готов. Воспроизведение восстановит его.';scenarioControls()}
  catch(error){$('scenarioStatus').textContent=error.message}
};
$('scenarioRecord').onclick=()=>{
  try{scenarioRecorder=new PreviewScenarios.Recorder(scenarioDocument,scenarioState);savedScenario=scenarioRecorder.data;$('scenarioStatus').textContent='Запись: изменяйте каналы, отправляйте команды внутри предпросмотра';scenarioControls()}
  catch(error){$('scenarioStatus').textContent=error.message}
};
$('scenarioStop').onclick=scenarioStop;
$('scenarioPlay').onclick=async()=>{
  if(scenarioPlaying||scenarioRecorder||!scenarioReady()||!savedScenario)return;
  let data;try{data=PreviewScenarios.validate(scenarioDocument,savedScenario)}catch(error){$('scenarioStatus').textContent=error.message;return}
  const run=++scenarioRun;scenarioPlaying=true;scenarioControls();
  try{
    $('scenarioStatus').textContent='Восстановление начальных значений…';
    await scenarioAsk({action:'restore',...data.initial,playback:true});
    for(let i=0;i<data.steps.length;i++){
      const step=data.steps[i];$('scenarioStatus').textContent='Шаг '+(i+1)+'/'+data.steps.length+' через '+(step.afterMs/1000).toFixed(2)+' с: '+scenarioDescription(step);
      await scenarioWait(step.afterMs,run);if(run!==scenarioRun)throw Error('Остановлено');
      await scenarioAsk(step);
    }
    await scenarioWait(data.tailMs,run);if(run!==scenarioRun)throw Error('Остановлено');
    await scenarioAsk({action:'playback',value:false});
    $('scenarioStatus').textContent='Воспроизведение завершено: '+data.steps.length+' шагов. Это имитация, FBD не исполнялась.';
  }catch(error){
    if(run===scenarioRun){
      if(previewActive)previewSend({action:'playback',value:false,cancelPending:true,requestId:'error-'+(++scenarioRequest)});
      $('scenarioStatus').textContent='Сценарий остановлен: '+error.message;previewLog('Сценарий: '+error.message);
    }
  }finally{if(run===scenarioRun){scenarioPlaying=false;scenarioControls()}}
};
$('scenarioSave').onclick=()=>{
  if(!savedScenario||!scenarioDocument)return;
  try{
    const data=PreviewScenarios.validate(scenarioDocument,savedScenario);
    const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)+'\n'],{type:'application/json;charset=utf-8'}));
    const link=document.createElement('a');link.href=url;link.download=data.projectId+'_scenario.json';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }catch(error){$('scenarioStatus').textContent=error.message}
};
$('scenarioLoad').onclick=()=>$('scenarioFile').click();
$('scenarioFile').onchange=async event=>{
  const file=event.target.files&&event.target.files[0],epoch=scenarioEpoch;
  if(!file)return;
  try{
    if(file.size>512*1024)throw Error('Файл сценария больше 512 КиБ');
    const data=JSON.parse(await file.text());if(epoch!==scenarioEpoch||!scenarioReady())throw Error('Предпросмотр изменился; откройте файл повторно');
    const validated=PreviewScenarios.validate(scenarioDocument,data);savedScenario=validated;
    $('scenarioStatus').textContent='Сценарий загружен: '+validated.steps.length+' шагов. Для запуска нажмите «Воспроизвести».';scenarioControls();
  }catch(error){$('scenarioStatus').textContent='Не удалось открыть сценарий: '+error.message}
  finally{event.target.value=''}
};
