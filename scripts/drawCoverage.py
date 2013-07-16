#!/usr/bin/env python

import sys
import os

from optparse import OptionParser
parser=OptionParser()
parser.add_option("-c","--cat",default=0)
parser.add_option("-s","--expSignals",default=[],action="append")
parser.add_option("-f","--files",default=[],action="append")
parser.add_option("-D","--outDir")
parser.add_option("-d","--datfile")
(options,args)=parser.parse_args()

coverageValues=[0.1,0.5,1.,2.]
muerr = 0.25

os.system('mkdir -p %s'%options.outDir)

import ROOT as r
r.gROOT.SetBatch()

dummyHist = r.TH1F('dummy','',7,-1.75,1.75)
dummyHist.GetXaxis().SetTitle("#mu_{gen}")
dummyHist.GetYaxis().SetTitle("Coverage")
dummyHist.SetStats(0)

scanTypes=['Fab','Paul','Chi2','AIC']
graphCol=[r.kBlue,r.kRed,r.kGreen+1,r.kMagenta]
label=['Hgg Nominal Pol','Envelope (no pen)','Envelope (1/dof pen)','Envelope (2/dof pen)']

def makePlot():
  
  muToFileDict={}
  for i, expS in enumerate(options.expSignals):
    muToFileDict[float(expS)] = options.files[i]

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
    siglines.append(r.TLine(-1.75,coverage,1.75,coverage))
    siglines[i].SetLineWidth(2)
    siglines[i].SetLineStyle(2)
    sigboxes.append(r.TPaveText(-1.6,coverage+0.1,-1.25,coverage))
    sigboxes[i].SetFillColor(0)
    sigboxes[i].SetLineColor(0)
    sigboxes[i].SetTextSize(0.04)
    sigboxes[i].AddText('%3.1f#sigma'%(sig))

  for truth in truth_mods:
    graphDict={}
    leg = r.TLegend(0.3,0.75,0.59,0.89)
    leg.SetFillColor(0)
    leg.SetLineColor(0)
    leg2 = r.TLegend(0.6,0.75,0.89,0.89)
    leg2.SetFillColor(0)
    leg2.SetLineColor(0)
    for c, stype in enumerate(scanTypes):
      graphDict[stype] = []
      for v, cov in enumerate(coverageValues):
        graphDict[stype].append(r.TGraphErrors())
        graphDict[stype][v].SetLineColor(graphCol[c])
        graphDict[stype][v].SetMarkerColor(graphCol[c])
        #graphDict[stype][v].SetLineWidth(2)
        #graphDict[stype][v].SetMarkerStyle(r.kPlus)
        graphDict[stype][v].GetXaxis().SetTitle("#mu_{gen}")
        graphDict[stype][v].GetYaxis().SetTitle("Coverage")
        graphDict[stype][v].SetTitle('Category %d - truth=%s'%(options.cat,truth))
      if c<len(scanTypes)/2:
        leg.AddEntry(graphDict[stype][0],label[c],"L")
      else:
        leg2.AddEntry(graphDict[stype][0],label[c],"L")
    for p, mu in enumerate(muToFileDict.keys()):
      f = r.TFile.Open(muToFileDict[mu])
      for c, stype in enumerate(scanTypes):
        for v, cov in enumerate(coverageValues):
          graph = f.Get('%s_mu%sCov%3.1f'%(truth,stype,cov))
          x = r.Double(0.)
          y = r.Double(0.)
          graph.GetPoint(0,x,y)
          yerr = graph.GetErrorY(0)
          graphDict[stype][v].SetPoint(p,mu,y)
          graphDict[stype][v].SetPointError(p,muerr,yerr)
   
    dummyHist.GetYaxis().SetRangeUser(0.,1.3)
    dummyHist.SetTitle('Category %d - truth=%s'%(options.cat,truth))
    dummyHist.Draw()
    for sigline in siglines: sigline.Draw("same")
    for sigbox in sigboxes: sigbox.Draw("same")
    for c, stype in enumerate(scanTypes):
      for v, cov in enumerate(coverageValues):
        graphDict[stype][v].Draw("Psame")
    leg.Draw("same")
    leg2.Draw("same")
    canv.Print('%s/%s_coverage.pdf'%(options.outDir,truth))
    canv.Print('%s/%s_coverage.png'%(options.outDir,truth))
  
if not options.datfile:
  makePlot()
else:
  f = open(options.datfile)
  for line in f.readlines():
    if line.startswith('#') or line.startswith('\n'): continue
    opts = line.split()
    options.cat = int(opts[0].split('=')[1])
    options.outDir = opts[1].split('=')[1]
    options.expSignals=[]
    options.files=[]
    for val in opts[2].split('=')[1].split(','):
      options.expSignals.append(float(val))
    for file in opts[3].split('=')[1].split(','):
      options.files.append(file)
    os.system('mkdir -p %s'%options.outDir)
    makePlot()


  
