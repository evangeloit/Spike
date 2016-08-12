import numpy as np
import pylab as plt
import pickle
import os;
#from Parameters import *


class InfoAnalysis(object):
    
    def singleCellInfoAnalysis(self,phases,saveImage = True, showImage = True, nBins=3,weightedAnalysis = False,plotAllSingleCellInfo = False):
        fig=plt.figure(4 , figsize=(20, 5),dpi=150);
        
#         Parameters

        nExcitCells = 32*32;
        nInhibCells = 16*16;
        

        nObj = 5;
        nTrans = 2;
        nLayers = 4;
        presentationTime = 1.0;
        

        nInfoCalc = nExcitCells;
        
        phaseIndex = 1;
        for phase in phases:

#             fn_id = "../output/Neurons_SpikeIDs_" + phase + "_Epoch0.txt";
#             fn_t = "../output/Neurons_SpikeTimes_" + phase + "_Epoch0.txt";
#             
#             spikeIDs = np.loadtxt(fn_id);
#             spikeTimes = np.loadtxt(fn_t);
            
            fn_id = "../output/Neurons_SpikeIDs_" + phase + "_Epoch0.bin";
            fn_t = "../output/Neurons_SpikeTimes_" + phase + "_Epoch0.bin";  
            dtIDs = np.dtype('int32');
            dtTimes = np.dtype('f4');
            
            spikeIDs = np.fromfile(fn_id, dtype=dtIDs);
            spikeTimes = np.fromfile(fn_t, dtype=dtTimes);
            

            FR = np.zeros((nObj, nTrans,nLayers, nExcitCells));
            for l in range(nLayers):
                cond_ids = (l*(nExcitCells+nInhibCells) < spikeIDs) & (spikeIDs < l*(nInhibCells+nExcitCells)+nExcitCells);
                spikeIDs_layer = np.extract(cond_ids, spikeIDs);
                spikeTimes_layer = np.extract(cond_ids, spikeTimes);
                for obj in range(nObj):
                    for trans in range(nTrans):
                        cond_stim = ((presentationTime*(obj*nTrans+trans)) < spikeTimes_layer) & (spikeTimes_layer < (presentationTime*(obj*nTrans+trans+1)));
                        spikeIDs_stim = np.extract(cond_stim,spikeIDs_layer)-((nExcitCells+nInhibCells)*l);
                        for id in spikeIDs_stim:
                            FR[obj,trans,l,id]=FR[obj,trans,l,id]+1;
#             FR = np.random.rand(nObj, nTrans,nLayers, nExcitCells)
                        
            
#             print FR;
                        
            performanceMeasure = 0.0;
            
            for l in range(nLayers):
                #normalize
                if FR[:,:,l,:].max()>0.001:
                    FR_norm = (FR-FR[:,:,l,:].min())/(FR[:,:,l,:].max()-FR[:,:,l,:].min());
#                     FR_norm = FR/FR[:,:,l,:].max();
#                     FR_norm = FR/FR.max();
                    
                    FR_tmp = FR_norm;
                else:
                    FR_tmp = FR;
                    
                infos = np.zeros(nExcitCells);
                
                sumPerBin = np.zeros((nExcitCells,nBins));
                sumPerObj = nTrans;
                sumPerCell = nTrans*nObj;
                IRs = np.zeros((nObj,nExcitCells));#I(R,s) single cell information
                IRs_weighted = np.zeros((nObj,nExcitCells));#I(R,s) single cell information
                pq_r = np.zeros(nObj)#prob(s') temporally used in the decoing process
                Ps = 1/nObj   #Prob(s) 
                
                
                print("**Loading data**")
                binMatrix = np.zeros((nExcitCells, nObj, nBins));# #number of times when fr is classified into a specific bin within a specific objs's transformations
                for obj in range(nObj):
                    print str(obj) + '/' + str(nObj);
                    for trans in range(nTrans):
                        for cell in range(nExcitCells):
#                             bin = np.around(FR_tmp[obj,trans,l,cell]*(nBins-1));
                            bin = min(np.floor((FR_tmp[obj,trans,l,cell])*(nBins)),nBins-1)
                            binMatrix[cell,obj,bin]=binMatrix[cell,obj,bin]+1;
                
                #print binMatrix;
                
                print "** single-cell information analysis **";
                # Loop through all cells to calculate single cell information
                for cell in range(nExcitCells):
                    # For each cell, count the number of transforms per bin
                    for bin in range(nBins):
                        for obj in range(nObj):
                            sumPerBin[cell,bin]+=binMatrix[cell,obj,bin];
            
                    # Calculate the information for cell_x cell_y per stimulus
                    for obj in range(nObj):
                        for bin in range(nBins):
                            Pr = sumPerBin[cell,bin]/sumPerCell;
                            Prs = binMatrix[cell,obj,bin]/sumPerObj;
                            if(Pr!=0 and Prs!=0 and Pr<Prs):
                                IRs[obj,cell]+=(Prs*(np.log2(Prs/Pr)));#*((bin-1)/(nBins-1)); #could be added to weight the degree of firing rates.
                                #IRs(row,col,obj)=IRs(row,col,obj)+(Prs*(log2(Prs/Pr)))*((bin-1)/(nBins-1)); #could be added to weight the degree of firing rates.
                                IRs_weighted[obj,cell]+=(Prs*(np.log2(Prs/Pr)))*((bin)/(nBins-1)); #could be added to weight the degree of firing rates.
             
                if (weightedAnalysis):
                    IRs = IRs_weighted;
                
                
                if (plotAllSingleCellInfo):
                    IRs_sorted = np.sort(IRs*-1)*-1;
                    plt.subplot(2,nLayers,(phaseIndex-1)*nLayers+(l+1));

#                     plt.plot(np.transpose(IRs_sorted), color='k');
                    plt.plot(np.transpose(IRs_sorted));
                    
                    plt.ylim([-0.05, np.log2(nObj)+0.05]);
                    plt.xlim([0, nExcitCells])
                    plt.title("Layer " + str(l));
                    plt.ylabel("Information [bit]");
                    plt.xlabel("Cell Rank");
                    
                else:
                    IRs = np.max(IRs,axis=0);
                    
                    IRs_sorted = np.transpose(np.sort(IRs));
                    reversed_arr = IRs_sorted[::-1]
                
                
                    infos = reversed_arr;
                
                    plt.subplot(1,nLayers,l+1)
                    if phaseIndex==1:
                        plt.plot(np.transpose(infos), linestyle='--', color='k');
                    elif phaseIndex==2:
                        plt.plot(np.transpose(infos), linestyle='-', color='k');
                    plt.ylim([-0.05, np.log2(nObj)+0.05]);
                    plt.xlim([0, nExcitCells])
                    plt.title("Layer " + str(l));
                    plt.ylabel("Information [bit]");
                    plt.xlabel("Cell Rank");
                    plt.hold(True);
                        
                

#         plt.savefig(os.path.split(os.path.realpath(__file__))[0] +"/Results/"+experimentName+"/singleCellInfo_bin"+str(nBins)+".png");
#         plt.savefig(os.path.split(os.path.realpath(__file__))[0] +"/Results/"+experimentName+"/singleCellInfo_bin"+str(nBins)+".eps");
            phaseIndex+=1;
        
        if showImage:
            plt.show();
        if saveImage:
            if (plotAllSingleCellInfo):
                fig.savefig("../output/SingleCellInfo_ALL.png");
                fig.savefig("../output/SingleCellInfo_ALL.eps");
            else:
                  fig.savefig("../output/SingleCellInfo_MAX.png");
                  fig.savefig("../output/SingleCellInfo_MAX.eps");              
    
            print("figure SingleCellInfo.png is exported in Results") 