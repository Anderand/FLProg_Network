// Pure scenario format/recording. No network, DOM or real controller access.
const PreviewScenarios = (() => {
  const schema = 'flprog.webui.preview-scenario/1.0', maxSteps = 200, maxDuration = 600000;
  const isSecret = (doc,c) => c.secret === true || c.id === 'wifi_password' || c.id === 'ap_password' || doc.pages.some(p=>p.widgets.some(w=>w.type==='password-input' && [w.channel,...(w.bindings||[]).filter(b=>b.role==='setpoint').map(b=>b.channel)].includes(c.id)));
  const signature = doc => doc.channels.map(c => ({id:c.id,type:c.type,direction:c.direction,secret:isSecret(doc,c)})).sort((a,b)=>a.id.localeCompare(b.id));
  function typed(channel, value) {
    if (channel.type === 'bool' && typeof value !== 'boolean') throw Error('Нужен bool: ' + channel.id);
    if (channel.type === 'text' && (typeof value !== 'string' || new TextEncoder().encode(value).length > 63)) throw Error('Текст: не больше 63 байт: ' + channel.id);
    if ((channel.type === 'float' || channel.type === 'int32') && (typeof value !== 'number' || !Number.isFinite(value))) throw Error('Нужно конечное число: ' + channel.id);
    if (channel.type === 'int32' && (!Number.isInteger(value) || value < -2147483648 || value > 2147483647)) throw Error('Нужен int32: ' + channel.id);
    return value;
  }
  function snapshot(doc, state) {
    if (!state || !state.values || typeof state.values!=='object' || Array.isArray(state.values) || typeof state.online !== 'boolean' || typeof state.automatic !== 'boolean') throw Error('Предпросмотр ещё не готов');
    const values = Object.create(null);
    for (const c of doc.channels) if (!isSecret(doc,c)) values[c.id] = typed(c, state.values[c.id]);
    return {values, online:state.online, automatic:state.automatic};
  }
  function action(doc, input) {
    if (!input || typeof input !== 'object') throw Error('Неверный шаг сценария');
    if (input.action === 'restart') return {action:'restart'};
    if (input.action === 'online' || input.action === 'automatic') {
      if (typeof input.value !== 'boolean') throw Error('Для состояния нужен bool');
      return {action:input.action,value:input.value};
    }
    if (input.action !== 'set' && input.action !== 'command') throw Error('Неизвестное действие сценария');
    const c = doc.channels.find(c => c.id === input.id);
    if (!c || isSecret(doc,c)) throw Error('Канал отсутствует или содержит пароль: ' + input.id);
    const result = {action:input.action,id:c.id,value:typed(c,input.value)};
    if (input.action === 'command') {
      const w = doc.pages.flatMap(p=>p.widgets).find(w=>w.id === input.widget);
      if (c.direction === 'publish' || !w || ![w.channel,...(w.bindings||[]).filter(b=>b.role==='setpoint').map(b=>b.channel)].includes(c.id)) throw Error('Команда не соответствует виджету: ' + input.id);
      result.widget = w.id;
    }
    return result;
  }
  function validate(doc, data) {
    if (!data || data.schema !== schema || data.projectId !== doc.project.id) throw Error('Сценарий относится к другому проекту или формату');
    const supplied=Array.isArray(data.channels)&&data.channels.length===doc.channels.length?data.channels.map(c=>({id:c?.id,type:c?.type,direction:c?.direction,secret:c?.secret})).sort((a,b)=>String(a.id).localeCompare(String(b.id))):null;
    if (JSON.stringify(supplied) !== JSON.stringify(signature(doc))) throw Error('Состав или типы каналов изменились');
    if (!data.initial || !data.initial.values || typeof data.initial.values !== 'object') throw Error('Нет начального снимка');
    const expected = doc.channels.filter(c=>!isSecret(doc,c)).map(c=>c.id).sort();
    if (JSON.stringify(Object.keys(data.initial.values).sort()) !== JSON.stringify(expected)) throw Error('Снимок не соответствует каналам проекта');
    const initial = snapshot(doc,data.initial);
    if (!Array.isArray(data.steps) || data.steps.length > maxSteps) throw Error('Максимум 200 шагов');
    let duration = 0;
    const steps = data.steps.map(step => {
      if (!step || typeof step!=='object') throw Error('Неверный шаг сценария');
      if (!Number.isInteger(step.afterMs) || step.afterMs < 0 || step.afterMs > maxDuration) throw Error('Неверная задержка шага');
      duration += step.afterMs; return {...action(doc,step),afterMs:step.afterMs};
    });
    if (!Number.isInteger(data.tailMs) || data.tailMs < 0 || duration + data.tailMs > maxDuration) throw Error('Максимальная длительность — 10 минут');
    return {schema,projectId:doc.project.id,channels:signature(doc),initial,steps,tailMs:data.tailMs};
  }
  function create(doc, state) {
    return {schema,projectId:doc.project.id,channels:signature(doc),initial:snapshot(doc,state),steps:[],tailMs:0};
  }
  class Recorder {
    constructor(doc,state,clock=Date.now) {this.doc=doc;this.clock=clock;this.last=this.started=clock();this.data=create(doc,state);}
    accept(input) {
      const channel = this.doc.channels.find(c=>c.id===input.id);
      if (channel && isSecret(this.doc,channel)) return false;
      const step = action(this.doc,input),now=this.clock();
      if (this.data.steps.length >= maxSteps || now-this.started > maxDuration) throw Error('Достигнут лимит сценария: 200 шагов / 10 минут');
      this.data.steps.push({...step,afterMs:Math.max(0,Math.round(now-this.last))});this.last=now;return true;
    }
    finish() {
      this.data.tailMs=Math.max(0,Math.min(maxDuration,this.clock()-this.started)-(this.last-this.started));
      return validate(this.doc,this.data);
    }
  }
  return {schema,maxSteps,maxDuration,signature,snapshot,action,validate,create,Recorder};
})();
