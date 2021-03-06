
import sys
from pyspark import SparkContext

def mapToCluster(data, means):
	#data -> a single integer value.
	#means -> list of the mean values.
	closestMean = float(means[0])
	for mean in means:
		if abs(float(data) - float(mean)) < abs(float(data) - float(closestMean)):
			closestMean = float(mean)
	#return the mean value to which this data point belongs to
	return float(closestMean)

def updatemeans(data1, data2):
	#data1,data2 -> tuple of format (meanvalue, count)
	n1 = float(data1[1])
	n2 = float(data2[1])
	avg1 = float(data1[0])
	avg2 = float(data2[0])
	newavg = (n1*avg1 + n2*avg2)/(n1+n2)
	newcount = n1 + n2
	#give (avg1, n1), (avg2, n2), new average will be (n1*avg1 + n2*avg2)/(n1+n2)
	return (newavg,newcount)

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print(str(len(sys.argv))+"Usage: kmeans <datafile> <initialmeanfile>")	
		exit(-1)

	#Create a sparkcontext
	sc = SparkContext(appName="kmeans")
	#load data from the text file
	data = sc.textFile(sys.argv[1]).cache()
	#load initial mean values from the text file
	means = sc.textFile(sys.argv[2])
	#We cannot directory use RDD. It should first be converted into a list to be iterated upon.
	meansList = means.collect()

	#we will run 50 iterations for calculating k means.
	numiter = 50

	for i in range(numiter):
		#For each data point create a tuple of the format (meanvalue,(datapoint, 1))
		clustermap = data.map(lambda p: (mapToCluster(p,meansList),(p,1)))
		#Use reduce operation to calculate new mean value for all the datapoint belonging to the same key
		newmeans = clustermap.reduceByKey(updatemeans)
		#Create a list from the RDD
		meansTupleList = newmeans.collect()
		meansList = []
		for mi in meansTupleList:
			meansList.append(mi[1][0]) 

	finalclustermap = data.map(lambda p: (mapToCluster(p,meansList),p)).sortByKey()
	finalclustermap.saveAsTextFile("output")
	

