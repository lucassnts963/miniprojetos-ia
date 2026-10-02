"""A rede que completa texto: um transformer pequeno (a mesma arquitetura das LLMs, em miniatura).

    pedaços -> números (embedding) + posição -> blocos [atenção + rede densa] -> chance de cada próximo pedaço

A atenção é o que deixa cada pedaço "olhar" para todos os anteriores e pesar quais importam.
"""
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

PADRAO = dict(vocab=3000, janela=96, largura=256, camadas=6, cabecas=4)


class Bloco(nn.Module):
    def __init__(self, largura, cabecas):
        super().__init__()
        self.cabecas = cabecas
        self.n1, self.n2 = nn.LayerNorm(largura), nn.LayerNorm(largura)
        self.qkv = nn.Linear(largura, 3 * largura)
        self.saida = nn.Linear(largura, largura)
        self.densa = nn.Sequential(nn.Linear(largura, 4 * largura), nn.GELU(), nn.Linear(4 * largura, largura))
        self.solta = nn.Dropout(0.1)

    def forward(self, x, guardar=None):
        B, T, C = x.shape
        q, k, v = self.qkv(self.n1(x)).view(B, T, 3, self.cabecas, C // self.cabecas).permute(2, 0, 3, 1, 4)
        pesos = (q @ k.transpose(-2, -1)) / math.sqrt(k.shape[-1])
        futuro = torch.triu(torch.ones(T, T, dtype=torch.bool, device=x.device), 1)
        pesos = pesos.masked_fill(futuro, float("-inf")).softmax(-1)      # cada pedaço só olha para trás
        if guardar is not None:
            guardar.append(pesos.detach())
        a = (self.solta(pesos) @ v).transpose(1, 2).reshape(B, T, C)
        x = x + self.solta(self.saida(a))
        return x + self.solta(self.densa(self.n2(x)))


class Rede(nn.Module):
    def __init__(self, vocab, janela, largura, camadas, cabecas):
        super().__init__()
        self.cfg = dict(vocab=vocab, janela=janela, largura=largura, camadas=camadas, cabecas=cabecas)
        self.pedaco = nn.Embedding(vocab, largura)
        self.posicao = nn.Embedding(janela, largura)
        self.blocos = nn.ModuleList(Bloco(largura, cabecas) for _ in range(camadas))
        self.norma = nn.LayerNorm(largura)
        self.cabeca = nn.Linear(largura, vocab, bias=False)
        self.cabeca.weight = self.pedaco.weight                           # mesma tabela na entrada e na saída
        self.apply(self._iniciar)

    @staticmethod
    def _iniciar(m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, std=0.02)
            if getattr(m, "bias", None) is not None:
                nn.init.zeros_(m.bias)

    def forward(self, ids, alvo=None, guardar=None):
        T = ids.shape[1]
        x = self.pedaco(ids) + self.posicao(torch.arange(T, device=ids.device))
        for b in self.blocos:
            x = b(x, guardar)
        notas = self.cabeca(self.norma(x))                                # uma nota para cada pedaço do vocabulário
        if alvo is None:
            return notas
        return notas, F.cross_entropy(notas.view(-1, notas.shape[-1]).float(), alvo.view(-1))

    @torch.no_grad()
    def proximo(self, contexto, com_atencao=False):
        """Chance de cada pedaço ser o próximo. contexto: lista de ids (usa os últimos `janela`)."""
        self.eval()
        dev = next(self.parameters()).device
        ids = torch.tensor([list(contexto)[-self.cfg["janela"]:]], device=dev)
        guardar = [] if com_atencao else None
        p = self(ids, guardar=guardar)[0, -1].float().softmax(-1).cpu().numpy()
        if not com_atencao:
            return p
        # para onde o último pedaço olhou, na última camada (média das cabeças)
        return p, guardar[-1][0, :, -1, :].float().mean(0).cpu().numpy()

    @torch.no_grad()
    def por_dentro(self, contexto):
        """O caminho da última posição pela rede, camada por camada.

        -> (para onde ela olhou em cada camada (camadas, T), o palpite que a rede daria se parasse ali (camadas, vocab))
        O palpite de cada camada usa a mesma saída final aplicada ao estado daquela camada.
        """
        self.eval()
        dev = next(self.parameters()).device
        ids = torch.tensor([list(contexto)[-self.cfg["janela"]:]], device=dev)
        x = self.pedaco(ids) + self.posicao(torch.arange(ids.shape[1], device=dev))
        olhar, palpites = [], []
        for b in self.blocos:
            pesos = []
            x = b(x, pesos)
            olhar.append(pesos[0][0, :, -1, :].float().mean(0))
            palpites.append(self.cabeca(self.norma(x[0, -1])).float().softmax(-1))
        return torch.stack(olhar).cpu().numpy(), torch.stack(palpites).cpu().numpy()
