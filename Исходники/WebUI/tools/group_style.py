"""Page-owned appearance of existing named groups; no layout or channel changes."""
DEFAULT_GROUP_STYLE={'border':True,'padding':12,'gap':10}
def group_style(page,name):
 styles=page.get('groupStyles',{})
 if not isinstance(styles,dict):raise ValueError('Настройки групп должны быть объектом')
 style=styles.get(str(name).strip(),{})
 if not isinstance(style,dict)or set(style)-set(DEFAULT_GROUP_STYLE):raise ValueError('Неизвестные настройки оформления группы')
 value={**DEFAULT_GROUP_STYLE,**style}
 if type(value['border'])is not bool:raise ValueError('Рамка группы: true/false')
 for key in ['padding','gap']:
  if type(value[key])is not int or not 0<=value[key]<=32:raise ValueError('Отступы группы: целые 0..32 px')
 return value

def validate_group_styles(page):
 styles=page.get('groupStyles',{})
 if not isinstance(styles,dict):raise ValueError('Настройки групп должны быть объектом')
 for name in styles:
  if not isinstance(name,str)or not name.strip()or name!=name.strip()or len(name.encode('utf-8'))>180:raise ValueError('Некорректное имя группы в настройках')
  group_style(page,name)
