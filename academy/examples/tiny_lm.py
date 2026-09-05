"""用小型因果 Transformer 練習預訓練、全量微調與分開計分；僅用自寫 fixture。"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import torch
from torch import nn
import torch.nn.functional as F

TRAIN = ['read the code.\n', 'run the test.\n', 'check the result.\n', 'keep the proof.\n',
         'read the test.\n', 'run the code.\n', 'check the proof.\n', 'keep the result.\n']
HELD = ['read the result.\n', 'check the code.\n']
ADAPT = ['write a note.\n', 'write a test.\n', 'write a proof.\n']
CHARS = sorted(set(''.join(TRAIN+HELD+ADAPT)))
CONTEXT = 24

def encode(text): return torch.tensor([CHARS.index(c) for c in text], dtype=torch.long)

class Attention(nn.Module):
    def __init__(self, dim, heads):
        super().__init__()
        if dim % heads:
            raise ValueError('dim must be divisible by heads')
        self.heads = heads
        self.qkv = nn.Linear(dim, 3*dim, bias=False)
        self.out = nn.Linear(dim, dim)
    def forward(self, x):
        B,T,D = x.shape
        q,k,v = self.qkv(x).chunk(3, dim=-1)
        q,k,v = [item.reshape(B,T,self.heads,D//self.heads).transpose(1,2) for item in (q,k,v)]
        weights = q @ k.transpose(-2,-1) / math.sqrt(D//self.heads)
        future = torch.triu(torch.ones(T,T,device=x.device,dtype=torch.bool), diagonal=1)
        weights = weights.masked_fill(future, float('-inf')).softmax(-1)
        values = (weights @ v).transpose(1,2).contiguous().reshape(B,T,D)
        return self.out(values)

class TinyLM(nn.Module):
    def __init__(self, dim=32, heads=4):
        super().__init__()
        self.token = nn.Embedding(len(CHARS), dim)
        self.position = nn.Embedding(CONTEXT, dim)
        self.norm1, self.norm2 = nn.LayerNorm(dim), nn.LayerNorm(dim)
        self.attention = Attention(dim, heads)
        self.ffn = nn.Sequential(nn.Linear(dim,4*dim),nn.GELU(),nn.Linear(4*dim,dim))
        self.head = nn.Linear(dim,len(CHARS))
    def forward(self, ids):
        if ids.shape[1] > CONTEXT:
            raise ValueError('context exceeded')
        x = self.token(ids) + self.position(torch.arange(ids.shape[1],device=ids.device))
        x = x + self.attention(self.norm1(x))
        x = x + self.ffn(self.norm2(x))
        return self.head(x)

def contract_checks(model):
    model.eval()
    ids = encode('read the code.').unsqueeze(0)
    with torch.no_grad():
        original = model(ids)
        altered = ids.clone();altered[0,-1] = (altered[0,-1]+1) % len(CHARS)
        assert original.shape == (1,ids.shape[1],len(CHARS))
        assert torch.allclose(original[:,:-1], model(altered)[:,:-1], atol=1e-6)
    model(ids).sum().backward()
    assert model.attention.qkv.weight.grad is not None
    model.zero_grad()

def sentence_loss(model, text):
    ids = encode(text)
    return F.cross_entropy(model(ids[:-1].unsqueeze(0)).reshape(-1,len(CHARS)),ids[1:])

def measure(model, lines):
    model.eval()
    with torch.no_grad():
        tokens = sum(len(line)-1 for line in lines)
        nll = sum(float(sentence_loss(model,line))*(len(line)-1) for line in lines) / tokens
    return {'tokens':tokens, 'nll':nll, 'perplexity':math.exp(nll)}

def train(model, lines, steps, seed):
    if not steps: return
    generator = torch.Generator().manual_seed(seed)
    opt = torch.optim.AdamW(model.parameters(),lr=.003,weight_decay=.01)
    model.train()
    for _ in range(steps):
        selected = torch.randint(len(lines),(4,),generator=generator)
        loss = torch.stack([sentence_loss(model,lines[int(i)]) for i in selected]).mean()
        opt.zero_grad();loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(),1.0)
        opt.step()

def generate(model,prompt,count=30):
    model.eval()
    text = prompt
    with torch.no_grad():
        for _ in range(count):
            ids=encode(text[-CONTEXT:]).unsqueeze(0)
            next_id=int(model(ids)[0,-1].argmax())
            text+=CHARS[next_id]
            if text.endswith('\n'): break
    return text

def task_score(model):
    prompts = ['write a ', 'write a n']
    targets = ['note.\n', 'ote.\n']
    outputs=[generate(model,p) for p in prompts]
    # 固定兩個提示只量句型遷移，不是獨立能力 benchmark。
    return {'correct':sum(o==p+t for o,p,t in zip(outputs,prompts,targets)),
            'total':len(prompts),'outputs':outputs,'scope':'Two development prompts, not an independent benchmark'}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steps',type=int,default=240)
    parser.add_argument('--adapt-steps',type=int,default=0)
    args=parser.parse_args(argv)
    if args.steps < 0 or args.adapt_steps < 0: parser.error('steps must be nonnegative')
    torch.set_num_threads(2);torch.manual_seed(42)
    model=TinyLM();contract_checks(model)
    initial=measure(model,TRAIN)
    train(model,TRAIN,args.steps,42)
    before={'train':measure(model,TRAIN),'held_out':measure(model,HELD),
            'sample':generate(model,'read '),'adaptation_task':task_score(model)}
    train(model,ADAPT,args.adapt_steps,43)
    after={'held_out':measure(model,HELD),'adaptation_task':task_score(model)}
    report={'seed':42,'device':'cpu','torch':torch.__version__,'steps':args.steps,
            'adapt_steps':args.adapt_steps,'vocab':len(CHARS),
            'data_sha256':hashlib.sha256(json.dumps([TRAIN,HELD,ADAPT]).encode()).hexdigest(),
            'parameters':sum(p.numel() for p in model.parameters()),'initial':initial,
            'before_adaptation':before,'after_adaptation':after,
            'limits':'Tiny self-authored phrases; held-out vocabulary known; no general language ability claim.'}
    print(json.dumps(report,indent=2));return report

if __name__=='__main__': main()
