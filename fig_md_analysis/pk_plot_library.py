def imports():
	import pickle as pkl
	import seaborn as sns
	import matplotlib.pyplot as plt
	plt.rcParams['mathtext.fontset'] = 'dejavuserif'
	plt.rcParams['font.family'] = 'serif'
	return

def rgba(color, alpha):
	import matplotlib as mpl
	col = mpl.colors.to_rgba(color, alpha)
	return col
def wnum(comov = True):
	if comov:
		unit = 'cMpc/h'
	else:
		unit = 'Mpc/h'
	return "$k$ (%s)$^{-1}$"%unit

def pklab(name1, name2 = '', fn = 'k', rm = True, comov = True):
	if rm:
		name1 = '\\mathrm{%s}'%name1
		if not name2 == '':
			name2 = '\\mathrm{%s}'%name2
	if not name2 == '':
		name = name1 + '\\times' + name2
	else:
		name = name1
	
	if comov:
		unit = 'cMpc/h'
	else:
		unit = 'Mpc/h'
	return "P$_{%s}$ $(%s)$ (%s)$^{3}$"%(name, fn, unit)
def pkrat(name1, name2, fn = 'k', rm = True):
    if rm:
        name1 = '\\mathrm{%s}'%name1
        name2 = '\\mathrm{%s}'%name2
    
    return "P$_{%s}$ $(%s)$ / P$_{%s}$ $(%s)$"%(name1, fn, name2, fn)

def ccrat(name1, name2, fn = 'k', rm = True, frac = False):
    if rm:
        name1 = '\\mathrm{%s}'%name1
        name2 = '\\mathrm{%s}'%name2
    
    out = 'r$_{%s}$ $(%s)$ / r$_{%s}$ $(%s)$'%(name1, fn, name2, fn)
    if frac:
        out = '$\\frac{r_{%s} (%s)}{r_{%s} (%s)}$'%(name1, fn, name2, fn)
    return out

def obsbiaslab(name1, name2, fn = 'k', rm = True):
    if rm:
        name1 = '\\mathrm{%s}'%name1
        name2 = '\\mathrm{%s}'%name2
    
    out = '$\\mathrm{b}_{%s-%s} (%s) = \\sqrt{\\frac{\\mathrm{P}_{%s} (%s)}{\\mathrm{P}_{%s} (%s)}}$'%(name1, name2,fn, name1, fn, name2, fn)
    return out

def thbiaslab(name1, name2, fn = 'k', rm = True):
	if rm:
		name1 = '\\mathrm{%s}'%name1
		name2 = '\\mathrm{%s}'%name2
	out = '$\\mathrm{b}_{%s-%s} (%s) = \\frac{\\mathrm{P}_{%s \\times %s} (%s)}{\\mathrm{P}_{%s} (%s)}$'%(name1, name2, fn, name1, name2, fn, name2, fn)
	return out
def cclab(name1, name2, fn = 'k', rm = True):
    if rm:
        name1 = '\\mathrm{%s}'%name1
        name2 = '\\mathrm{%s}'%name2
    
    numerator = '\\mathrm{P}_{%s \\times %s}(%s)'%(name1, name2, fn)
    denom = '\\mathrm{P}_{%s}(%s) \\mathrm{P}_{%s}(%s)'%(name1, fn, name2, fn)
    CORRCOEF = 'r $(%s)$ = $\\frac{%s}{\\sqrt{%s}}$'%(fn, numerator, denom)
    return CORRCOEF

def darkmode(fg):
	fg.axisLabelArgs('both', color = 'white')
	fg.colLabelArgs(color = 'white')
	fg.rowLabelArgs(color = 'white')
	fg.spineArgs(edgecolor = 'white')
	fg.figArgs(facecolor = 'black')
	fg.axisArgs(facecolor = 'black')
	fg.tickArgs(color = 'white', labelcolor = 'white')
	fg.legendArgs(labelcolor = 'white')

	return