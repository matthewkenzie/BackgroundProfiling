#!/usr/bin/env python

import sys
import os

from optparse import OptionParser
parser=OptionParser()
parser.add_option("-c","--cat",type="int",default=0)
parser.add_option("-m","--expMasses",default=[],action="append")
parser.add_option("-f","--files",default=[],action="append")
parser.add_option("-D","--outDir")
parser.add_option("-d","--datfile")
(options,args)=parser.parse_args()

coverageValues=[0.1,0.5,1.,2.]
masserr = 5 

os.system('mkdir -p %s'%options.outDir)

import ROOT as r
r.gROOT.SetBatch()

dummyHist = r.TH1F('dummy','',5,105,155)
dummyHist.GetXaxis().SetTitle("#m_{H}")
dummyHist.GetYaxis().SetTitle("Coverage")
dummyHist.SetStats(0)

muBiasBand = r.TGraphErrors()
muBiasBand.SetLineColor(r.kGray)
muBiasBand.SetFillColor(r.kGray)
muBiasBand.SetFillStyle(1001)
muBiasBand.SetMarkerColor(r.kGray)
muPullBand = r.TGraphErrors()
muPullBand.SetLineColor(r.kGray)
muPullBand.SetFillColor(r.kGray)
muPullBand.SetFillStyle(1001)
muPullBand.SetMarkerColor(r.kGray)

scanTypes=['Fab','Paul','Chi2','AIC']
graphCol=[r.kBlue,r.kRed,r.kGreen+1,r.kMagenta]
graphFil=[3002,3002,3002,3002]
label=['Hgg Nominal Pol','Envelope (no pen)','Envelope (1/dof pen)','Envelope (2/dof pen)']
plotTypes=['Coverage','Bias','Pull']

def makePlot():
  
  massToFileDict={}
  for i, expM in enumerate(options.expMasses):
    massToFileDict[float(expM)] = options.files[i]

  truth_mods=[]
  dummyFile = r.TFile.Open(options.files[0])
  for key in dummyFile.GetListOfKeys():
    name = key.GetName()
    truth = name.split('_mu')[0]
    if truth not in truth_mods: truth_mods.append(truth)
  dummyFile.Close()
  print truth_mods

  canv = r.TCanvas()

  siglines=[]
  sigboxes=[]
  for i, sig in enumerate(coverageValues):
    coverage = 1.-r.TMath.Prob(sig*sig,1)
    siglines.append(r.TLine(105,coverage,155,coverage))
    siglines[i].SetLineWidth(2)
    siglines[i].SetLineStyle(2)
    sigboxes.append(r.TPaveText(107,coverage+0.1,112,coverage))
    sigboxes[i].SetFillColor(0)
    sigboxes[i].SetLineColor(0)
    sigboxes[i].SetTextSize(0.04)
    sigboxes[i].AddText('%3.1f#sigma'%(sig))

  for truth in truth_mods:
    # coverage
    graphDict={}
    leg = r.TLegend(0.3,0.75,0.59,0.89)
    leg.SetFillColor(0)
    leg.SetLineColor(0)
    leg2 = r.TLegend(0.6,0.75,0.89,0.89)
    leg2.SetFillColor(0)
    leg2.SetLineColor(0)
    for ptype in plotTypes:
      graphDict[ptype] = {}
      if ptype=='Coverage':
        for c, stype in enumerate(scanTypes):
          graphDict[ptype][stype] = []
          for v, cov in enumerate(coverageValues):
            graphDict[ptype][stype].append(r.TGraphErrors())
            graphDict[ptype][stype][v].SetLineColor(graphCol[c])
            graphDict[ptype][stype][v].SetMarkerColor(graphCol[c])
            graphDict[ptype][stype][v].SetFillColor(graphCol[c])
            graphDict[ptype][stype][v].SetFillStyle(graphFil[c])
            graphDict[ptype][stype][v].GetXaxis().SetTitle("#m_{H}")
            graphDict[ptype][stype][v].GetYaxis().SetTitle("Coverage")
            graphDict[ptype][stype][v].SetTitle('Category %d - truth=%s'%(options.cat,truth))
          if c<len(scanTypes)/2:
            leg.AddEntry(graphDict[ptype][stype][0],label[c],"F")
          else:
            leg2.AddEntry(graphDict[ptype][stype][0],label[c],"F")
      else:
        for c, stype in enumerate(scanTypes):
          graphDict[ptype][stype] = r.TGraphErrors()
          graphDict[ptype][stype].SetLineColor(graphCol[c])
          graphDict[ptype][stype].SetMarkerColor(graphCol[c])
          graphDict[ptype][stype].SetFillColor(graphCol[c])
          graphDict[ptype][stype].SetFillStyle(graphFil[c])
          graphDict[ptype][stype].GetXaxis().SetTitle("#m_{H}")
          graphDict[ptype][stype].GetYaxis().SetTitle("Coverage")
          graphDict[ptype][stype].SetTitle('Category %d - truth=%s'%(options.cat,truth))
    
    mass_arr = massToFileDict.keys()
    mass_arr.sort()
    for p, mass in enumerate(mass_arr):
      f = r.TFile.Open(massToFileDict[mass])
      for c, stype in enumerate(scanTypes):
        hist = f.Get('%s_mu%s'%(truth,stype))
        graphDict['Bias'][stype].SetPoint(p,mass,hist.GetMean()/hist.GetRMS())
        graphDict['Bias'][stype].SetPointError(p,0,hist.GetMeanError()/hist.GetRMS())
        histPull = f.Get('%s_mu%sPull'%(truth,stype))
        graphDict['Pull'][stype].SetPoint(p,mass,histPull.GetMean())
        graphDict['Pull'][stype].SetPointError(p,0,histPull.GetMeanError())
        muBiasBand.SetPoint(p,mass-5,0)
        muBiasBand.SetPointError(p,masserr,0.2)
        muPullBand.SetPoint(p,mass-5,0)
        muPullBand.SetPointError(p,masserr,0.14)
        for v, cov in enumerate(coverageValues):
          graph = f.Get('%s_mu%sCov%3.1f'%(truth,stype,cov))
          x = r.Double(0.)
          y = r.Double(0.)
          graph.GetPoint(0,x,y)
          yerr = graph.GetErrorY(0)
          graphDict['Coverage'][stype][v].SetPoint(p,mass,y)
          graphDict['Coverage'][stype][v].SetPointError(p,masserr,yerr)
   
    muBiasBand.SetPoint(len(options.expMasses),155,0)
    muBiasBand.SetPointError(len(options.expMasses),masserr,0.2)
    muPullBand.SetPoint(len(options.expMasses),155,0)
    muPullBand.SetPointError(len(options.expMasses),masserr,0.14)

    dummyHist.GetYaxis().SetRangeUser(0.,1.3)
    dummyHist.SetTitle('Category %d - truth=%s'%(options.cat,truth))
    dummyHist.Draw()
    for sigline in siglines: sigline.Draw("same")
    for sigbox in sigboxes: sigbox.Draw("same")
    for c, stype in enumerate(scanTypes):
      for v, cov in enumerate(coverageValues):
        graphDict['Coverage'][stype][v].Draw("Psame")
    leg.Draw("same")
    leg2.Draw("same")
    canv.Print('%s/%s_coverage.pdf'%(options.outDir,truth))
    canv.Print('%s/%s_coverage.png'%(options.outDir,truth))
    
    dummyHist.GetYaxis().SetRangeUser(-0.5,0.5)
    dummyHist.GetYaxis().SetTitle("#mu bias (syst/stat)")
    dummyHist.Draw()
    muBiasBand.Draw("E3same")
    dummyHist.Draw("AXISsame")
    for c, stype in enumerate(scanTypes):
      graphDict['Bias'][stype].Draw("E3same")
    leg.Draw("same")
    leg2.Draw("same")
    canv.Print('%s/%s_bias.pdf'%(options.outDir,truth))
    canv.Print('%s/%s_bias.png'%(options.outDir,truth))
  
    dummyHist.GetYaxis().SetTitle("#mu pull (fit-gen)/err")
    dummyHist.Draw()
    muPullBand.Draw("E3same")
    dummyHist.Draw("AXISsame")
    for c, stype in enumerate(scanTypes):
      graphDict['Pull'][stype].Draw("E3same")
    leg.Draw("same")
    leg2.Draw("same")
    canv.Print('%s/%s_pull.pdf'%(options.outDir,truth))
    canv.Print('%s/%s_pull.png'%(options.outDir,truth))
  
if not options.datfile:
  makePlot()
else:
  f = open(options.datfile)
  for line in f.readlines():
    if line.startswith('#') or line.startswith('\n'): continue
    opts = line.split()
    options.cat = int(opts[0].split('=')[1])
    options.outDir = opts[1].split('=')[1]
    options.expMasses=[]
    options.files=[]
    for val in opts[2].split('=')[1].split(','):
      options.expMasses.append(float(val))
    for file in opts[3].split('=')[1].split(','):
      options.files.append(file)
    os.system('mkdir -p %s'%options.outDir)
    makePlot()


  

