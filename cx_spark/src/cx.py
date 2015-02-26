'''
CX decomposition with approximate leverage scores

Author: Jiyan Yang(jiyan@stanford.edu)
'''

from projections import *
from rma_utils import *
from rowmatrix import *
from comp_sketch import *
from numpy.linalg import norm
import time

class CX:
    def __init__(self, matrix_A, sc):
        self.matrix_A = matrix_A
        self.sc=sc

    def get_lev(self, k, **kwargs):

        if k == self.matrix_A.m or k == self.matrix_A.n: #k=min(m,n)
            #approximating the leverage scores
            load_N = kwargs.get('load_N', True)
            save_N = kwargs.get('save_N', True)
            N, time = comp_sketch(self.matrix_A, 'N', load_N, save_N, 'cx', sketch_type='projection', k=1, **kwargs)

            self.lev = [ l[1][0] for l in comp_lev(self.matrix_A.matrix_with_index, self.sc, N, 'cx') ]
            sumlev = sum(self.lev)
            self.p = [l/sumlev for l in self.lev]
        else:
            reo = 4
            q = kwargs.get('q')

            Pi = np.random.randn(self.matrix_A.n, 2*k);

            print 'Computing leverage scores, at iteration 1!'
            B = self.matrix_A.atamat(Pi,self.sc)

            for i in range(1,q):
                print 'Computing leverage scores, at iteration {0}!'.format(i+1)
                if i % reo == reo-1:
                    print "Reorthogonalzing!"
                    B = self.matrix_A.rtimes(B,self.sc)
                    Q, R = np.linalg.qr(B)
                    B = Q
                    B = self.matrix_A.ltimes(B.T,self.sc).T
                else:
                    B = self.matrix_A.atamat(B,self.sc)

            B = self.matrix_A.rtimes(B,self.sc)


            #B = matmat(self.matrix_A.rdd,Pi,'r',self.sc)
       
            #for i in range(q):
            #    print "Computing leverage scores, at iteration {0}".format(i)
            #    if i % reo == reo-1:
                    #print "reorthogonalzing!"
            #        Q, R = np.linalg.qr(B)   
            #        B = Q 
                #print "in Spe, q=%d, computing product!",i
            #    B = matmat(self.matrix_A.rdd,B.T,'l',self.sc).T
                #print "in Spe, computing product again!"
            #    B = matmat(self.matrix_A.rdd,B,'r',self.sc)

            lev, self.p = compLevExact(B, k, 0)
            self.lev = self.p*k

        return self.lev, self.p

    def comp_idx(self, scheme='deterministic', r=10):
        #seleting rows based on self.lev
        #scheme can be either 'deterministic' or 'randomized'
        #r dentotes the number of rows to select
        if scheme == 'deterministic':
            self.idx = np.array(self.lev).argsort()[::-1][:r]
        elif scheme == 'randomized':
            bins = np.add.accumulate(self.p)
            self.idx = np.digitize(np.random.random_sample(r), bins)

        return self.idx

    def get_rows(self):
        #getting the selected rows back
        idx = self.idx
        rows = self.matrix_A.rdd.filter(lambda (key, row): key in idx).collect()
        self.R = np.array([row[1] for row in rows])

        return self.R.shape #shape of R is r by d

    def comp_err(self):
        #computing the reconstruction error
        Rinv = np.linalg.pinv(self.R) #its shape is d by r
        RRinv = np.dot(Rinv, self.R) #its shape is d by d
        temp = np.eye(self.matrix_A.n) - RRinv

        diff = np.sqrt( self.matrix_A.rtimes(temp,self.sc,True).map(lambda (key,row): norm(row)**2 ).sum() )
        #diff = np.sqrt( self.matrix_A.rdd.map(lambda row: xN(row, [temp.value])).reduce(add) )

        return diff
