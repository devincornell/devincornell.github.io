from __future__ import annotations
import numpy as np
import dataclasses
import typing

from cy_levenshtein import cy_levenshtein_dist, cy_levenshtein_dist_generic

@dataclasses.dataclass
class Vocab:
    current_ind: int = 0
    ind_to_tok: typing.Dict[int,str] = dataclasses.field(default_factory=dict)
    tok_to_ind: typing.Dict[str,int] = dataclasses.field(default_factory=dict)
    
    def add_tok(self, tok: str) -> int:
        '''Get index of current token (or add it) and return it.'''
        if tok not in self.tok_to_ind:
            self.tok_to_ind[tok] = self.current_ind
            self.ind_to_tok[self.current_ind] = tok
            self.current_ind += 1
            
        return self.tok_to_ind[tok]
    
    def get_indices(self, toks: typing.Iterable[str]) -> np.ndarray[np.uint64]:
        '''Plural of get index, but returns a numpy array.'''
        return np.array([self.get_ind(t) for t in toks], dtype=np.uint64)

@dataclasses.dataclass
class Corpus:
    token_ids: np.ndarray[np.uint64]
    doc_indices: np.ndarray[np.uint64]
    vocab: Vocab
    
    @classmethod
    def from_doc_tokens(cls, doc_tokens: typing.Iterable[typing.List[str]]):
        vocab = Vocab()
        
        doc_indices = list()
        tokens = list()
        ind = 0
        for toks in doc_tokens:
            doc_indices.append(ind)
            ind += len(toks)
            
            for tok in toks:
                tokens.append(vocab.add_tok(tok))
        
        new_corpus: cls = cls(
            token_ids = np.array(tokens, dtype=np.uint64),
            doc_indices = np.array(doc_indices + [len(tokens)], dtype=np.uint64),
            vocab = vocab
        )
        return new_corpus
    
    ######################## Useful Properties ########################
    def all_doc_tokens(self) -> typing.List[typing.List[str]]:
        '''Get tokens as strings nested in documents.'''
        return [self.doc_tokens(i) for i in range(self.num_docs())]
    
    def doc_tokens(self, ind: int) -> typing.List[str]:
        return [self.vocab.ind_to_tok[tid] for tid in self.token_ids[self.doc_slice(ind)]]
    
    def doc_token_ids(self, ind: int) -> np.ndarray[np.uint64]:
        return self.token_ids[self.doc_slice(ind)]
    
    def doc_slice(self, ind: int) -> slice:
        try:
            return slice(self.doc_indices[ind], self.doc_indices[ind+1])
        except KeyError:
            raise KeyError(f'Corpus has no document {ind=}. Total number of documents: {self.num_docs}.')
    
    def num_toks(self) -> int:
        return self.token_ids.shape[0]
    
    def num_docs(self) -> int:
        return self.doc_indices.shape[0] - 1
        
        
def levenshtein_dist(w1: np.ndarray[np.uint64], w2: np.ndarray[np.uint64]) -> int:
    shp = (w1.shape[0]+1,)
    return cy_levenshtein_dist(w1, w2, np.empty(shp, dtype=np.uint64))

def levenshtein_dist_generic(w1: np.ndarray[np.uint64], w2: np.ndarray[np.uint64]) -> int:
    #distances = np.empty((w1.shape[0]+1,), dtype=np.uint64)
    return cy_levenshtein_dist_generic(w1, 0, w1.shape[0], w2, 0, w2.shape[0])

def levenshtein_dist_corpus(w1: np.ndarray[np.uint64], w2: np.ndarray[np.uint64]) -> int:
    #distances = np.empty((w1.shape[0]+1,), dtype=np.uint64)
    return cy_levenshtein_dist_generic(w1, 0, w1.shape[0], w2, 0, w2.shape[0])

if __name__ == '__main__':
    #vocab = Corpus()
    #w1 = vocab.get_indices('hello world')
    #w2 = vocab.get_indices('hello bob')
    #w3 = vocab.get_indices('hell yeah')
    
    toc_tokens = [
        'hello world'.split(),
        'hello word'.split(),
        'hello bob'.split(),
        'the world is on fire'.split(),
        'the world is one big fire'.split(),
        'hello mothafucka'.split(),
    ]
    corpus = Corpus.from_doc_tokens(toc_tokens)
    print(corpus)
    print(corpus.num_docs())
    
    for i in range(corpus.num_docs()):
        for j in range(i+1, corpus.num_docs()):
            dist = levenshtein_dist(corpus.doc_token_ids(i), corpus.doc_token_ids(j))
            print(f'{corpus.doc_tokens(i)} --> {corpus.doc_tokens(j)}, {dist=}')
    
    exit()
    print(levenshtein_dist(w1, w2))
    print(w1)
    print(w2)
    
    
    


