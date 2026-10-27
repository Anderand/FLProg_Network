// Read-only view of the current design. All user strings are rendered as text.
let displayedContract = null;
function renderChannelContract() {
  const body = document.querySelector('#contractTable tbody');
  body.replaceChildren();
  if (!displayedContract) return;
  const filter = $('contractFilter').value;
  const rows = displayedContract.report.channels.filter(c => filter === 'all' || (filter === 'system') === c.system);
  for (const channel of rows) {
    const row = document.createElement('tr');
    const cells = [String(channel.index), channel.label + '\n' + channel.id,
      channel.type, channel.direction_title + '\n' + (channel.system ? 'Автоматически' : channel.blocks.join(' + ')),
      channel.references.map(ref => ref.page_title + ' / ' + ref.widget_label + ' (' + ref.role_title + ')').join('\n') || 'Без виджета'];
    for (const text of cells) {
      const cell = document.createElement('td'); cell.textContent = text; row.append(cell);
    }
    body.append(row);
  }
  if (!rows.length) {
    const row = document.createElement('tr'), cell = document.createElement('td');
    cell.colSpan = 5; cell.textContent = 'В этой группе каналов нет'; row.append(cell); body.append(row);
  }
}
function downloadChannelContract(format) {
  if (!displayedContract) return;
  const json = format === 'json';
  const content = json ? JSON.stringify(displayedContract.report, null, 2) + '\n' : displayedContract.markdown;
  const blob = new Blob([content], {type: json ? 'application/json;charset=utf-8' : 'text/markdown;charset=utf-8'});
  const url = URL.createObjectURL(blob), anchor = document.createElement('a');
  anchor.href = url; anchor.download = displayedContract.report.project_id + '_channels.' + format;
  document.body.append(anchor); anchor.click(); anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
$('channelContract').onclick = async () => {
  const button = $('channelContract'); button.disabled = true;
  try {
    const snapshot = copyModel();
    const result = await request('/api/contract', snapshot);
    if (JSON.stringify(snapshot) !== JSON.stringify(copyModel())) {
      note('Проект изменился. Откройте таблицу каналов повторно.'); return;
    }
    displayedContract = result;
    const report = result.report;
    $('contractSummary').textContent = 'Проект: ' + report.project_id + ' · системных: ' + report.summary.system + ' · пользовательских: ' + report.summary.user;
    $('contractFilter').value = 'all'; renderChannelContract(); $('contractDialog').showModal();
  } catch (error) { note('Не удалось построить таблицу: ' + error.message); }
  finally { button.disabled = false; }
};
$('contractFilter').onchange = renderChannelContract;
$('contractClose').onclick = () => $('contractDialog').close();
$('contractMarkdown').onclick = () => downloadChannelContract('md');
$('contractJson').onclick = () => downloadChannelContract('json');
