"""Bounded ASCII pattern grammar shared with the embedded matcher (no backtracking)."""
import string
SPECIAL=r'\.^$[]{}()*+?|'
def parse_pattern(pattern):
 if not isinstance(pattern,str) or len(pattern)>63 or any(not 32<=ord(c)<=126 for c in pattern):raise ValueError('Шаблон: до 63 печатных ASCII-символов')
 pos=1 if pattern.startswith('^') else 0;tokens=[]
 def atom(inclass=False):
  nonlocal pos
  if pos>=len(pattern):raise ValueError('Незавершённый шаблон')
  c=pattern[pos];pos+=1
  if c=='\\':
   if pos>=len(pattern):raise ValueError('Незавершённое экранирование')
   c=pattern[pos];pos+=1
   if c=='d':return set(string.digits)
   if c=='w':return set(string.ascii_letters+string.digits+'_')
   if c=='s':return set(' \t\n\r\v\f')
   if c not in SPECIAL+'-/':raise ValueError('Неизвестное экранирование')
   return {c}
  if (c in SPECIAL and not inclass) or (inclass and c=='['):raise ValueError('Группы, альтернативы и специальные конструкции не поддерживаются')
  return {c}
 while pos<len(pattern):
  if pattern[pos:]=='$':pos+=1;break
  if pattern[pos]=='[':
   pos+=1;neg=pos<len(pattern)and pattern[pos]=='^';pos+=int(neg);chars=set()
   while pos<len(pattern)and pattern[pos]!=']':
    start=atom(True)
    if pos<len(pattern)and pattern[pos]=='-'and pos+1<len(pattern)and pattern[pos+1]!=']':
     pos+=1;end=atom(True)
     if len(start)!=1 or len(end)!=1 or ord(next(iter(start)))>ord(next(iter(end))):raise ValueError('Некорректный диапазон шаблона')
     chars.update(map(chr,range(ord(next(iter(start))),ord(next(iter(end)))+1)))
    else:chars.update(start)
   if not chars or pos>=len(pattern):raise ValueError('Некорректный класс символов')
   pos+=1
   if neg:chars=set(map(chr,range(128)))-chars
  elif pattern[pos]=='.':chars=set(map(chr,range(128)))-{'\n','\r'};pos+=1
  else:chars=atom()
  lo=hi=1
  if pos<len(pattern)and pattern[pos]in '?*+':
   q=pattern[pos];pos+=1;lo=1 if q=='+'else 0;hi=1 if q=='?'else 63
  elif pos<len(pattern)and pattern[pos]=='{':
   end=pattern.find('}',pos);parts=pattern[pos+1:end].split(',')if end>=0 else []
   if not 1<=len(parts)<=2 or any(not p.isascii()or not p.isdigit()or len(p)>2 for p in parts):raise ValueError('Повтор: {n} или {n,m}, 0..63')
   lo=int(parts[0]);hi=int(parts[-1]);pos=end+1
   if not 0<=lo<=hi<=63:raise ValueError('Повтор: 0 <= n <= m <= 63')
  tokens.append((chars,lo,hi))
 return tokens

def pattern_matches(pattern,value):
 if not pattern:return True
 if len(value)>63 or any(ord(c)>127 for c in value):return False
 positions={0}
 for chars,lo,hi in parse_pattern(pattern):
  out=set()
  for start in positions:
   if lo==0:out.add(start)
   end=start
   for count in range(1,hi+1):
    if end>=len(value)or value[end]not in chars:break
    end+=1
    if count>=lo:out.add(end)
  positions=out
 return len(value)in positions
