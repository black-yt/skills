"""示例需求：给模型家族评测柱状图加入对应 logo，保留渐变、误差线、独立文字和可替换的数据。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example
from charts import Axes, footer
from model_logos import MODEL_LOGOS, draw_model_logo


# Model-family identifiers are real; ALL values and intervals are invented solely
# to demonstrate layout. The ordering is not a claim about model performance.
ROWS = [
    dict(provider="anthropic",value=74.2,low=72.1,high=76.3),
    dict(provider="openai",value=68.8,low=66.4,high=71.2),
    dict(provider="gemini",value=64.9,low=62.0,high=67.8),
    dict(provider="deepseek",value=59.4,low=56.8,high=62.0),
    dict(provider="qwen",value=54.2,low=51.1,high=57.3),
    dict(provider="glm",value=48.1,low=45.8,high=50.4),
    dict(provider="kimi",value=41.3,low=38.5,high=44.1),
    dict(provider="grok",value=36.8,low=34.6,high=39.0),
    dict(provider="mimo",value=30.7,low=28.2,high=33.2),
    dict(provider="minimax",value=23.5,low=21.4,high=25.6),
]


def draw(output, *, rows=None, **options):
    """Logo-aware bars; custom rows need provider/value/low/high, optional label."""
    rows=ROWS if rows is None else list(rows)
    if not rows:
        raise ValueError("Provide at least one model row")
    f=Figure(output,349,title="Model evaluation with recognizable identities",**options)
    f.background()
    f.header("Model evaluation with recognizable identities")
    f.text(16,54,"Model families · illustrative scores and ordering",size=10,color=P.muted)
    axis=Axes(f,53,78,647,166,(-.6,len(rows)-.4),(0,80))
    axis.frame(yticks=(0,20,40,60,80),ylabel="Task success (%)",size=9)
    for i,row in enumerate(rows):
        spec=MODEL_LOGOS[row["provider"]]
        axis.bar(i,row["value"],color=spec["color"],interval=(row["low"],row["high"]))
        f.text(axis.sx(i),axis.sy(row["high"])-6,f"{row['value']:.1f}",size=11,align="center")
        draw_model_logo(f,row["provider"],axis.sx(i),264,size=18)
        label=row.get("label",spec["label"])
        f.lines(axis.sx(i),291,label.split("\n"),size=10.5,align="center",leading=13,
                max_width=647/(len(rows)+.2)-3)
    footer(f,detail="Error bars: illustrative bounds")
    return f.save()


if __name__=="__main__":
    run_example(draw,"model_leaderboard")
