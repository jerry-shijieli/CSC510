from __future__ import print_function, division
from pdb import set_trace

from time import time
from scipy.sparse import csr_matrix

from sklearn.neighbors import NearestNeighbors
from random import randint,random,shuffle
from sklearn import svm
from sklearn.feature_extraction import FeatureHasher
from sklearn import naive_bayes
from sklearn import tree

from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import numpy as np
import pickle
from ABCD import ABCD

"Load data from txt"
def readfile(filename):
    corpus=[]
    label=[]
    with open(filename,'r') as f:
        for doc in f.readlines():
            try:
                corpus.append(doc.split(" ::::::>>>>>> ")[1][:-2])
                label.append(doc.split(" ::::::>>>>>> ")[0])
            except:
                pass

    label=np.array(label)

    return label, corpus

"Calculate iqr"
def iqr(array):
    return np.percentile(array,75)-np.percentile(array,25)

"Vector Space Model, input: list of str, output: list of dict"
def vsm(corpus):
    # tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=20000,
    #                                 stop_words='english')
    # return tf_vectorizer.fit_transform(corpus)
    return [Counter(row.split()) for row in corpus]


"Hash"
def hash(matrix,feature_number=4000):
    hasher = FeatureHasher(n_features=feature_number, non_negative=True)
    X=hasher.transform(matrix)
    return X

"Preprocessing"
def preprocess(filename):
    label, corpus=readfile(filename)
    matrix=vsm(corpus)
    matrix=hash(matrix)
    matrix=l2normalize(matrix)
    return label, matrix

"Shuffle"
def shuffle_tuple(my_tuple):
    tmp=[]
    aa=[]
    for i,array in enumerate(my_tuple):
        if not i:
            tmp=range(len(array))
            shuffle(tmp)
        aa.append(array[tmp])
    return tuple(aa)

"L2 normalization"
def l2normalize(mat):
    mat=mat.asfptype()
    for i in xrange(mat.shape[0]):
        nor=np.linalg.norm(mat[i].data,2)
        if not nor==0:
            for k in mat[i].indices:
                mat[i,k]=mat[i,k]/nor
    return mat

"Split data into training and testing"
def split_data(label,num_each=10):
    train=[]
    for ll in set(label):
        index=[i for i in xrange(len(label)) if label[i]==ll]
        train.extend(list(np.random.choice(index,size=num_each,replace=False)))
    test=list(set(range(len(label)))-set(train))
    return train,test


"Concatenate two csr into one (equal num of columns)"
def csr_vstack(a,b):
    data=np.array(list(a.data)+list(b.data))
    ind=np.array(list(a.indices)+list(b.indices))
    indp=list(a.indptr)+list(b.indptr+a.indptr[-1])[1:]
    return csr_matrix((data,ind,indp),shape=(a.shape[0]+b.shape[0],a.shape[1]))

"smote only oversample"
def smote_most(data,label,k=5):
    labelCont=Counter(label)
    # num=int(sum(labelCont.values())/len(labelCont.values()))
    num=int(np.max(labelCont.values()))
    labelmade=[]
    balanced=[]
    for l in labelCont:
        id=[i for i,x in enumerate(label) if x==l]
        sub=data[id]
        labelmade+=[l]*num
        if labelCont[l]<num:
            num_s=num-labelCont[l]
            nbrs = NearestNeighbors(n_neighbors=k+1, algorithm='brute').fit(sub)
            distances, indices = nbrs.kneighbors(sub)
            row=[]
            column=[]
            new=[]
            for i in xrange(num_s):
                mid=randint(0,sub.shape[0]-1)
                nn=indices[mid,randint(1,k)]
                indx=list(set(list(sub[mid].indices)+list(sub[nn].indices)))
                datamade=[]
                for j in indx:
                    gap=random()
                    datamade.append((sub[nn,j]-sub[mid,j])*gap+sub[mid,j])
                row.extend([i]*len(indx))
                column.extend(indx)
                new.extend(datamade)
            mat=csr_matrix((new, (row, column)), shape=(num_s, sub.shape[1]))
            if balanced == []:
                balanced=mat
            else:
                balanced=csr_vstack(balanced,mat)
            balanced=csr_vstack(balanced,sub)
        else:
            ind=np.random.choice(labelCont[l],num,replace=False)
            if balanced == []:
                balanced=sub[ind]
            else:
                balanced=csr_vstack(balanced,sub[ind])
    labelmade=np.array(labelmade)
    return balanced, labelmade


"Classifier: linear SVM"
def do_SVM(label,data):
    data,label=smote_most(data,label)
    clf = svm.SVC(probability=True,kernel='linear')
    clf.fit(data,label)
    return clf

"Evaluation"
def evaluate(true_label,prediction):
    dict={}
    labellist=set(true_label)
    abcd=ABCD(before=true_label,after=prediction)
    tmp = np.array([k.stats() for k in abcd()])
    for i,label in enumerate(labellist):
        dict[label]=tmp[i,-2]
    pre=np.mean(tmp[:,1])
    rec=np.mean(tmp[:,0])
    dict['F_M']=2*pre*rec/(pre+rec)
    return dict










