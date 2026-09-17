"""Check quantitative invariants and the emitted PDF, without reference images."""
from pathlib import Path
import tempfile
import unittest

import pymupdf
from style1 import Figure
from charts import Axes, Scale, pareto_frontier, nested_donut, bar_matrix
from demo_data import METHODS, budget_curve
from verify_pdf import verify


class ChartChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output=Path(self.temp.name)/"check.pdf"

    def figure(self):
        return Figure(self.output,280)

    def test_linear_and_log_distance(self):
        self.assertAlmostEqual(Scale(0,80,40,680)(40),360)
        scale=Scale(.1,100,10,310,log=True)
        self.assertAlmostEqual(scale(1)-scale(.1),scale(10)-scale(1))
        self.assertAlmostEqual(scale(10)-scale(1),scale(100)-scale(10))
        self.assertEqual(Scale(0,100,220,20)(25),170)

    def test_no_silent_out_of_range_or_nonfinite_data(self):
        for value in (-1,101,float("nan"),float("inf")):
            with self.assertRaises(ValueError):
                Scale(0,100,0,200)(value)
        with self.assertRaises(ValueError):
            Scale(0,100,0,200,log=True)

    def test_pareto_dominance_and_ties(self):
        # Equal costs, scores, and duplicate optimal points need distinct handling.
        cost=[3,1,1,2,4,3]
        score=[5,2,3,3,4,5]
        self.assertEqual(pareto_frontier(cost,score),[2,0,5])
        with self.assertRaises(ValueError):
            pareto_frontier([1,2],[3])

    def test_bar_baselines_and_invalid_bounds(self):
        f=self.figure()
        a=Axes(f,50,50,300,140,(0,5),(0,100))
        with self.assertRaises(ValueError):
            a.bar(1,50,interval=(60,70))
        with self.assertRaises(ValueError):
            a.band([0,1],[20,10],[10,30])
        with self.assertRaises(ValueError):
            a.series([0,1,1],[0,30,40])
        with self.assertRaises(ValueError):
            Axes(f,50,50,300,140,(0,5),(10,100)).bar(1,50)
        with self.assertRaises(ValueError):
            Axes(f,50,50,300,140,(1,10),(0,5),logx=True).hbar(1,5)

    def test_matrix_row_alignment_and_donut_values(self):
        f=self.figure()
        with self.assertRaises(ValueError):
            bar_matrix(f,10,50,680,["A","B"],[dict(title=["Score"],maximum=100,values=[5])],["#000000"]*2)
        with self.assertRaises(ValueError):
            nested_donut(f,150,150,[dict(color="#FFFFFF",children=[dict(label="A",value=0,color="#AAAAAA")])])
        total,segments=nested_donut(f,150,150,[dict(color="#FFFFFF",children=[
            dict(label="A",value=1,color="#AAAAAA"),dict(label="B",value=3,color="#BBBBBB")])])
        self.assertEqual(total,4)
        self.assertEqual(sum(s["value"] for s in segments),total)

    def test_pdf_text_vector_geometry_and_real_opacity(self):
        f=self.figure()
        f.background()
        f.header("Quantitative PDF validation")
        f.text(35,190,"Selectable axis label",angle=90,size=10)
        f.text(100,240,"Native vector paths, embedded fonts and Unicode text remain searchable.",size=10)
        # One half-transparent black box over a white region must render gray.
        f.box(90,75,100,100,fill="#FFFFFF",stroke=None,radius=0)
        f.box(90,75,100,100,fill="#000000",stroke=None,radius=0,alpha=.5)
        f.save()
        result=verify(self.output,expected=["Selectable axis label"])
        self.assertTrue(result["ok"],result["problems"])
        with pymupdf.open(self.output) as doc:
            pix=doc[0].get_pixmap(matrix=pymupdf.Matrix(1/f.scale,1/f.scale),alpha=False)
            rgb=pix.pixel(140,125)
            self.assertTrue(all(120<=c<=135 for c in rgb),rgb)

    def test_demo_curves_match_leaderboard_and_are_cumulative(self):
        for m in METHODS:
            x,y,low,high=budget_curve(m)
            self.assertEqual((x[0],x[-1]),(0,60))
            self.assertEqual(y[-1],m["score"])
            self.assertTrue(all(a<=b for a,b in zip(y,y[1:])))
            self.assertTrue(all(a<=b<=c for a,b,c in zip(low,y,high)))

    def test_domain_shares_are_feasible_counts(self):
        from examples.domain_specialization import domain_results
        results,marginal=domain_results()
        self.assertEqual(marginal[0],0)
        self.assertTrue(all(0<=value<=8 for value in marginal))
        for _,n,scores in results:
            for score in scores:
                count=n*score/100
                self.assertAlmostEqual(count,round(count))

    def test_logo_exception_preserves_image_checks(self):
        from PIL import Image
        from reportlab.lib.utils import ImageReader
        from model_logos import draw_model_logo, logo_path
        for case in ("approved","oversized","unknown","removed-alpha"):
            f=self.figure()
            f.background()
            f.header("Model logo validation")
            f.text(100,220,"Model identity remains a small asset; chart labels remain selectable text.",size=10)
            if case=="approved":
                draw_model_logo(f,"openai",140,125,size=18)
            elif case=="oversized":
                f.c.drawImage(str(logo_path("openai")),90,75,width=100,height=100,mask="auto")
            elif case=="unknown":
                f.c.drawImage(ImageReader(Image.new("RGB",(8,8),"red")),100,100,width=18,height=18)
            else:
                with Image.open(logo_path("openai")) as source:
                    f.c.drawImage(ImageReader(source.convert("RGB")),100,100,width=18,height=18)
            f.save()
            result=verify(self.output)
            self.assertEqual(result["ok"],case=="approved",(case,result["problems"]))
            if case=="approved":
                self.assertEqual(result["pages"][0]["model_logos"][0]["provider"],"openai")
                self.assertFalse(verify(self.output,strict_vector=True)["ok"])


if __name__=="__main__":
    unittest.main(verbosity=2)
