import matplotlib.pyplot as plt
import numpy as np
import tarfile, os
import math
import time
from ROOT import TCanvas, TGraph, TDatime, TAxis, TLegend, TMultiGraph

def txtfile(fill, NUM, place):
    """
        Require two folders named ATLAS and CMS to save tarballs
    """
    lumi = []
    times = []
    if place == "A":
        os.chdir("ATLAS")
    elif place == "C":
        os.chdir("CMS")
    else:
        raise AssertionError("ATLAS=A, CMS=C")
    tar_name = str(fill)+".tgz"
    tar = tarfile.open(mode="r",name=tar_name)
    
    for tarinfo in tar: 
        file_name = tarinfo.name
        sp_file_name = file_name.split("_")
        if len(sp_file_name)==4 and str(int(NUM)) == sp_file_name[2]:
            tfl = tar.extractfile(tarinfo)
            break
    
    content = tfl.readlines()
    for line in content:
        sp_line = line.split(" ")
        lumi.append(float(sp_line[2]))
        times.append(float(sp_line[0]))
    tfl.close()
    
    tar.close()
    os.chdir("..")
    return([times,lumi])

def twst(slow_time,fast_vtime):
    two_vtime = []
    diff_list = []
    for i in range(len(fast_vtime)):
        diff_list.append(abs(fast_vtime[i]-slow_time))
    sdiff_list = sorted(diff_list)
    time1 = sdiff_list[0]
    time2 = sdiff_list[1]
    index_time1 = diff_list.index(time1)
    index_time2 = diff_list.index(time2)
    if index_time2 == index_time1:
        index_time2 = index_time1+1
    return([index_time1,index_time2])

def BCIDratio(fill,NUM):

    
    ATLAS_vtime = txtfile(fill, NUM, 'A')[0] 
    ATLAS_vlumi = txtfile(fill, NUM, 'A')[1]
    
    CMS_vtime = txtfile(fill, NUM, 'C')[0]
    CMS_vlumi = txtfile(fill, NUM, 'C')[1]
 
    siCMS_vtime = ATLAS_vtime
    siCMS_vlumi = []
    ratio = []
    
    # interpolation CMS to ATLAS format
    for t in ATLAS_vtime:
        i = twst(t,CMS_vtime)[0]   
        j = twst(t,CMS_vtime)[1]
        t1 = CMS_vtime[i]
        t2 = CMS_vtime[j]
        l1 = CMS_vlumi[i]
        l2 = CMS_vlumi[j]
        l = ((l2-l1)*(t-t1)/(t2-t1)) + l1
        siCMS_vlumi.append(l)
  
    #calculate lumi ratio 
    for k in range(len(ATLAS_vtime)):
        ratio.append(((ATLAS_vlumi[k]/siCMS_vlumi[k])-1)*100)

    return(np.median(ratio))

def fillplot(fill):
    """
        Require "token" tarballs in current directory ( same names as in ATLAS and CMS folders)
    """
    
    BCIDs = []
    NUMs = []
    tar_name = str(fill)+".tgz"
    tar = tarfile.open(mode="r",name=tar_name)
    
    for tarinfo in tar: 
        file_name = tarinfo.name
        if len(file_name.split("_"))==4:
            sp_file_name = file_name.split("_")
            NUM = float(sp_file_name[2])
            NUMs.append(int(NUM))
            BCIDs.append(((NUM-1)/10)+1)
    tar.close()

    BCIDs = sorted(BCIDs)
    NUMs = sorted(NUMs)
    NUMs.append(40010) #prevent index out of range
    BCIDs.append(4000) #prevent index out of range
    ratio = [BCIDratio(fill,NUMs[0])]
    subratio = [BCIDratio(fill,NUMs[0])]
    subBCIDs = [BCIDs[0]]
    count = 1
   
    # produce plots trains by trains 
    for i in range(len(BCIDs)):
        if BCIDs[i+1] - BCIDs[i] < 20:   # rough intervals between two consecutive trains 
            ratio.append(BCIDratio(fill,NUMs[i+1]))
            subratio.append(BCIDratio(fill,NUMs[i+1]))
            subBCIDs.append(BCIDs[i+1])
        else:
            c1 = TCanvas("c1","The ratio of each BCID per fill",200,10,700,500)
            gr1 = TGraph(len(subratio),np.array(subBCIDs),np.array(subratio))
            gr1.SetMarkerColor(2)
            gr1.SetMarkerStyle(7)
            gr1.SetTitle( "Fill No. " + str(fill) )
            gr1.GetXaxis().SetTitle( 'BCID' )
            gr1.GetYaxis().SetRangeUser(-10, 10)
            gr1.GetYaxis().SetTitle( 'Ratio ATLAS/CMS (%)' )
            gr1.Draw( 'AP' )
            c1.SaveAs(str(fill)+"_Train" + str(count) +".pdf")
            c1.Update()
            time.sleep(5.5)
           
            count+=1
            if i == len(BCIDs)-2:
                break
            else:
                subratio = [BCIDratio(fill,NUMs[i+1])]
                subBCIDs = [BCIDs[i+1]]
                ratio.append(BCIDratio(fill,NUMs[i+1]))
        
fillplot(6266)  #change fills here 
