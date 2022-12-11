import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
import random
from tqdm import tqdm
import pickle
from datetime import datetime
from collections import Counter

def classes(df_old,df,column,new_name,old_column,n):
    """
    Description:
        Parsing defined column into the intervals. 
    Parameters:
        - df_old: original dataframe provided in Kaggle;
        - df: dataframe that is used for LSH alghorithm;
        - column: name of column is in df;
        - new_name: new title for column;
        - old_column: data column from df_old;
        - n: number of the intervals.
    Return:
        Updated df.
    """
    min = df_old[old_column].min()
    max = df_old[old_column].max()
    # interval will be the length of each class interval 
    interval = int((max - min)/n)
    
    df[new_name]=0

    df.loc[df[column] < min ,new_name]="1_"+new_name
    
    for i in range(1,n,1):
        
        df.loc[(df[column] >= min+interval*(i-1)) & (df[column] < min + interval*i),new_name]=str(i)+"_"+new_name

    df.loc[(df[column] >= min + i*interval),new_name]=str(i+1)+"_"+new_name
    
    return df

def random_hash(nHash,max_shingle):
    """
    Description:
        Randomizing a list of parameters of hash functions. 
    Parameters:
        - nHash: number of generated random hash functions;
        - max_shingle: number of uniq features of cumstomers.
    Return:
        The list of parameters of hash functions.
    """
    rand_params_list = []

    while nHash > 0:
        index = random.randint(0, max_shingle) 
        
        while index in rand_params_list:
            index = random.randint(0, max_shingle) 
            
        rand_params_list.append(index)
        nHash = nHash - 1

    return rand_params_list

def hash_function(a,b,x,max_prime):
    """
    Description:
        Computing hash value.
    Parameters:
        - a: random number between 0 and the number of rows of X;
        - b: random number between 0 and the number of rows of X;
        - x: element of X;
        - max_prime: prime number greater than the number of rows of X.
    Return:
        Computed hash value.
    """
    return (a*x+b)%max_prime

def set_signature_combination(sign_part):
    """
    Description:
        Casting subset of signatures to string format for using as a key in buckets.
    Parameters:
        - sign_part: sublist of signatures.
    Return:
        Casted subset of signatures.
    """
    return " ".join(sign_part)

def jaccard_sim(cust,query,i,df):
    """
    Description:
        Computing jaccard similary of 2 customers.
    Parameters:
        - cust: index of customer from original dataset provided in Kaggle;
        - query: second dataset for comparing;
        - i: index of customer from second dataset;
        - df: dataset provided in Kaggle.
    Return:
        Jaccard similarity of 2 customers.
    """
    customer = [df[column][cust] for column in ['Most_common_location', 'Class_income', 'Class_transaction', 'Class_age'] ]
    q = [query[column][i] for column in ['CustLocation', 'Class_income', 'Class_transaction', 'Class_age'] ]
    customer = set(customer)
    q = set(q)
    intersection = q.intersection(customer)
    union = q.union(customer)
    jaccard = len(intersection)/len(union)
    return jaccard


def most_common(x):
    """
    Description:
        Finding the most common location of transaction of a customer.
    Parameters:
        - x: all the locations of a customer.
    Return:
        Most common location.
    """

    occurence_count = Counter(list(x))
    frequency=occurence_count.most_common(1)[0][1]
    other_frequency=list(occurence_count.values())
    if other_frequency.count(frequency) > 1:
        return None
    
    return occurence_count.most_common(1)[0][0]

def grouping(data):
    """
    Description:
        Grouping the dataframe by CustomerId and creating 3 new columns.
    Parameters:
        - data: original dataframe
    Return:
        Updated dataframe.
    """
    #changing the type of CustomerDOB and TransactionDate
    data.CustomerDOB=pd.to_datetime(data.CustomerDOB)
    data.TransactionDate=pd.to_datetime(data.TransactionDate)
    #dropping customer born in 1800
    data.drop(data[data.CustomerDOB.dt.year == 1800].index, axis=0, inplace=True)
    #fixing date of birth of people born after 2000
    data.loc[data.CustomerDOB.dt.year > 2000, 'CustomerDOB'] = data.loc[data.CustomerDOB.dt.year > 2000, 'CustomerDOB'] - pd.DateOffset(years = 100)

    data_customers=data.groupby("CustomerID").sum()
    data_customers=data_customers.rename(columns={"TransactionAmount (INR)":"TOT TransactionAmount (INR)"})
    data_customers.drop(columns=["CustAccountBalance"],inplace=True)

    #creating Average_transaction_amount
    mean_transaction=pd.DataFrame(data.groupby("CustomerID")["TransactionAmount (INR)"].mean())
    mean_transaction=mean_transaction.rename(columns={"TransactionAmount (INR)":"Average_transaction_amount"})
    data_customers=pd.merge(data_customers,mean_transaction,on="CustomerID")
    
    #creating Most_common_location
    temporary_data=data[['CustomerID','CustLocation']]
    temporary_data['Most_common_location'] = temporary_data.groupby('CustomerID')['CustLocation'].transform(lambda x: most_common(x))
    temporary_data.drop_duplicates(subset=['CustomerID'],inplace=True)
    data_customers=pd.merge(data_customers,temporary_data[["CustomerID",'Most_common_location']],on="CustomerID")
    
    #creating Customer_age
    temporary_data=data[["CustomerID","CustomerDOB"]]
    temporary_data.drop_duplicates(subset=['CustomerID'],inplace=True)
    temporary_data['CustomerAge'] = (( pd.to_datetime('today') - temporary_data.CustomerDOB ) / np.timedelta64(1, 'Y')).round(0)
    temporary_data['CustomerAge'] = temporary_data['CustomerAge'].astype(int)
    data_customers=pd.merge(data_customers,temporary_data[["CustomerID",'CustomerAge']],on="CustomerID")
    
    #creating LastAccountBalance
    temporary_data=data.sort_values("TransactionDate")
    temporary_data=temporary_data.drop_duplicates(subset=["CustomerID"],keep="last")
    temporary_data=temporary_data.rename(columns={'CustAccountBalance':"LastAccountBalance"})
    data_customers=pd.merge(data_customers,temporary_data[["CustomerID","LastAccountBalance"]],on="CustomerID")
    
    
    
    return data_customers

