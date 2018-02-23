###############################################################################
# This program is meant to be incorporated into certain tests within QATrack 
# (http://qatrackplus.com/)
# There are two main modes to the program:
#   1) The ability to compare a static normalized profiler data 
#      set to a reference
#   2) The ability to analyze a profiler 'movie' frame by frame 
#      (an arc for us, but can be generalized to any movie)
# 
# The reference files should be located in the following directory:
# H:\DSP\Radio-oncologie\commun\Physique radio-onco\QAtrack\References\Profiler
#
# For information on how to implement within QATrack, see the file 
# QATrack_implementation.docx
#
# Ellis Mitrou (ellis.mitrou.chum@ssss.gouv.qc.ca)
# c2017
###############################################################################
import sys,os.path
import re
import numpy
from scipy import interpolate

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

#extracts a particular frame's AB and GT data and returns two lists. 
# frameNum starts at 1.
def extractArcFrame(filename,frameNum):
    with open(filename,"r") as f:
        arc_data = f.read().splitlines()    
    AB_Frame = []
    GT_Frame = []
    for j in range(0,len(arc_data)-1):
        if 'Frames:' in arc_data[j]:
            for k in range(j+1+int(frameNum),j+2+int(frameNum)):
                for col in range(3,66):
                    AB_Frame.append(float(arc_data[k].split()[col].
                                    replace(',','.'))) #get the AB columns
                for col in range(66,131):
                    GT_Frame.append(
                    float(arc_data[k].split()[col].replace(',','.')))
            return AB_Frame, GT_Frame
            
#This functions analyzes
def analyzeArc(filename,referencefilename, particletype):
    [AB_refDist, AB_refData, GT_refDist, GT_refData, ABflatness_ref,
     ABsymmetry_ref, GTflatness_ref,
     GTsymmetry_ref] = load_profilerFile(referencefilename) 
    
    #find the number of frames to analyze
    numFrames = getNumFrames(filename)
    
    #initialize some stuff:
    overallAB_avg_maximum = 0 #Highest AB error
    overallGT_avg_maximum = 0 #Higherst GT error
    count = 0.00001
    avgABsum = 0
    avgGTsum = 0
    #The frame that has the max avg error in GT (to be converted to an angle):
    frameGTavg_max = 0    
    #The frame that has the max avg error in AB (to be converted to an angle):
    frameABavg_max = 0    
    
    if particletype.upper() == 'PHOTON':
        startAngle = -180 #bipolar (photon arc)
        stopAngle = 180 #bipolar (photon arc)        
        
    elif particletype.upper() == 'ELECTRON':
        startAngle = -120 #bipolar (electron arc)
        stopAngle = 120 #bipolar (electron arc)
        
    else:
        print ('particletype has not been correctly defined. Correct '
        'options are (PHOTON) or (ELECTRON)')
        quit()
    
    # Threshold to account for profiler noise and dropped counts (%)
    # If the error for a frame is greather than 'threshold' the following
    # 'numFrames2skip' frames will be skipped
    threshold = 3
    numFrames2skip = 5
    numSkippedFrames = 0
    startFrame = 20
    
    frameNum = range(startFrame,numFrames+1) #skip the first 20 frames
    frameNum_iter = iter(frameNum)
    
    for frame in frameNum_iter:
        [AB_Frame, GT_Frame] = extractArcFrame(filename,frame)
        [averageABError, averageGTError, ABmax, GTmax] = computeError(
        AB_Frame, GT_Frame, AB_refData,GT_refData,particletype )

        if (averageABError > threshold) | (averageGTError > threshold):
            numSkippedFrames += 1
            for i in range(0,numFrames2skip):
                
                next(frameNum_iter,None) #skipping happens in this for loop
                    
        else:
            avgABsum += averageABError
            avgGTsum += averageGTError
        
            if averageABError > overallAB_avg_maximum:
                overallAB_avg_maximum = averageABError
                frameABavg_max = frame
            
            if averageGTError > overallGT_avg_maximum:
                overallGT_avg_maximum = averageGTError
                frameGTavg_max = frame

        
        
            count +=1


    overallAvgAB = avgABsum/count
    overallAvgGT = avgGTsum/count
    #Convert frame numbers where we find the maximum 
    #average difference to a bipolar angle:
    angleABavg_max = (
    (stopAngle-startAngle)*frameABavg_max/numFrames) - stopAngle
    angleGTavg_max = (
    (stopAngle-startAngle)*frameGTavg_max/numFrames) - stopAngle

    analyzeArc_return = [overallAvgAB, overallAvgGT, overallAB_avg_maximum,
    angleABavg_max, overallGT_avg_maximum, angleGTavg_max, numSkippedFrames]
    return analyzeArc_return

#### Static and general analysis functions ####     
# Load a profiler file and split it in AB and GT. 
# returns AB coordinates, AB data, GT coordinates, GT data,
# AB flatness value, AB symmetry value. GT flatness value
# and GT symmetry value

def load_profilerFile(filename):
    with open(filename,"r") as f:
        profiler_data = f.read().splitlines()
        
    #declare data variables
    ABdist = []
    ABdata = []
    GTdist = []
    GTdata = []
    
    for j in range(0,len(profiler_data)-1):
      #  print profiler_data[j]
        
    #find AB flatness
        if 'XAxisAnalysis' in re.sub('[\s+]', '', profiler_data[j]):
            ABflatness = float(
            (profiler_data[j+7].split('perc')[1]).replace(',', '.'))
            ABsymmetry = float(
            (profiler_data[j+8].split('perc')[1]).replace(',', '.'))

    #find AB data
        if 'DetectorIDXAxis' in re.sub('[\s+]', '', profiler_data[j]):
            for k in range(1,64):
                ABdist.append(float(
                profiler_data[j+k].split()[0].replace(',', '.')))
                ABdata.append(float(
                profiler_data[j+k].split()[1].replace(',', '.')))
            
    #find GT data
    
        if 'YAxisAnalysis' in re.sub('[\s+]', '', profiler_data[j]):
            GTflatness = float(
            (profiler_data[j+7].split('perc')[1].replace(',', '.')))
            GTsymmetry = float(
            (profiler_data[j+8].split('perc')[1].replace(',', '.')))
    
    for j in range(0,len(profiler_data)-1):
        if 'DetectorIDYAxis' in re.sub('[\s+]', '', profiler_data[j]):
            for k in range(1,66):
                GTdist.append(float(
                (profiler_data[j+k].split()[0]).replace(',', '.')))
                GTdata.append(float(
                (profiler_data[j+k].split()[1]).replace(',', '.')))
    
    
    
    #perform caxcorrection:
    ABdataCAXCORRECTED = caxcorrect(ABdist,ABdata)
    GTdataCAXCORRECTED = caxcorrect(GTdist,GTdata)
    
    
    load_profilerFile_return = [ABdist, ABdataCAXCORRECTED, GTdist,
    GTdataCAXCORRECTED, ABflatness, ABsymmetry, GTflatness, GTsymmetry]
    return  load_profilerFile_return


#Perform a CAX correction on the data
#Returns the y axis (ie. AB or GT data) only
def caxcorrect(x0, y0):

    x0_A=x0[:int(len(x0)/2)]
    x0_B=x0[int(len(x0)/2):]
    y0_A=y0[:int(len(y0)/2)]
    y0_B=y0[int(len(y0)/2):]
    
    #generate interp1d functions to find 25%
    f_A=interpolate.interp1d(y0_A,x0_A)
    f_B=interpolate.interp1d(y0_B,x0_B)



    #Shift the data by half of the difference of the 25% positions on each side
    xNEW = x0 - (f_A(25) + f_B(25))/2.0

    #generate interp1d function to interpolate back into the original
    #profiler coordinate system

    f_caxcorrected = interpolate.interp1d(xNEW,y0,fill_value="extrapolate")
    y_caxcorrected = f_caxcorrected(x0)
    
    return y_caxcorrected

#Computes average and maximum errors within +-10 cm of 
#central axis in AB and GT directions
def computeError(ABdata,GTdata, AB_refData, GT_refData,particletype):
    ABpoints = 0
    GTpoints = 0
    
    ABdiffsum = 0
    GTdiffsum = 0
    
    ABmax = 0
    GTmax = 0
    
    
    
    if particletype.upper() == 'PHOTON':
        ABstart = 12
        ABstop = 51
        GTstart = 12
        GTstop = 53
        
        
    elif particletype.upper() == 'ELECTRON':
        ABstart = 16
        ABstop = 46
        GTstart = 16
        GTstop = 48
        
    else:
        print ('particletype has not been correctly defined. Correct '
        'options are (PHOTON) or (ELECTRON)')
        quit()

    
    for datapos in range(int(ABstart),int(ABstop)):
        ABdifference = 100*abs(float(
        ABdata[datapos]) - float(
        AB_refData[datapos]))/float(AB_refData[datapos])
        ABdiffsum += ABdifference
        
        
        if ABdifference > ABmax:
            ABmax = ABdifference
        ABpoints+=1
        
    
    for datapos in range(int(GTstart),int(GTstop)):
        GTdifference = 100*abs(float(GTdata[datapos]) - float(
        GT_refData[datapos]))/float(GT_refData[datapos])
        GTdiffsum += GTdifference
        
        if GTdifference > GTmax:
            GTmax = GTdifference
        
        GTpoints+=1
        
    averageABError = ABdiffsum/ABpoints
    averageGTError = GTdiffsum/GTpoints
    return averageABError, averageGTError, ABmax, GTmax


def analyzeStatic(fname, ref_file,particletype):
    #Load the reference file and file to be analyzed 
    [AB_refDist, AB_refData, GT_refDist, GT_refData,
        ABflatness_ref, ABsymmetry_ref, GTflatness_ref,
            GTsymmetry_ref] = load_profilerFile(ref_file)
    
    [ABdist, ABdata, GTdist, GTdata, ABflatness,
        ABsymmetry, GTflatness, GTsymmetry] = load_profilerFile(fname)
    
    
    
    #Calculate AB and GT Error for central 20 cm of the field.
    
    [averageABError, averageGTError, ABmax, GTmax] = computeError(
                              ABdata,GTdata, AB_refData,GT_refData
                              ,particletype)
    
    static_return = [ABsymmetry, ABflatness, GTsymmetry,
    GTflatness, ABmax, GTmax, averageABError, averageGTError]
    
    return static_return
    

#Create a python dictionary with the results from the analysis
#function to populate qatrack results.
profiler_results = dict()

#### QATrack integration begins here ####
    
#To test QA track implementation use this in the file upload
# composite test calculation box. Just uncomment the necessary lines


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
            print "Le fichier, %(filenameerror)s specifie n'existe pas" %{
            "filenameerror":filename}
            quit()
        mode_command = True


        
#The various tests must have this in their composite test
# calculation procedure so that the results populate.
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

ref_path = ('/chum/dsp/Radio-oncologie/commun/Physique radio-onco/'
            'QAtrack/References/Profiler/')


#ref_file = ref_path + 'VERSA_ref6MV.txt'
#ref_file = ref_path + 'VERSA_ref10MV.txt'
#ref_file = ref_path + 'VERSA_ref18MV.txt'
#ref_file = ref_path + 'VERSA_ref6FFF.txt'
#ref_file = ref_path + 'VERSA_ref10FFF.txt'
#ref_file = ref_path + 'VERSA_ref6MEV.txt'
#ref_file = ref_path + 'VERSA_ref9MEV.txt'
#ref_file = ref_path + 'VERSA_ref12MEV.txt'
#ref_file = ref_path + 'VERSA_ref15MEV.txt'

#ref_file = ref_path + 'EDGE_ref6MV.txt'
#ref_file = ref_path + 'EDGE_ref6FFF.txt'
#ref_file = ref_path + 'EDGE_ref10FFF.txt'
#ref_file = ref_path + 'EDGE_ref25FFF.txt'

#ref_file = ref_path + 'SALLEG_VARIAN_ref6MV.txt'


#uncomment the analysis that you wish to perform:

#For static analysis of photon beams:
#[profiler_results['symAB'], profiler_results['homAB'],
# profiler_results['symGT'], profiler_results['homGT'],
# profiler_results['maxAB'], profiler_results['maxGT'],
# profiler_results['meanAB'], profiler_results['meanGT']
# ] = analyzeStatic(filename, ref_file, 'PHOTON')
 
#For static analysis of electron beams:
#[profiler_results['symAB'], profiler_results['homAB'],
# profiler_results['symGT'], profiler_results['homGT'],
# profiler_results['maxAB'], profiler_results['maxGT'],
# profiler_results['meanAB'], profiler_results['meanGT']
# ] = analyzeStatic(filename, ref_file, 'ELECTRON') 

#For arc analysis of photon beams:
#[profiler_results['overallAvgAB'], profiler_results['overallAvgGT'],
# profiler_results['overallAB_avg_maximum'], profiler_results['angleABavg_max'],
# profiler_results['overallGT_avg_maximum'], profiler_results['angleGTavg_max'],
# profiler_results['numSkippedFrames']
#] = analyzeArc(filename, ref_file, 'PHOTON')

#For arc analysis of electron beams:
#[profiler_results['overallAvgAB'], profiler_results['overallAvgGT'],
# profiler_results['overallAB_avg_maximum'], profiler_results['angleABavg_max'],
# profiler_results['overallGT_avg_maximum'], profiler_results['angleGTavg_max'],
# profiler_results['numSkippedFrames']
#] = analyzeArc(filename, ref_file, 'ELECTRON')

#qatrack needs this line.
result = profiler_results 
print result
