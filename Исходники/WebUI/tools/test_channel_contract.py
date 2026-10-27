import copy,json,tempfile,unittest
from pathlib import Path
from channel_contract import channel_contract,contract_markdown
from build_project_package import build

class ChannelContractTest(unittest.TestCase):
    def document(self):
        return dict(schema='flprog.webui/1.0',project=dict(id='pump_panel',title='Насос'),
          transport=dict(id='w5500-http-1',port=80),channels=[
          dict(id='actual',label='Факт',type='float',direction='publish',index=104,source='user'),
          dict(id='setpoint',label='Уставка',type='float',direction='duplex',index=101,source='user'),
          dict(id='busy',label='Выполняется',type='bool',direction='publish',index=102,source='user'),
          dict(id='result',label='Выполнено',type='bool',direction='publish',index=103,source='user'),
          dict(id='start',label='Запуск',type='bool',direction='command',index=105,source='user'),
          dict(id='note',label='Заметка',type='text',direction='publish',index=107,source='user'),
          dict(id='counter',label='Счётчик',type='int32',direction='publish',index=106,source='user'),
          dict(id='network_ip',label='IP',type='text',direction='publish',index=0,source='FLProgNetworkInterface::localIP')],
          pages=[dict(id='main',title='Главная',widgets=[
            dict(id='field',type='number-input',channel='setpoint',label='Уставка',x=1,y=1,w=4,h=2,
                 bindings=[dict(role='value',channel='actual',direction='publish'),dict(role='busy',channel='busy',direction='publish'),dict(role='result',channel='result',direction='publish')]),
            dict(id='button',type='button',channel='start',label='Запустить',x=5,y=1,w=4,h=2)])])
    def test_stable_numbers_directions_and_all_types(self):
        report=channel_contract(self.document());rows={c['id']:c for c in report['channels']}
        self.assertEqual(rows['setpoint']['index'],101)
        self.assertEqual(rows['setpoint']['blocks'],['Publish Float','Command Float'])
        self.assertEqual(rows['start']['blocks'],['Command Bool'])
        self.assertEqual(rows['counter']['blocks'],['Publish Int'])
        self.assertEqual(rows['note']['blocks'],['Publish Text'])
        self.assertEqual(rows['network_ip']['blocks'],[])
        self.assertTrue(rows['network_ip']['system'])
        self.assertEqual(report['summary']['user'],7)
    def test_binding_roles_and_unused_channels_are_explicit(self):
        rows={c['id']:c for c in channel_contract(self.document())['channels']}
        self.assertEqual(rows['busy']['references'][0]['role'],'busy')
        self.assertEqual(rows['result']['references'][0]['role'],'result')
        self.assertEqual(rows['actual']['references'][0]['widget_id'],'field')
        self.assertEqual(rows['note']['references'],[])
        self.assertIn('Виджет не использует канал',contract_markdown(channel_contract(self.document())))
    def test_no_mutation_or_value_export(self):
        doc=self.document();doc['channels'][0].pop('index')
        doc['channels'][0]['value']='PRIVATE_CHANNEL_VALUE'
        doc['wifi_password']='PRIVATE_WIFI_PASSWORD'
        before=copy.deepcopy(doc);report=channel_contract(doc)
        self.assertEqual(doc,before)
        content=json.dumps(report)+contract_markdown(report)
        self.assertNotIn('PRIVATE_CHANNEL_VALUE',content)
        self.assertNotIn('PRIVATE_WIFI_PASSWORD',content)
    def test_markdown_does_not_create_html_or_images_from_labels(self):
        doc=self.document();doc['project']['title']='<img src=x> ![x](https://example.com) |\n# x'
        md=contract_markdown(channel_contract(doc))
        self.assertNotIn('<img',md);self.assertNotIn('![x]',md)
        self.assertIn('&lt;img',md)
    def test_generated_package_has_same_contract_as_editor(self):
        doc=self.document()
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'project.flpui';source.write_text(json.dumps(doc),encoding='utf-8')
            package=build(source,Path(tmp)/'packages')
            self.assertEqual(json.loads((package/'CHANNELS.json').read_text(encoding='utf-8')),channel_contract(doc))
            self.assertEqual((package/'CHANNELS_RU.md').read_text(encoding='utf-8'),contract_markdown(channel_contract(doc)))

if __name__=='__main__':unittest.main()
