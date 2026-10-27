"""Four native draw.io examples, with public paper labels and transcribed data."""
import json
import math
from pathlib import Path
from drawio import Diagram, INK
from components import (GREEN, TEAL, YELLOW, MINT, brain, buffer, card,
                        cube, document, native_icon, network, phase, snowflake, yarn)


def title(d,name,x,y,w,text,size=25,color=INK):
    return d.text(name,x,y,w,38,text,size=size,bold=True,italic=True,color=color)


def figure1():
    d=Diagram("Figure 1 · Complementary learning",1440,510)
    d.polygon("fast-field",[(199,10),(1237,10),(1341,255),(98,255)],fill="#F0A5A7",stroke="none",sketch=False,
              gradientColor="#CFB2C4",gradientDirection="south")
    d.polygon("slow-field",[(98,255),(1341,255),(1237,489),(199,489)],fill="#CFB2C4",stroke="none",sketch=False,
              gradientColor="#ACC6EB",gradientDirection="south")
    d.line("human-model-divider",[(712,10),(712,489)],color="#36313A",sw=2.5)
    d.line("fast-slow-divider",[(195,255),(1245,255)],color="#36313A",sw=1.7,dashed=True)
    title(d,"fast-heading",208,14,486,"Fast hippocampus")
    title(d,"day-heading",742,14,477,"Daytime Scaling")
    title(d,"slow-heading",290,451,400,"Slow neocortex")
    title(d,"night-heading",789,451,430,"Nighttime Scaling")

    d.shape("human-emblem",10,169,169,169,kind="ellipse",fill="#E3E5F3",gradientColor="#F1BFCB",stroke=INK,sw=2.3,sketch=False)
    brain(d,"human-brain",40,189,108)
    d.text("human-label",5,348,180,82,"Human\nBrain",size=27,bold=True)
    phase(d,"latent-evolve-emblem",1260,169,169)
    d.text("latent-evolve-label",1253,348,184,82,"Latent\nEvolve",size=27,bold=True)

    d.shape("memory-cloud",190,70,208,88,kind="cloud",fill="#D3DF9A",stroke="#597647",sw=1.8)
    native_icon(d,"tree-file-icon","tabler-file-code",230,83,37,color="#2B657B",sw=1.7)
    native_icon(d,"data-file-icon","tabler-chart-bar",310,83,37,color="#3C7283",sw=1.7)
    d.text("tree-file-label",211,121,75,26,"tree.py",size=13,bold=True)
    d.text("data-file-label",284,118,103,36,"data science\nhandbook",size=12.5,bold=True)
    d.text("fast-note",418,74,274,54,"Superficial, fast recall of\nmemory clues",size=15)
    document(d,"new-task-human",207,180,113,61,"Write a\nkaggle code",size=14)
    brain(d,"fast-brain",400,143,82)
    card(d,"recalled-code",500,143,187,94,"- use tree search\n  func(x_node, 1)\n- analyze data ...",fill="#3F999C",stroke="#294A56",size=14,bold=False)
    d.root.find("mxCell[@id='recalled-code-label']").set("style",d.root.find("mxCell[@id='recalled-code-label']").get("style")+"fontColor=#FFFFFF;")
    d.edge("human-task-recall","new-task-human","fast-brain",points=[(357,223),(383,207)],curved=True,color="#66716E",sw=2.4)
    d.edge("human-recall-output","fast-brain","recalled-code",color="#35566D",sw=2)

    d.shape("old-human-tasks",197,274,162,172,fill="#C4C7BD",stroke="none",sketch=False)
    for name,y,text,h in (("kaggle",282,"kaggle coding",44),("numpy",336,"use numpy for\nstatistic course",46),("pandas",398,"use pandas\nfor homework",43)):
        document(d,"human-skill-"+name,207,y,140,h,text,size=13)
    d.text("human-task-ellipsis",215,380,130,18,"... ...",size=13)
    brain(d,"slow-brain",404,344,86)
    d.text("slow-note",485,276,207,60,"Silent, long-term\nconsolidation of seen tasks\nand skills",size=14)
    buffer(d,"consolidated-skills",518,349,173,95,"",fill="#D6E396",edge="#708B4D",top="#E6EDB0")
    native_icon(d,"skill-code-icon","tabler-file-code",529,375,29,color="#3C7189",sw=1.6)
    d.text("skill-notebook-label",558,375,127,46,"coding +\ndata analysis",size=14,bold=True)
    for name,entry in (("kaggle",.2),("numpy",.5),("pandas",.8)):
        d.edge("human-consolidate-"+name,"human-skill-"+name,"slow-brain",entry=(0,entry),sw=1.8)
    d.edge("human-store-skill","slow-brain","consolidated-skills",exit=(1,.7),entry=(0,.6),color="#6B7B83",sw=2)

    document(d,"day-task",751,68,112,63,"Write a\nkaggle code",size=14)
    card(d,"day-llm",740,151,123,85,"LLM\nBackbone",fill="#D4E5CA",size=17)
    snowflake(d,"day-frozen",838,140,37)
    d.shape("episodic-cache",892,65,323,93,fill="#C5C6C7",stroke="none",sketch=False)
    d.text("cache-title",899,65,310,27,"Episodic Buffer M",size=15,bold=True)
    for i,(x,fill) in enumerate(((904,YELLOW),(952,"#B9D9A8"),(1000,"#92CFCA"),(1048,"#60B7BC"),(1123,"#9DD3AF"),(1170,"#6AAAC2"))):
        cube(d,"cached-latent-"+str(i),x,100,39,34,fill=fill)
    d.text("cache-ellipsis",1087,103,30,20,"...",size=16)
    d.text("retrieval-label",1082,157,160,27,"Fast Retrieval",size=14,italic=True)
    card(d,"day-recalled-code",879,182,344,57,"- recall previous Kaggle solutions\n- fast adaptation to the codes ...",fill="#3F999C",stroke="#294A56",size=13.5,bold=False)
    node=d.root.find("mxCell[@id='day-recalled-code-label']")
    node.set("style",node.get("style")+"fontColor=#FFFFFF;")
    d.edge("day-task-input","day-task","day-llm",exit=(.5,1),entry=(.5,0),color="#5C7259",sw=1.8)
    d.edge("retrieve-near-history","episodic-cache","day-llm",exit=(.30,1),entry=(1,.22),points=[(949,171),(889,172)],curved=True,sw=1.6)
    d.edge("retrieve-far-history","episodic-cache","day-llm",exit=(.78,1),entry=(1,.32),points=[(1080,181),(907,182)],curved=True,sw=1.6)
    d.edge("day-produce-code","day-llm","day-recalled-code",exit=(1,.7),entry=(0,.5),sw=1.9)

    d.shape("night-experience-panel",733,274,490,172,fill="#C7C4CF",stroke="none",sketch=False)
    for name,y,text,h in (("kaggle",281,"Write a\nkaggle code",47),("leetcode",337,"leetcode task",36),("numpy",396,"use numpy for\nstatistic course",45)):
        document(d,"night-task-"+name,744,y,137,h,text,size=12.7)
    d.text("night-task-ellipsis",752,373,120,21,"... ...",size=13)
    card(d,"night-llm",929,282,110,58,"LLM\nBackbone",fill="#D4E5CA",size=15)
    snowflake(d,"night-frozen",1016,271,34)
    d.text("consolidation-note",1055,280,160,69,"Consolidate\nknowledge and\nexperiences",size=14)
    card(d,"night-weaver",931,367,126,78,"Latent\nWeaver",fill="#F1BCC9",stroke="#A86575",size=16)
    yarn(d,"night-yarn",974,353,34)
    d.text("generate-label",1056,365,171,28,"Learn to generate",size=14,italic=True,color="#7E4853")
    cube(d,"learned-latent-a",1092,399,52,40,fill=MINT)
    cube(d,"learned-latent-b",1170,399,49,40,fill="#A8CEC5")
    for name,entry in (("kaggle",.18),("leetcode",.48),("numpy",.78)):
        d.edge("night-experience-"+name,"night-task-"+name,"night-weaver",entry=(0,entry),points=[(904,374)],curved=True,sw=1.7)
    d.edge("night-backbone-to-weaver","night-llm","night-weaver",exit=(.36,1),entry=(.36,0),sw=1.8)
    d.edge("night-weaver-to-backbone","night-weaver","night-llm",exit=(.72,0),entry=(.72,1),sw=1.8)
    d.edge("night-output-prior","night-weaver","learned-latent-a",sw=2)
    return d


def figure2():
    d=Diagram("Figure 2 · LatentEvolve architecture",1440,830)
    d.shape("day-field",0,0,1002,830,fill="#FFF9E9",stroke="none",sketch=False)
    d.shape("night-field",1002,0,438,830,fill="#ECF3FC",stroke="none",sketch=False)
    title(d,"day-title",22,10,455,"Daytime Scaling",size=32,color="#95571D")
    title(d,"night-title",1018,10,406,"Nighttime Scaling",size=30,color="#245D88")
    card(d,"task",112,77,856,82,"",fill="#F7F7F4",stroke="#707371")
    d.text("task-prefix",124,85,145,32,"Task cᵢ",size=24,bold=True,align="left")
    d.shape("task-query",270,92,29,29,kind="ellipse",fill="#F4C9CE",stroke="#95585A",sw=1.8)
    d.text("task-sentence-a",309,86,647,34,": Write a data analysis code for this",size=18,family="DejaVu Sans Mono",align="left")
    d.text("task-sentence-b",124,123,830,27,"Excel file and visualize the geometric data",size=18,family="DejaVu Sans Mono",align="left")

    card(d,"backbone",25,229,219,246,"LLM\nBackbone\n\n(frozen)",fill="#D4E7CE",size=28)
    snowflake(d,"backbone-frozen",1,203,70)
    card(d,"decoded-sequence",259,229,640,103,"",fill=TEAL,stroke="#5F8580")
    d.text("decoding-label",273,187,360,34,"Standard decoding",size=22,italic=True)
    positions=[(285,"z₁"),(339,"z₂"),(393,"z₃"),(447,"z₄"),(501,"z₅"),(555,"z₆"),(702,"z₈₀"),(756,"z₈₁"),(810,"z₈₂"),(864,"z₈₃")]
    for i,(x,word) in enumerate(positions):
        d.text("token-label-"+str(i),x-4,242,44,24,word,size=18,italic=True)
        d.shape("token-"+str(i),x,275,38,42,fill="#D9E8F4",stroke="#537690",sw=1.6,rounded=1,arcSize=5)
    d.text("sequence-ellipsis",615,275,68,37,"... ...",size=20)
    d.line("truncation-bracket",[(276,325),(276,342),(594,342),(594,325)],sw=1.7)
    d.text("truncate-label",281,342,190,29,"Truncate",size=20,italic=True)
    card(d,"base-latent",260,380,264,100,"",fill=TEAL,stroke="#5F8580")
    d.text("base-label",273,391,161,76,"Initial base\nlatent z_base,i",size=19,align="left")
    cube(d,"base-cube",440,404,65,55,fill=YELLOW)
    card(d,"refined-latent",566,380,255,100,"",fill=TEAL,stroke="#5F8580")
    d.text("refined-label",581,391,162,76,"Refined\nlatent z₀,ᵢ",size=20,align="left")
    cube(d,"refined-cube",744,404,61,55,fill=MINT)
    d.edge("task-to-backbone","task","backbone",exit=(.09,1),entry=(.62,0),color="#74966E",sw=3)
    d.edge("standard-decode","backbone","decoded-sequence",exit=(1,.08),entry=(0,.18),color="#737B77",sw=3)
    d.edge("truncate-to-base",start=(435,343),target="base-latent",entry=(.66,0),sw=1.7)
    d.edge("base-to-refined","base-latent","refined-latent",sw=2)

    card(d,"consolidation",1039,78,379,237,"",fill="#F0D9E2",stroke="#B96E79")
    brain(d,"consolidation-brain",1052,88,69)
    d.text("consolidation-text",1124,95,276,67,"Consolidation\nfrom experiences",size=23)
    d.shape("consolidation-query",1064,186,53,53,kind="ellipse",fill="#F7D6D9",stroke="#885760",sw=1.7)
    d.text("consolidation-query-label",1064,188,53,48,"cᵢ",size=25,italic=True)
    cube(d,"consolidation-input-latent",1067,253,58,42,fill="#C2DD9F")
    d.shape("consolidation-brace",1136,184,22,113,kind="curlyBracket",fill="none",stroke="#614650",sw=1.7,sketch=False)
    yarn(d,"consolidation-yarn",1184,226,54)
    d.text("weave-label",1233,196,104,30,"Weave",size=20,italic=True)
    cube(d,"consolidation-result",1321,232,71,57,fill=MINT)
    d.text("consolidation-latent-label",1291,286,118,24,"Latent z₀,ᵢ",size=17)
    d.edge("consolidation-generate","consolidation-yarn","consolidation-result",sw=1.8)

    d.polygon("instantiation-wedge",[(1100,437),(1131,335),(1131,518)],fill="#E4E3E2",stroke="none",sketch=False)
    d.shape("instantiation-panel",1131,335,287,183,fill="#E4E3E2",stroke="none",sketch=False)
    d.shape("weaver",922,345,192,177,kind="ellipse",fill="#F0D4DF",stroke="#A96778",sw=2.5)
    yarn(d,"weaver-yarn",988,354,54)
    d.text("weaver-label",939,420,158,80,"Latent\nWeaver",size=29,bold=True)
    d.text("refine-weave-label",832,375,94,64,"Refine\nWeave",size=19,italic=True)
    d.edge("weaver-to-refined","weaver","refined-latent",exit=(0,.5),entry=(1,.52),sw=2)
    d.edge("weaver-detail","weaver","consolidation",exit=(.58,0),entry=(.1,1),color="#B16D7B",sw=1.5)

    d.text("instantiation-label",1190,342,217,55,"Instantiation\nchoices",size=21)
    network(d,"slm",1144,419,79,73)
    d.text("slm-label",1140,393,80,25,"SLM",size=19,italic=True)
    d.text("plus-label",1222,425,28,35,"+",size=30)
    for letter,y in (("A",416),("B",461)):
        d.shape("lora-"+letter,1250,y,52,31,kind="trapezoid",fill="#DDE7A8",stroke="#667C49",sw=1.5,flipV=1)
        d.text("lora-label-"+letter,1250,y+1,52,28,letter,size=17)
    d.text("lora-title",1243,492,67,23,"LoRA",size=18)
    card(d,"adapter",1321,417,85,73,"Emb.\nProjector",fill="#D7E4BC",size=13,bold=False)
    d.text("adapter-title",1317,492,94,24,"Adapter",size=18)

    d.shape("optimization-panel",40,552,610,246,fill="#A1C5D0",stroke="#5C8090",sw=2.2,rounded=1,arcSize=10,dashed=1,dashPattern="5 4")
    title(d,"optimization-title",75,511,570,"Iterative test-time optimization",size=23)
    d.shape("update-mark",32,532,55,55,kind="ellipse",fill="#F7E7B2",stroke="#696458",sw=1.6)
    d.edge("update-loop",start=(42,549),end=(73,546),points=[(43,531),(73,531)],curved=True,color="#B46D7E",sw=1.8)
    d.text("update-label",109,555,100,30,"update",size=19,italic=True)
    snowflake(d,"self-reward",55,647,85)
    snowflake(d,"rollout-frozen",544,647,83)
    d.text("self-reward-label",47,737,106,56,"Self\nreward",size=19,italic=True)
    d.text("frozen-label",539,737,98,55,"Frozen\nLLM",size=19)
    cube(d,"optimized-latent",451,664,72,60,fill="#A9C58B")
    d.text("optimized-label",405,737,154,54,"Optimized\nlatent",size=19)
    for index,(y,prob,fill) in enumerate(((603,"0.5","#D7E7F4"),(661,"0.3","#AED6A0"),(719,"0.7","#D7E7F4"))):
        d.text("rollout-probability-"+str(index),172,y+3,44,35,prob,size=18)
        d.shape("rollout-a-"+str(index),235,y,43,39,fill=fill,stroke="#668795",sw=1.5)
        d.text("rollout-dots-"+str(index),280,y+2,40,33,"...",size=18)
        d.shape("rollout-b-"+str(index),324,y,43,39,fill=fill,stroke="#668795",sw=1.5)
        d.edge("reward-to-rollout-"+str(index),"self-reward","rollout-a-"+str(index),exit=(1,.5),entry=(0,.5),points=[(163,684),(182,y+20)],curved=True,sw=1.6)
        d.edge("latent-to-rollout-"+str(index),"optimized-latent","rollout-b-"+str(index),exit=(0,.5),entry=(1,.5),points=[(416,694),(398,y+20)],curved=True,sw=1.7)
    d.edge("optimization-loop","self-reward","optimized-latent",exit=(.5,0),entry=(.5,0),points=[(126,588),(372,577),(473,613)],curved=True,sw=2.3)
    d.edge("evaluate-latent","optimized-latent","rollout-frozen",sw=1.8)
    d.text("rollouts-label",203,766,244,30,"Multiple rollouts",size=20,italic=True)
    d.edge("refine-with-rollouts","refined-latent","optimization-panel",exit=(.21,1),entry=(.96,0),points=[(610,515)],color="#7B9495",sw=5)

    d.shape("momentum-panel",686,540,177,213,fill="#E9E4DF",stroke="none",sketch=False)
    d.text("momentum-label",692,547,166,61,"Momentum\nTransfer",size=22,italic=True)
    for i,(x,y,fill) in enumerate(((707,616,YELLOW),(789,616,MINT),(707,684,YELLOW),(789,684,MINT))):
        cube(d,"momentum-latent-"+str(i),x,y,58,47,fill=fill)
    d.line("momentum-bracket",[(698,610),(698,742),(719,742)],sw=1.7)
    d.edge("rollout-to-momentum","optimization-panel","momentum-panel",exit=(1,.50),entry=(0,.50),sw=1.8)
    d.edge("momentum-to-refined","momentum-panel","refined-latent",exit=(.35,0),entry=(.78,1),sw=1.8)
    d.text("merge-label",774,498,91,28,"merge",size=19,italic=True)

    buffer(d,"episodic-buffer",887,562,250,237)
    for row,y in enumerate((625,697)):
        d.shape("buffer-query-"+str(row),909,y,41,41,kind="ellipse",fill="#F5D0D1",stroke="#B4787E",sw=1.5)
        d.text("buffer-query-label-"+str(row),909,y+3,41,34,"cᵢ" if row==0 else "cₘ",size=19,italic=True)
        cube(d,"buffer-base-"+str(row),971,y-2,60,49,fill=YELLOW)
        cube(d,"buffer-refined-"+str(row),1051,y-2,60,49,fill=MINT)
    d.text("buffer-ellipsis",949,674,153,20,"... ...",size=17)
    d.text("buffer-caption",900,750,226,25,"query-latent pairs",size=19)
    d.edge("save-experience","optimization-panel","episodic-buffer",exit=(1,.93),entry=(0,.93),points=[(759,781)],dashed=True,sw=1.7)
    d.text("stored-triplet",652,796,228,28,"{(cᵢ, z_base,i, z*ᵢ)}",size=16,italic=True)

    d.shape("subset-back",1231,575,187,173,fill="#9CCFC6",stroke="none",sketch=False)
    d.shape("subset-front",1215,589,187,173,fill="#A9D6CC",stroke="none",sketch=False)
    d.shape("subset-query",1240,607,43,43,kind="ellipse",fill="#F5D0D1",stroke="#B4787E",sw=1.6)
    cube(d,"subset-base",1231,685,58,46,fill=YELLOW)
    cube(d,"subset-refined",1321,640,61,50,fill=MINT)
    d.shape("subset-brace-a",1201,622,18,113,kind="curlyBracket",fill="none",stroke=INK,sw=1.5,sketch=False)
    d.shape("subset-brace-b",1393,622,18,113,kind="curlyBracket",fill="none",stroke=INK,sw=1.5,flipH=1,sketch=False)
    d.text("subset-caption",1213,767,207,56,"High confidence\nlatent subset",size=20)
    d.edge("buffer-select-subset","episodic-buffer","subset-front",exit=(1,.46),entry=(0,.48),sw=1.8)
    d.text("selection-condition",1102,683,140,24,"E[Q(vᵢ)] > τ",size=17,rotation=90,whiteSpace="nowrap")
    d.edge("finetune-weaver","subset-front","weaver",exit=(.2,0),entry=(.78,.88),points=[(1179,556)],color="#916573",sw=5)
    d.text("finetune-label",1115,520,147,32,"Finetune",size=20,italic=True,rotation=32)
    return d


def source_values():
    return json.loads((Path(__file__).resolve().parents[1]/"assets/data/latent-evolve.json").read_text(encoding="utf-8"))


def figure3(data=None):
    data=source_values()["trajectories"] if data is None else data
    names=("MATH-500","MMLU","GPQA","JAMA")
    if set(data)!=set(names) or any(len(v)!=8 or any(not isinstance(n,(int,float)) or not math.isfinite(n) or not 0<=n<=100 for n in v) for v in data.values()):
        raise ValueError("provide eight finite percentages for MATH-500, MMLU, GPQA and JAMA")
    d=Diagram("Figure 3 · Day/night trajectories",1440,550)
    x0,y0,w,h=85,75,1056,360
    colors=("#4F7458","#8BA576","#7E6797","#A394AF")
    for i in range(8):
        d.shape(f"phase-{i}",x0+i*w/8,y0,w/8,h,fill="#F7DBDE" if i%2==0 else "#DCE9F6",stroke="none",sketch=False)
        d.text(f"phase-label-{i}",x0+i*w/8,y0-38,w/8,27,"Day" if i%2==0 else "Night",size=19,family="DejaVu Sans")
    yleft=lambda n:y0+h-(n-48)/36*h
    yright=lambda n:y0+h-(n-28)/36*h
    xpos=[x0+(i+.5)*w/8 for i in range(8)]
    for n in (50,60,70,80):
        y=yleft(n)
        d.line(f"grid-{n}",[(x0,y),(x0+w,y)],color="#BBC4C8",sw=.6)
        d.text(f"left-tick-{n}",25,y-12,49,24,str(n),size=17,family="DejaVu Sans")
    for n in (30,40,50,60):
        y=yright(n)
        d.text(f"right-tick-{n}",1147,y-12,48,24,str(n),size=17,family="DejaVu Sans")
    d.line("left-axis",[(x0,y0),(x0,y0+h)],color="#747D83",sw=1)
    d.line("right-axis",[(x0+w,y0),(x0+w,y0+h)],color="#747D83",sw=1)
    d.line("bottom-axis",[(x0,y0+h),(x0+w,y0+h)],color="#747D83",sw=1)
    markers=("ellipse","rhombus","triangle","triangle")
    for index,name in enumerate(names):
        ys=[(yleft if index<2 else yright)(n) for n in data[name]]
        d.line("trajectory-"+name,list(zip(xpos,ys)),color=colors[index],sw=2.3)
        for i,(x,y,value) in enumerate(zip(xpos,ys,data[name])):
            d.shape(f"point-{index}-{i}",x-6,y-6,12,12,kind=markers[index],fill=colors[index],stroke="white",sw=.6,sketch=False,
                    direction="south" if index==3 else "north")
            dy=((-30,12,-60,-30,-30,-30,-30,-30),
                (12,-30,14,12,12,-30,15,15),
                (-32,-32,-32,-32,-32,13,-32,-8),
                (-32,14,14,14,14,14,14,14))[index][i]
            dx=25 if index==2 and i==7 else 0
            d.text(f"value-{index}-{i}",x-31+dx,y+dy,62,24,f"{value:.1f}",size=14.5,color=colors[index],family="DejaVu Sans")
    for i,batch in enumerate(("MATH (200)","MATH (200)","MMLU (200)","MMLU (200)")):
        d.text(f"batch-{i}",x0+i*w/4,y0+h+12,w/4,30,batch,size=18,family="DejaVu Sans")
        if i:
            d.line(f"batch-divider-{i}",[(x0+i*w/4,y0),(x0+i*w/4,y0+h)],color="#8F999F",sw=.8)
    d.text("left-axis-name",85,491,470,28,"Left axis: in-domain accuracy (%)",size=15,family="DejaVu Sans",align="left")
    d.text("right-axis-name",676,491,465,28,"Right axis: out-of-domain accuracy (%)",size=15,family="DejaVu Sans",align="right")
    for i,(word,color) in enumerate((("Daytime Scaling","#F7DBDE"),("Nighttime Scaling","#DCE9F6"))):
        d.shape(f"legend-phase-{i}",1231,70+i*42,22,22,fill=color,stroke="#BDC5CC",sw=.6,sketch=False)
        d.text(f"legend-phase-word-{i}",1260,66+i*42,177,30,word,size=14,family="DejaVu Sans",align="left")
    for label,y in (("In-domain data",192),("Out-of-domain data",330)):
        d.text("legend-heading-"+str(y),1224,y,210,30,label,size=17,bold=True,family="DejaVu Sans",align="left")
    for i,(name,y) in enumerate(zip(names,(241,282,378,419))):
        d.line("legend-line-"+name,[(1230,y+12),(1263,y+12)],color=colors[i],sw=2.3)
        d.shape("legend-marker-"+name,1240,y+6,12,12,kind=markers[i],fill=colors[i],stroke="white",sw=.6,sketch=False,direction="south" if i==3 else "north")
        d.text("legend-name-"+name,1272,y,156,25,name,size=16,family="DejaVu Sans",align="left")
    return d


def hatched_bar(d,name,x,y,w,h,fill,pattern,parent="1"):
    group=d.group(name,x,y,w,h,parent=parent)
    d.shape(name+"-body",0,0,w,h,fill=fill,stroke="#627078",sw=.8,sketch=False,parent=group)
    if pattern in (1,2,3):
        for direction in ((1,-1) if pattern==3 else (1,) if pattern==1 else (-1,)):
            for index,offset in enumerate(range(-int(h),int(w)+1,12)):
                # Clip each diagonal segment to the bar rectangle.
                points=[]
                for yy in (0,h):
                    xx=offset+yy if direction==1 else w-offset-yy
                    if 0<=xx<=w:points.append((xx,yy))
                for xx in (0,w):
                    yy=xx-offset if direction==1 else w-offset-xx
                    if 0<=yy<=h:points.append((xx,yy))
                points=list(dict.fromkeys(points))
                if len(points)>=2:
                    d.line(name+f"-hatch-{direction}-{index}",points[:2],color="#8C9699",sw=.45,parent=group)
    if pattern==4:
        for row,yy in enumerate(range(7,int(h),13)):
            for col,xx in enumerate(range(5,int(w),10)):
                d.shape(name+f"-dot-{row}-{col}",xx,yy,1.4,1.4,kind="ellipse",fill="#879197",stroke="none",sketch=False,parent=group)
    return group


def figure4(data=None,lengths=None):
    raw=source_values()
    data=raw["ablation"] if data is None else data
    lengths=raw["latent_lengths"] if lengths is None else lengths
    if len(data)!=3 or len(lengths)!=5 or len(set(lengths))!=5:
        raise ValueError("three panels and five distinct latent lengths are required")
    for panel in data.values():
        if set(panel)!={"MATH-500","SciBench"} or any(len(v)!=5 or any(not isinstance(n,(int,float)) or not math.isfinite(n) or not 20<=n<=85 for n in v) for v in panel.values()):
            raise ValueError("this source-matched axis requires five percentages in [20,85] for each dataset")
    d=Diagram("Figure 4 · Ablation and sensitivity",1440,540)
    palette=("#D9CFAB","#B5D5BD","#BED8E5","#E7C7AA","#E8BCC5")
    for index,(name,panel) in enumerate(data.items()):
        x=42+index*468
        title(d,f"panel-title-{index}",x,15,430,name,size=24)
        plotx,ploty,plotw,ploth=x+42,87,371,341
        yy=lambda value:ploty+ploth-(value-20)/65*ploth
        for tick in (20,40,60,80):
            py=yy(tick)
            d.line(f"grid-{index}-{tick}",[(plotx,py),(plotx+plotw,py)],color="#D4DADD",sw=.7)
            d.text(f"tick-{index}-{tick}",x+1,py-11,34,22,str(tick),size=14,family="DejaVu Sans")
        d.line(f"axis-{index}",[(plotx,ploty),(plotx,ploty+ploth),(plotx+plotw,ploty+ploth)],color="#68737C",sw=1)
        for group,(dataset,values) in enumerate(panel.items()):
            gx=plotx+18+group*185
            for bar,value in enumerate(values):
                bx=gx+bar*28
                by=yy(value)
                hatched_bar(d,f"bar-{index}-{group}-{bar}",bx,by,23,ploty+ploth-by,palette[bar],bar)
                d.text(f"bar-value-{index}-{group}-{bar}",bx-4,by-23,31,21,f"{value:.1f}",size=10.5,family="DejaVu Sans")
            d.text(f"dataset-{index}-{group}",gx-7,438,163,29,dataset,size=18,family="DejaVu Sans")
    for i,(length,color) in enumerate(zip(lengths,palette)):
        x=360+i*151
        hatched_bar(d,"legend-length-"+str(length),x,492,28,23,color,i)
        d.text("legend-length-word-"+str(length),x+36,490,101,27,f"L′ = {length}",size=17,family="DejaVu Sans",align="left")
    d.text("accuracy-label",50,57,170,23,"Accuracy (%)",size=13,family="DejaVu Sans",align="left")
    return d
