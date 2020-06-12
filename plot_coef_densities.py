#!/usr/bin/env python
""" Script to create comparative density plots for each coefficient and
    land cover class in a Glance formatted training dataset"""

import numpy as np
import pandas as pd
import warnings
import click
import seaborn as sns
import matplotlib.pyplot as plt

@click.command(short_help='Plot coefficient densities per training class')
@click.argument('csv', metavar='<training data>', nargs=1,
                type=click.Path(exists=True, resolve_path=True))
@click.argument('band_list', metavar='<band list>', nargs=1, type=click.STRING)
@click.argument('coef_list', metavar='<coefficient list>', nargs=1, type=click.STRING)
def plot_densities(csv, band_list, coef_list):
    df = pd.read_csv(csv)   
   
    # I think these are stable now so we can hardcode them (for now)
    class_dict = {
            0: 'NoLabel',
            1: 'Water',
            2: 'Snow/Ice',
            3: 'Built',
            4: 'Bare',
            5: 'Trees',
            6: 'Shrub',
            7: 'Herbaceous',
            8: 'Woodland'
        }

    df = df.replace({'Glance_Class_ID_level1': class_dict})
    df = getCoords(df)
    df = df.query('Glance_Class_ID_level1 != "NoLabel"')#.query('Glance_Class_ID_level1 != "Woodland"')
    
    # Calculate xlim automatically based on percentiles?
    pal = ['black','#33a02c','red','#ffff99','#b2df8a','grey','#386cb0', 'brown']
    # Build property names based on band and coef lists
    bands = band_list.split()
    coefs = coef_list.split()
    property_list = [i + '_' + j for i in bands for j in coefs]  
    for p in property_list:
        click.echo('Saving figure for coefficient {}'.format(p))
        doRidge(df, pal, p)



def doRidge(df, pal, coef):
    sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
    warnings.filterwarnings('ignore')
    
    # Try defining xlim automatically
    stats = df[coef].describe()
    xlim = []
    xlim.append(df[coef].min() - stats['std']*2)
    xlim.append(df[coef].max() + stats['std']*2) 

    g = sns.FacetGrid(df, row="Glance_Class_ID_level1", hue="Glance_Class_ID_level1", 
                      aspect=10, height=.5, palette=pal, xlim=xlim)

    # Draw the densities in a few steps
    g.map(sns.kdeplot, coef, clip_on=True, shade=True, alpha=1, lw=1.5, bw=.05)
    g.map(sns.kdeplot, coef, clip_on=True, color="black", lw=2, bw=.05)
    g.map(plt.axhline, y=0, lw=.5, clip_on=False)


    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
        ax.set_xlim(xlim)
        ax.text(0, .2, label, fontweight="bold", color='k', fontsize=10,
                ha="left", va="center", transform=ax.transAxes)


    g.map(label, coef)

    # Set the subplots to overlap
    g.fig.subplots_adjust(hspace=-.1)

    # Remove axes details that don't play well with overlap
    g.set_titles("")
    g.set(yticks=[])
    g.despine(bottom=True, left=True)
    outname = 'RidgePlot_' + coef + '.png'
    g.savefig(outname, dpi=300)
#    plt.tight_layout()
    plt.clf()
    plt.close()

def getCoords(df):
    lats = []
    longs = []
    for index, row in df.iterrows():
        coords = row['.geo'].split('coordinates":')[1].split('[')[1].split(']')[0].split(',')
        longs.append(float(coords[0]))
        lats.append(float(coords[1]))

    df['Longitude'] = longs
    df['Latitude'] = lats
    return df

if __name__ == '__main__':
   plot_densities()
