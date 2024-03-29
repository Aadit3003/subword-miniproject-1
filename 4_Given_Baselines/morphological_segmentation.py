# -*- coding: utf-8 -*-
"""Morphological Segmentation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13wFV7C68lNFmr8xGR1eWTuR3FLmRqlng

# CMU 11424/11824 Spring 2024: Morphological Segmentation

## Baselines for Morphological Segmentation

## Download Datasets

Data should be downloaded from Canvas and uploaded to the Colab filesystem.
"""

from Timer import Timer

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/

# !unzip dataset.zip

"""## Performance Measures

There are many different ways to measure the correctness of our models, such as raw accuracy or span accuracy. However, since this dataset contains morpheme *allomorphy*, we are simplifying our approach and calculating the f1 score of the morphemes generated, treating each set of morphemes as a bag of words.
"""

def evaluate(gold, pred):

  tp = 0
  fp = 0
  fn = 0

  for g, p in zip(gold, pred):
    g_bag = g.strip().split(" ")
    p_bag = p.strip().split(" ")

    tp += sum([1 for i in p_bag if i in g_bag])
    fp += sum([1 for i in p_bag if not i in g_bag])
    fn += sum([1 for i in g_bag if not i in p_bag])

  precision = tp / (tp + fp)
  recall = tp / (tp + fn)
  if precision == 0 or recall == 0:
    f1 = 0
  else:
    f1 = 2 / ((1/precision) + (1/recall))

  return {
      "f1": f1,
      "precision": precision,
      "recall": recall,
  }

"""## Unigram SentencePiece

First, we need to install and import [sentencepiece](https://github.com/google/sentencepiece). This unsupervised tokenization toolkit includes both byte-pair-encoding (BPE) and unigram based algorithms, but we will use the unigram method as out baseline here because of its superior performance.
"""

# !pip install sentencepiece

timer = Timer()
timer.start()
import sentencepiece as spm

"""Now, we will train sentencpiece on our train file for the language of interest -- we do not need to provide the segmented target files since this is an unsupervised technique. Vocab size is chosen manually for each language based on hyper-parameter search. For Shipibo-Konibo (shp) I recommend a vocab size of __316__. For Rarámuri/Tahumara (tar) I recommend a vocab size of __412__.

"""

lang = "shp"
vocab_size=412

train_file = f'miniproj1-dataset/{lang}.train.src'

spm.SentencePieceTrainer.Train(
    input=train_file,
    model_prefix=f'unigram_{lang}',
    vocab_size=vocab_size,
    model_type='unigram'
)

input_file = f'miniproj1-dataset/{lang}.dev.src'
output_file = f'miniproj1-dataset/{lang}.dev.tgt'

s = spm.SentencePieceProcessor(model_file=f'unigram_{lang}.model')


golds = []
preds = []

for word, morph in zip(open(input_file), open(output_file)):
  gold = morph.strip()
  pred = ' '.join(s.encode(word, out_type=str))[1:].lstrip()
  golds.append(gold)
  preds.append(pred)

print(evaluate(golds, preds))
timer.stop()
print("SENTENCE_PIECE: ", str(timer))

with open(f'unigram_{lang}.dev.tgt', 'w') as f:
  f.write("\n".join(preds))

"""## Morfessor

First, we install and and import [Morfessor 2.0](https://morfessor.readthedocs.io/en/latest/). Like Sentencepiece, this algorithm uses unlabelled data in order to generate predictions.
"""

# !pip install morfessor

timer.start()
import morfessor

"""Because the algorithm is unsupervised, we only need to provide the src file. Unlike Sentencepiece, there is no need to specify the vocabulary size."""

lang = "shp"

train_file = f'miniproj1-dataset/{lang}.train.src'

io = morfessor.MorfessorIO()
data = list(io.read_corpus_file(train_file))
model = morfessor.BaselineModel()
model.load_data(data)
model.train_batch()
io.write_binary_file(f'morfessor_{lang}.model', model)

input_file = f'miniproj1-dataset/{lang}.dev.src'
output_file = f'miniproj1-dataset/{lang}.dev.tgt'

model = io.read_binary_model_file(f'morfessor_{lang}.model')

golds = []
preds = []

for word, morph in zip(open(input_file), open(output_file)):
  gold = morph.strip()
  pred = " ".join(model.viterbi_segment(word)[0]).strip()
  golds.append(gold)
  preds.append(pred)

print(evaluate(golds, preds))


with open(f'morfessor_{lang}.dev.tgt', 'w') as f:
  f.write("\n".join(preds))


timer.stop()
print("MORFESSOR: ", str(timer))

