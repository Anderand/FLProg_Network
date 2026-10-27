import random,re
from field_pattern import parse_pattern,pattern_matches
GOLDEN=[('[A-Z]{2}-[0-9]{3}','AB-123',True),('[A-Z]{2}-[0-9]{3}','ab-123',False),('[A-Z]{2}-[0-9]{3}','AB-12',False),('[A-Z]{2}-[0-9]{3}','AB-1234',False),('^A$','A\n',False),('^$','',True),(r'\d+','123',True),(r'\d+','',False),(r'\w{1,8}','Az_123',True),(r'\s?A','\tA',True),('a*b?c+','aaabccc',True),('a{0,2}','',True),('a{0,2}','aaa',False),('[^A-Z]+','123-',True),('[^A-Z]+','A',False),('[._-]+','._-',True),(r'\[\]\$','[]$',True),('.','\n',False),('.','\t',True),('[a-c]{2,3}','abc',True),('[a-c]{2,3}','ad',False),('a{0}','',True),('a{63}','a'*63,True),('a{63}','a'*62,False),('[A-Z]+','АБ',False),('','АБ',True)]
INVALID=['(a)','a|b',r'\1','a{64}','a{2,1}','a{1,}','[z-a]','[]','[a',r'\q','a**','a{001}','\\','A^B','A$B','АБ','a'*64]
def vectors():
 out=[dict(pattern=p,value=v,expected=e)for p,v,e in GOLDEN];rng=random.Random(314)
 atoms=['a','b','[A-Z]','[0-9]','[a-c]','[^0-9]',r'\d',r'\w','.','[._-]'];quant=['','?','*','+','{0,2}','{2}']
 for _ in range(100):
  p=''.join(rng.choice(atoms)+rng.choice(quant)for _ in range(rng.randint(1,3)));v=''.join(rng.choice('abAB12_.-\t\n')for _ in range(rng.randint(0,8)))
  out.append(dict(pattern=p,value=v,expected=bool(re.fullmatch(p,v,flags=re.ASCII))))
 out.extend(dict(pattern=p,value='abc',expected=False)for p in INVALID)
 out.append(dict(pattern='a*'*30+'b',value='a'*62+'c',expected=False))
 return out
