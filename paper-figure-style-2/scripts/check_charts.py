"""Meaningful checks of statistics, missingness and emitted PDF objects."""
from pathlib import Path
import tempfile
import unittest

import numpy as np
import matplotlib.pyplot as plt
import pymupdf

from charts import wilson, grouped_bars, logistic_fit, rate_heatmap, radial_profile, failure_pie
from demo_data import repeated_tasks, recovery_counts
from style2 import theme, save_pdf, BLUE, TEAL
from verify_pdf import verify


class ChartChecks(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output=Path(self.tmp.name)/"figure.pdf"
        self.addCleanup(plt.close,"all")

    def test_wilson_known_values_boundaries_and_missing(self):
        p,lo,hi=wilson(np.array([0,5,10,0]),np.array([10,10,10,0]))
        np.testing.assert_allclose(lo[:3],[0,.23659309,.7224672],atol=1e-7)
        np.testing.assert_allclose(hi[:3],[.2775328,.76340691,1],atol=1e-7)
        self.assertTrue(np.isnan(p[3]))
        for k,n in (([-1],[5]),([6],[5]),([.5],[1]),([1],[float('nan')])):
            with self.assertRaises(ValueError): wilson(k,n)

    def test_logistic_fit_recovers_known_binomial_curve(self):
        x=np.arange(1.,6.)
        n=np.array([1000]*5)
        k=np.rint(n/(1+np.exp(-(2.8-.9*x))))
        b=logistic_fit(x,k,n,ridge=.0001)
        np.testing.assert_allclose(b,[2.8,-.9],atol=.015)
        # Empty levels must have no influence on the fit.
        b2=logistic_fit(np.r_[x,1000],np.r_[k,0],np.r_[n,0],ridge=.0001)
        np.testing.assert_allclose(b,b2,atol=1e-9)
        with self.assertRaises(ValueError): logistic_fit([1,1],[0,1],[1,1])

    def test_recovery_marginals_derive_from_same_tasks(self):
        one,two,total,hits,ns=recovery_counts()
        np.testing.assert_array_equal(total,ns.sum(axis=1))
        np.testing.assert_array_equal(one+two,hits.sum(axis=1))
        _,scores,demands=repeated_tasks()
        high=(scores>=.8).sum(axis=1)
        for c in range(6):
            self.assertEqual(one[c],np.sum((demands[:,c]>0)&(high==1)))
            self.assertEqual(two[c],np.sum((demands[:,c]>0)&(high==2)))
        from plots import recovery_analysis
        with self.assertRaises(ValueError):
            recovery_analysis(self.output,counts=(one+1,two,total,hits,ns))

    def test_missing_bars_do_not_become_zero_and_sparse_is_translucent(self):
        with theme():
            fig,ax=plt.subplots()
            artists=grouped_bars(ax,[[0,50,np.nan]],["Zero","Measured","Missing"],["A"],[BLUE],counts=[[50,3,0]])
            self.assertEqual(len(artists),2)
            self.assertEqual(artists[0].get_height(),0)
            self.assertEqual(artists[0].get_alpha(),1)
            self.assertLess(artists[1].get_alpha(),.5)
            self.assertEqual(ax.get_ylim()[0],0)
            self.assertTrue(any(t.get_text()=="–" for t in ax.texts))
            with self.assertRaises(ValueError): grouped_bars(ax,[[50]],["X"],["A"],[BLUE],intervals=([[60]],[[70]]))

    def test_sector_geometry_and_pie_normalization(self):
        with theme():
            fig,ax=plt.subplots()
            wedges=radial_profile(ax,[1,2,3,4,5,0],list("ABCDEF"),BLUE,"Profile")
            self.assertEqual(len(wedges),15)
            self.assertAlmostEqual(max(w.r for w in wedges),1.)
            with self.assertRaises(ValueError): radial_profile(ax,[1,6,2],list("ABC"),BLUE,"Bad")
            plt.close(fig)
            fig,ax=plt.subplots()
            wedges=failure_pie(ax,[1,3],["A","B"],[BLUE,TEAL],title="Counts")
            self.assertAlmostEqual(abs(wedges[0].theta2-wedges[0].theta1),90)
            with self.assertRaises(ValueError): failure_pie(ax,[0,0],["A","B"],[BLUE,TEAL],title="Empty")
        from plots import failure_distributions
        with self.assertRaises(ValueError): failure_distributions(self.output,counts=[[1]*10,[1]*10])

    def test_heatmap_pdf_has_text_no_bitmaps_and_correct_missing_cell(self):
        with theme():
            fig,ax=plt.subplots(figsize=(7,3))
            fig.subplots_adjust(left=.14,bottom=.27,top=.88)
            rate_heatmap(ax,[[0,0,2],[4,1,3]],[[10,0,4],[5,2,6]],["Search","Tools"],[1,2,3])
            fig.text(.1,.94,"Selectable demand heatmap with explicit missing tasks",fontsize=9)
            save_pdf(fig,self.output,title="Test heatmap")
        result=verify(self.output,expected=("Search","50.0%†","Selectable demand"))
        self.assertTrue(result["ok"],result["problems"])
        with pymupdf.open(self.output) as doc:
            self.assertIn("–",doc[0].get_text())
            self.assertEqual(len(doc[0].get_images()),0)
            self.assertGreater(len(doc[0].get_drawings()),6)

    def test_pdf_width_scales_geometry_and_text(self):
        with theme():
            fig,ax=plt.subplots(figsize=(11,4))
            ax.set_axis_off()
            ax.text(.1,.5,"A scalable vector figure with an embedded selectable font and a visible label.",fontsize=10)
            save_pdf(fig,self.output,title="Resize",width_in=5.5)
        with pymupdf.open(self.output) as doc:
            self.assertAlmostEqual(doc[0].rect.width,396)
            spans=[s for b in doc[0].get_text("dict")["blocks"] for l in b.get("lines",[]) for s in l["spans"]]
            self.assertAlmostEqual(spans[0]["size"],5)


if __name__=="__main__": unittest.main(verbosity=2)
