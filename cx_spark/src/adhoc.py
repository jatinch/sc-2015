from pyspark import SparkContext
from pyspark import SparkConf

from utils import prepare_matrix
from cx import CX
from sparse_row_matrix import SparseRowMatrix

conf = SparkConf().set('spark.eventLog.enabled','true').set('spark.driver.maxResultSize', '15g') 
sc = SparkContext(appName='cx_exp',conf=conf)
import ast
import numpy as np

def parse(string):
    s = str(string)
    val = ast.literal_eval(s)
    return val[0], (np.array(val[1][0]), np.array(val[1][1]))


data = sc.textFile('/scratch1/scratchdirs/msingh/sc_paper/experiments/striped_data/columns_matrix').map(lambda x:parse(x))
#row_shape = 131048
#column_shape = 8258911
row_shape = 8258911
column_shape =131048

print data.take(1)

matrix_A = SparseRowMatrix(data,'output', row_shape,column_shape, True)
cx = CX(matrix_A)
k = 20
q = 2
lev, p = cx.get_lev(k,axis=0, q=q) 
#end = time.time()
leverage_scores_file='/scratch1/scratchdirs/msingh/sc_paper/experiments/striped_data/columns_row_leverage_scores'
p_score_file='/scratch1/scratchdirs/msingh/sc_paper/experiments/striped_data/columns_p_scores'
np.savetxt(leverage_scores_file, np.array(lev))
np.savetxt(p_score_file, np.array(p))





#825 post street
"""
rows_rdd = data.map(lambda x:str(x)).map(lambda x:x.split(',')).map(lambda x:(int(x[0]), int(x[1]), float(x[2])))
sorted_Rdd = prepare_matrix(rows_rdd)
sorted_Rdd.saveAsTextFile('/scratch1/scratchdirs/msingh/sc_paper/experiments/striped_data/rows_matrix')
columns_rdd = rows_rdd.map(lambda x: (x[1],x[0],x[2]))
csorted_rdd = prepare_matrix(columns_rdd)
sorted_Rdd.saveAsTextFile('/scratch1/scratchdirs/msingh/sc_paper/experiments/striped_data/columns_matrix')
print "completed"

d = data.take(2)
r = rdd.take(2)
print d
print r
rdd.map(lambda x:str(x)).map(lambda x:x.split(',')[1]).saveAsTextFile('/scratch1/scratchdirs/msingh/sc_paper/full_output/scratch/columns1')

#.map(lambda x:str(x)).map(lambda x:x.split(',')[1]).saveAsTextFile('/scratch1/scratchdirs/msingh/sc_paper/full_output/scratch/columns')
"""
