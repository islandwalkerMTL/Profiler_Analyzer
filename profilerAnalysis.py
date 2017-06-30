####################################################################################
# This program is meant to be incorporated into certain tests within QATrack (http://qatrackplus.com/)
# There are two main modes to the program:
#	1) The ability to compare a static normalized profiler data set to a reference
#   2) The ability to analyze a profiler 'movie' frame by frame (an arc for us, but can be generalized to any movie)
# 
# The reference files should be located in the following directory:
#     H:\DSP\Radio-oncologie\commun\Physique radio-onco\QAtrack\References\Profiler
#
# For information on how to implement within QATrack, see the file QATrack_implementation.docx
#
# Ellis Mitrou (ellis.mitrou.chum@ssss.gouv.qc.ca)
# c2017
####################################################################################
import sys,os.path

# gets the number of frames in a given profiler file.	
def getNumFrames(filename):
    with open(filename,"r") as f:
        arc_data = f.read().splitlines()
	
	for j in range(0,len(arc_data)-1):
		if 'Frames:' in arc_data[j]:
			frameline = j
			numframes = len(arc_data) - frameline - 2
	return numframes
			

######Arc analysis functions#####

#extracts a particular frame's AB and GT data and returns two lists. frameNum starts at 1.
def extractArcFrame(filename,frameNum):
    with open(filename,"r") as f:
        arc_data = f.read().splitlines()
	
	AB_Frame = []
	GT_Frame = []
	for j in range(0,len(arc_data)-1):
		if 'Frames:' in arc_data[j]:
			for k in range(j+1+int(frameNum),j+2+int(frameNum)):
				for col in range(3,66):
					AB_Frame.append(float(arc_data[k].split()[col].replace(',','.'))) #get the AB columns
					
					
					
				for col in range(66,131):
					GT_Frame.append(float(arc_data[k].split()[col].replace(',','.')))
			
			
			return AB_Frame, GT_Frame
#This functions analyzes
def analyzeArc(filename,referencefilename):
	[AB_refDist, AB_refData, GT_refDist, GT_refData, ABflatness_ref, ABsymmetry_ref, GTflatness_ref, GTsymmetry_ref] = load_profilerFile(referencefilename) # for testing purposes only!!!!
	#print 'avgABError(%) ' +  'avgGTError(%) ' + 'ABmax ' + 'GTmax '
	
	#find the number of frames to analyze
	numFrames = getNumFrames(filename)
	overallABmaximum = 0 #Highest AB error
	overallGTmaximum = 0 #Higherst GT error
	count = 0
	avgABsum = 0
	avgGTsum = 0
	for frameNum in range(1,numFrames+1):
		[AB_Frame, GT_Frame] = extractArcFrame(filename,frameNum)
		[averageABError, averageGTError, ABmax, GTmax] = computeError(AB_Frame, GT_Frame, AB_refData,GT_refData )
		avgABsum += averageABError
		avgGTsum += averageGTError
		
		if ABmax > overallABmaximum:
			overallABmaximum = ABmax
		if GTmax > overallGTmaximum:
			overallGTmaximum = GTmax
			
		count +=1
		
	overallAvgAB = avgABsum/count
	overallAvgGT = avgGTsum/count
	
		
		
		
	#Now get average error for -180, -90, 0, +90 and +180 degrees
	#-180 degrees
	[AB_Frame_neg180, GT_Frame_neg180] = extractArcFrame(filename,2)	
	[AB_Frame_neg90, GT_Frame_neg90] = extractArcFrame(filename,numFrames/4)
	[AB_Frame_0, GT_Frame_0] = extractArcFrame(filename,numFrames/2)
	[AB_Frame_90, GT_Frame_90] = extractArcFrame(filename,3*numFrames/4)
	[AB_Frame_180, GT_Frame_180] = extractArcFrame(filename,numFrames)
	
	
	[averageABError_neg180, averageGTError_neg180, ABmax_neg180, GTmax_neg180] = computeError(AB_Frame_neg180, GT_Frame_neg180, AB_refData,GT_refData )
	[averageABError_neg90, averageGTError_neg90, ABmax_neg90, GTmax_neg90] = computeError(AB_Frame_neg90, GT_Frame_neg90, AB_refData,GT_refData )
	[averageABError_0, averageGTError_0, ABmax_0, GTmax_0] = computeError(AB_Frame_0, GT_Frame_0, AB_refData,GT_refData )
	[averageABError_90, averageGTError_90, ABmax_90, GTmax_90] = computeError(AB_Frame_90, GT_Frame_90, AB_refData,GT_refData )
	[averageABError_180, averageGTError_180, ABmax_180, GTmax_180] = computeError(AB_Frame_180, GT_Frame_180, AB_refData,GT_refData )
	
	return overallAvgAB, overallAvgGT, overallABmaximum, overallGTmaximum, averageABError_neg180, averageGTError_neg180, ABmax_neg180, GTmax_neg180, averageABError_neg90, averageGTError_neg90, ABmax_neg90, GTmax_neg90, averageABError_0, averageGTError_0, ABmax_0, GTmax_0,averageABError_90, averageGTError_90, ABmax_90, GTmax_90, averageABError_180, averageGTError_180, ABmax_180, GTmax_180

		
		
	


#### Static and general analysis functions ####		
#Load a profiler file and split it in AB and GT. 
#returns AB coordinates, AB data, GT coordinates, GT data, AB flatness value, AB symmetry value. GT flatness value and GT symmetry value
def load_profilerFile(filename):
    with open(filename,"r") as f:
        profiler_data = f.read().splitlines()
		
		
		
	#declare data variables
	ABdist = []
	ABdata = []
	GTdist = []
	GTdata = []

	
	
	
	for j in range(0,len(profiler_data)-1):
		
		
	#find AB flatness
		if 'X Axis Analysis' in profiler_data[j]:
			ABflatness = float((profiler_data[j+7].split('perc')[1]).replace(',', '.'))
			ABsymmetry = float((profiler_data[j+8].split('perc')[1]).replace(',', '.'))

		
		
	#find AB data
		if 'Detector ID	X Axis' in profiler_data[j]:
			for k in range(1,64):
				ABdist.append(float(profiler_data[j+k].split()[0].replace(',', '.')))
				ABdata.append(float(profiler_data[j+k].split()[1].replace(',', '.')))
			
			
	#find GT data
	
		if 'Y Axis Analysis' in profiler_data[j]:
			GTflatness = float((profiler_data[j+7].split('perc')[1].replace(',', '.')))
			GTsymmetry = float((profiler_data[j+8].split('perc')[1].replace(',', '.')))
	
	for j in range(0,len(profiler_data)-1):
		if 'Detector ID	Y Axis' in profiler_data[j]:
			for k in range(1,66):
				GTdist.append(float((profiler_data[j+k].split()[0]).replace(',', '.')))
				GTdata.append(float((profiler_data[j+k].split()[1]).replace(',', '.')))
	
    return 	ABdist, ABdata, GTdist, GTdata, ABflatness, ABsymmetry, GTflatness, GTsymmetry


#Computes average and maximum errors within +-10 cm of central axis in AB and GT directions
def computeError(ABdata,GTdata, AB_refData, GT_refData):
	
	ABpoints = 0
	GTpoints = 0
	
	ABdiffsum = 0
	GTdiffsum = 0
	
	ABmax = 0
	GTmax = 0
	for datapos in range(12,51):
		ABdifference = 100*abs(float(ABdata[datapos]) - float(AB_refData[datapos]))/float(AB_refData[datapos])
		ABdiffsum += ABdifference
		
		
		if ABdifference > ABmax:
			ABmax = ABdifference
		ABpoints+=1
		
	
		
	
	
	for datapos in range(12,53):
		GTdifference = 100*abs(float(GTdata[datapos]) - float(GT_refData[datapos]))/float(GT_refData[datapos])
		GTdiffsum += GTdifference
		
		if GTdifference > GTmax:
			GTmax = GTdifference
		
		GTpoints+=1
	
	
		
	averageABError = ABdiffsum/ABpoints
	averageGTError = GTdiffsum/GTpoints
	return averageABError, averageGTError, ABmax, GTmax

	
	

def analyzeStatic(fname, ref_file):
	   


    #Load the reference file and file to be analyzed 
	[AB_refDist, AB_refData, GT_refDist, GT_refData, ABflatness_ref, ABsymmetry_ref, GTflatness_ref, GTsymmetry_ref] = load_profilerFile(ref_file)
	[ABdist, ABdata, GTdist, GTdata, ABflatness, ABsymmetry, GTflatness, GTsymmetry] = load_profilerFile(fname)
	
	
	
	#Calculate AB and GT Error for central 20 cm of the field.
	
	[averageABError, averageGTError, ABmax, GTmax] = computeError(ABdata,GTdata, AB_refData,GT_refData)
	
	return ABsymmetry, ABflatness, GTsymmetry, GTflatness, ABmax, GTmax, averageABError, averageGTError
	



#Create a python dictionary with the results from the analysis function to populate qatrack results.
profiler_results = dict()

#### QATrack integration begins here ####
	
#To test QA track implementation use this in the file upload composite test calculation box. Just uncomment the necessary lines


#For static
# profiler_results['symAB'] = float(100)
# profiler_results['homAB'] = float(101)
# profiler_results['symGT'] = float(102)
# profiler_results['homGT'] = float(103)
# profiler_results['maxAB'] = float(104)
# profiler_results['maxGT'] = float(105)
# profiler_results['meanAB'] = float(106)
# profiler_results['meanGT'] = float(107)
# result = profiler_results

#For Arc
# profiler_results['overallAvgAB'] =1
# profiler_results['overallAvgGT'] =2
# profiler_results['overallABmaximum'] =3
# profiler_results['overallGTmaximum'] =4
# profiler_results['averageABError_neg180']=5
# profiler_results['averageGTError_neg180']=6
# profiler_results['ABmax_neg180']=7
# profiler_results['GTmax_neg180']=8
# profiler_results['averageABError_neg90']=9
# profiler_results['averageGTError_neg90']=10
# profiler_results['ABmax_neg90']=11
# profiler_results['GTmax_neg90']=12
# profiler_results['averageABError_0']=13
# profiler_results['averageGTError_0']=14
# profiler_results['ABmax_0']=15
# profiler_results['GTmax_0']=16
# profiler_results['averageABError_90']=17
# profiler_results['averageGTError_90']=18
# profiler_results['ABmax_90']=19
# profiler_results['GTmax_90']=20
# profiler_results['averageABError_180']=21
# profiler_results['averageGTError_180']=22
# profiler_results['ABmax_180']=23
# profiler_results['GTmax_180']=24









#From Danis Blais' catphan analysis program
mode_command = False
if 'FILE' in vars() or 'FILE' in globals():
    # on recupere le nom du fichier a partir de l'objet FILE 
    # qui nous est passe et on ferme le fichier pour ne pas avoir de conflit
    filename = FILE.name
    FILE.close()
else:
    # le programme a ete lance en dehors de QATrack+
    if len(sys.argv) < 2:
        print 'SVP specifiez en argument le nom du fichier'
        quit()
    else:
        filename = str(sys.argv[1])
        if not os.path.isfile(filename):
            print "Le fichier specifie n'existe pas"
            quit()
        mode_command = True


		
#The various tests must have this in their composite test calculation procedure so that the results populate.
#eg for 6 MV:
	#result = profiler_stat_6mv['symAB']
	#result = profiler_stat_6mv['meanAB']
	#result = profiler_stat_6mv['meanGT']
	#result = profiler_stat_6mv['maxAB']
	#result = profiler_stat_6mv['symGT']
	#result = profiler_stat_6mv['homAB']
	#result = profiler_stat_6mv['homGT']
	#result = profiler_stat_6mv['maxGT']		



#Define reference file

#ref_file = '/chum/dsp/Radio-oncologie/commun/Physique' + ' ' + 'radio-onco/QAtrack/References/Profiler/VERSA_ref6MV.txt'
#ref_file = '/chum/dsp/Radio-oncologie/commun/Physique' + ' ' + 'radio-onco/QAtrack/References/Profiler/VERSA_ref10MV.txt'
#ref_file = '/chum/dsp/Radio-oncologie/commun/Physique' + ' ' + 'radio-onco/QAtrack/References/Profiler/VERSA_ref18MV.txt'
#ref_file = '/chum/dsp/Radio-oncologie/commun/Physique' + ' ' + 'radio-onco/QAtrack/References/Profiler/VERSA_ref6FFF.txt'
#ref_file = '/chum/dsp/Radio-oncologie/commun/Physique' + ' ' + 'radio-onco/QAtrack/References/Profiler/VERSA_ref10FFF.txt'
#ref_file = 'VERSA_ref6MEV.txt'
#ref_file = 'VERSA_ref9MEV.txt'
#ref_file = 'VERSA_ref12MEV.txt'
#ref_file = 'VERSA_ref15MEV.txt'

#ref_file = 'EDGE_ref6MV.txt'
#ref_file = 'EDGE_ref6FFF.txt'
#ref_file = 'EDGE_ref10FFF.txt'

#ref_file = 'IX_ref6MV.txt'
#ref_file = 'IX_ref23MV.txt'



#uncomment the analysis that you wish to perform:

#For static analysis:
#[profiler_results['symAB'], profiler_results['homAB'], profiler_results['symGT'], profiler_results['homGT'], profiler_results['maxAB'], profiler_results['maxGT'], profiler_results['meanAB'], profiler_results['meanGT']] = analyzeStatic(filename, ref_file)
#For arc analysis:
#[profiler_results['overallAvgAB'], profiler_results['overallAvgGT'], profiler_results['overallABmaximum'], profiler_results['overallGTmaximum'], profiler_results['averageABError_neg180'], profiler_results['averageGTError_neg180'], profiler_results['ABmax_neg180'], profiler_results['GTmax_neg180'], profiler_results['averageABError_neg90'], profiler_results['averageGTError_neg90'], profiler_results['ABmax_neg90'], profiler_results['GTmax_neg90'], profiler_results['averageABError_0'], profiler_results['averageGTError_0'], profiler_results['ABmax_0'], profiler_results['GTmax_0'],profiler_results['averageABError_90'], profiler_results['averageGTError_90'], profiler_results['ABmax_90'], profiler_results['GTmax_90'], profiler_results['averageABError_180'], profiler_results['averageGTError_180'], profiler_results['ABmax_180'], profiler_results['GTmax_180']] = analyzeArc(filename, ref_file)



#qatrack needs this line.
result = profiler_results 

	
	
