import DTCurrent
import ROOT

# read file
data = DTCurrent.DTCurrent('augustfills/2984/WM2_MB1_S10.txt')

# drawing elements
canvas = ROOT.TCanvas("c1", "c1", 200, 10, 600, 400)
canvas.SetGrid()
mg = ROOT.TMultiGraph()
leg = ROOT.TLegend(0.1, 0.5, 0.3, 0.9)

# plot series
colors = [2,3,4]
graphs = []
for superlayer in [1,2,3]:
	# data points
	graphs.append(ROOT.TGraph(len(data.luminosity), data.luminosity, data.get(superlayer=superlayer)))
	graphs[-1].SetMarkerColor(colors[superlayer-1])
	graphs[-1].SetMarkerSize(1)
	graphs[-1].SetMarkerStyle(21)
	graphs[-1].SetLineColor(0)
	mg.Add(graphs[-1])
	leg.AddEntry(graphs[-1], 'SL'+str(superlayer)+'w', "p")

	# fitted line
	graphs.append(ROOT.TGraph(len(data.luminosity), data.luminosity, data.get(superlayer=superlayer, fit=1)))
	graphs[-1].SetLineColor(colors[superlayer-1])
	graphs[-1].SetLineWidth(1)
	graphs[-1].SetLineStyle(2)
	graphs[-1].SetMarkerSize(0)
	mg.Add(graphs[-1])
	leg.AddEntry(graphs[-1], 'SL'+str(superlayer)+'w fit', "l")
mg.Draw("AL*")
leg.Draw()

# plot labels
mg.SetTitle('Average Wire Current vs Luminosity Fits for {chamber} Fill {fill}'.format(chamber=data.chamber, fill=data.fill))
mg.GetXaxis().SetTitle('Instantaneous \; Luminosity \; (\mu barn^{-1} \cdot s^{-1})')
mg.GetYaxis().SetTitle('Current \; (\mu A)')
mg.SetMinimum(0)
mg.GetXaxis().SetLimits(0., 8000.)

canvas.Update()

input("Press Enter to continue...")
