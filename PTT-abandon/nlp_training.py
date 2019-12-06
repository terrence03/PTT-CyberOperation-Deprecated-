# %%
from snownlp import SnowNLP
from snownlp import sentiment

opath = r'E:\\research\\data\\UdicOpenData-master\\udicOpenData\\PTT\\'
pfile = 'Positive\\adulation\\adulation.txt'
nfile = 'Negative\\HatePolitics\\HatePolitics.content.txt'

tpath = r'E:\\research\\data\\語料\\'
tpfile = 'pos.txt'
tnfile = 'neg.txt'


def tradtion2simple(file):
    with open(file, 'r', encoding='utf-8') as f:
        doc = f.read()
        s = SnowNLP(doc)
        r = s.han
    return r


def save(doc, filename):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(doc)


# %%
save(tradtion2simple(opath+pfile), tpath+tpfile)
save(tradtion2simple(opath+nfile), tpath+tnfile)

# %%
sentiment.train(tpath+tnfile, tpath+tpfile)
sentiment.save(tpath+'sentiment.marshal')


# %%
