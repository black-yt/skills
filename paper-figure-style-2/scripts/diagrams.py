"""Reusable layouts for component maps, lifecycle lanes and interface walkthroughs."""
import numpy as np
from style2 import Diagram, BLUE, CYAN, TEAL, MUTED, INK, PHASES, tint


def miniature_table(d,x,y,w,h,title,columns,rows,*,color=BLUE):
    d.rect(x,y,w,h,fill="white",edge=tint(color,.35),dash=(0,(2,2)))
    d.text(x+6,y+10,title,size=9,color=color)
    top=y+22
    d.line([(x+4,top),(x+w-4,top)],color="#D5DAE0",lw=.65)
    column_w=(w-12)/len(columns)
    for j,column in enumerate(columns):
        d.text(x+7+j*column_w,top+9,column,size=6.7,bold=True)
    row_h=min(14,(h-36)/max(1,len(rows)))
    for i,row in enumerate(rows):
        yy=top+23+i*row_h
        for j,value in enumerate(row):
            d.text(x+7+j*column_w,yy,value,size=6.5)
        if i<len(rows)-1:
            d.line([(x+5,yy+6),(x+w-5,yy+6)],color="#EBEEF2",lw=.5)


def component_overview(output, *, width_in=11, title="Evaluation Studio"):
    """Request: explain how benchmark suites, harnesses and execution are connected."""
    d=Diagram(485,width_in=width_in)
    left=d.group(4,5,358,262,"Benchmarks",zone="green",icon="network",icon_color="#69A2AC",icon_accent="#D8C659")
    mid=d.group(370,5,358,262,"Harnesses",zone="blue",icon="network",icon_color="#555066",icon_accent="#C8C3D7")
    right=d.group(736,5,358,262,"Environment",zone="purple",icon="cube",icon_color="#7A80E8",icon_accent="#D7F0FF")
    cards=[("Search","Web evidence tasks","search"),("Coding","Repository repair","code"),
           ("Scientific","Simulation and reasoning","science"),("End-to-end","Multi-stage research","network"),
           ("Terminal","Command-line workflows","terminal"),("General","Everyday assistance","records")]
    for i,(name,body,icon) in enumerate(cards):
        x=12+(i%2)*174; y=42+(i//2)*49
        d.card(x,y,165,44,name,body,color=left,icon=icon)
    d.rect(13,191,340,68,fill="white",edge=tint(left,.3),dash=(0,(2,2)))
    d.text(20,201,"Research artifacts",size=11,color=left)
    # Native-vector thumbnails with different scientific visual textures.
    rng=np.random.default_rng(2)
    for i,label in enumerate(("Microscopy","Materials","Diffraction","Climate")):
        x=20+i*82
        d.rect(x,211,75,31,fill=("#313941","#D9AF3F","#182B56","#E7F2F6")[i],edge=None)
        if i==0:
            for _ in range(45):
                xx,yy=rng.uniform([x+2,213],[x+73,239])
                d.circle(xx,yy,rng.uniform(.5,1.2),fill="#8F9DA5",edge=None)
        elif i==1:
            for j in range(12):
                d.line([(x+2+j*6,241),(x+18+j*4,212)],color=("#C753A5","#E9C751","#759F7D")[j%3],lw=4)
        elif i==2:
            for r in (3,6,10,14): d.circle(x+38,226,r,fill=None,edge="#817AA7",lw=.8)
        else:
            for j,c in enumerate(("#CA5D4F","#E1B361","#56A5A8")):
                pts=[(x+q,227+6*np.sin(q/10+j)) for q in range(3,73,2)]
                d.line(pts,color=c,lw=1)
        d.text(x+37,251,label,size=8,ha="center")
    for i,(name,body,icon) in enumerate([
        ("Model Endpoint","Configured model API","robot"),("Adapter","Native harness interface","adapter"),
        ("Harness Loop","Context and action selection","loop"),("Tool Calls","Shell, code and domain tools","tools")]):
        d.card(378+(i%2)*174,42+(i//2)*49,165,44,name,body,color=mid,icon=icon,
               icon_color="#4E67C5" if icon=="adapter" else None,
               icon_accent="#CDD6FA" if icon=="adapter" else None)
    d.rect(380,142,162,115,fill="white",edge=tint(mid,.25))
    for i,(name,body) in enumerate((("Context","Task and history"),("Action","Tool invocation"),("Observation","Returned feedback"))):
        y=150+i*33
        d.rect(405,y,126,23,fill="#EAF3FB",edge=None)
        d.text(468,y+8,name,size=11,bold=True,ha="center",color=mid)
        d.text(468,y+19,body,size=7.7,ha="center")
        if i<2: d.arrow([(468,y+24),(468,y+32)],color=mid,head=5)
    d.arrow([(405,230),(395,230),(395,161),(405,161)],color=mid)
    miniature_table(d,551,143,166,113,"Runner trace",("Step","Event"),
                    [("01","Read task"),("02","Select tools"),("03","Run checks"),("04","Save evidence")],color=mid)
    for i,(name,body,icon) in enumerate([
        ("Host Process","Local runtime","screen"),("Sandbox","Isolated execution","cube"),
        ("Session Interface","Commands and observations","screen"),("Runtime Feedback","Output and execution state","report")]):
        d.card(744+(i%2)*174,42+(i//2)*49,165,44,name,body,color=right,icon=icon,
               icon_color="#438E93" if name=="Session Interface" else None,
               icon_accent="#EF9860" if name=="Session Interface" else None)
    d.icon("network",749,142,size=25,color="#41434C",accent="#E2E4EA")
    d.text(779,155,"Execution",size=12,color=right,bold=True)
    d.icon("loop",928,142,size=25,color="#E75D67",accent="#FF9090")
    d.text(958,155,"Recovery",size=12,color=right,bold=True)
    miniature_table(d,748,174,335,83,"Managed runtime view",("Instance","Status","Resources"),
                    [("worker-01","ready","4 CPU / 8 GB"),("worker-02","running","4 CPU / 8 GB")],color=right)
    # Connect every top-level component to the control-plane bus.
    d.line([(184,283),(915,283)],color=INK,lw=1.1)
    for x in (184,550,915): d.arrow([(x,283),(x,268)],head=7)
    d.text(550,293,"Connect benchmarks, harnesses and environments",size=10,ha="center")
    control=d.group(4,307,524,158,"Control Plane",zone="gold",icon="sliders")
    analysis=d.group(568,307,526,158,"Analysis",zone="rose",icon="analysis")
    for i,(name,body,icon) in enumerate((("Run Lifecycle","State and ownership","play"),("Scheduling","Resource budgets","schedule"),
                                      ("Adapters","Native interfaces","tools"),("Run Records","Scores and evidence","records"))):
        xx=14+i*128
        d.icon(icon,xx,345,size=23)
        d.text(xx+27,350,name,size=10.8,bold=True,color=control)
        d.text(xx+27,370,body,size=7.8)
    miniature_table(d,15,391,236,64,"Run configuration",("Concurrent tasks","Retry budget"),[("4","2")],color=control)
    miniature_table(d,262,391,254,64,"Job records",("Run","State","Score"),[("trial-001","completed","0.78")],color=control)
    d.arrow([(529,391),(566,391)],head=6)
    d.text(548,376,"Run\nrecords",size=9,ha="center")
    for i,(name,body,icon) in enumerate((("Scores","Native metrics","chart"),("Capability Map","Task demand profiles","network"),
                                      ("Report","Evidence and insights","report"))):
        xx=578+i*169
        d.icon(icon,xx,345,size=25,
               color="#8E8697" if icon=="network" else None,
               accent="#D8D3DD" if icon=="network" else None)
        d.text(xx+31,350,name,size=12,bold=True,color=analysis)
        d.text(xx+31,369,body,size=8.7)
    miniature_table(d,580,391,326,64,"Metrics view",("Benchmark","Accuracy","Tasks"),[("Code Suite","78.4%","250")],color=analysis)
    miniature_table(d,918,391,164,64,"Evidence inspector",("Step","Observation"),[("04","Checks passed")],color=analysis)
    d.note()
    return d.save(output,title+" · component overview")


def lifecycle(output, *, width_in=11, stages=None):
    """Request: show scheduling, provisioning, execution and failure cleanup."""
    labels=stages or ("Scheduling","Runtime","Execution","Finalization")
    if len(labels)!=4: raise ValueError("This layout has four lifecycle stages")
    d=Diagram(475,width_in=width_in)
    accents=tuple(phase[2] for phase in PHASES)
    for i,(label,(fill,_,c)) in enumerate(zip(labels,PHASES)):
        yy=5+i*115
        d.rect(3,yy,1093,107,fill=fill,edge=None)
        d.circle(28,yy+53,17,fill=c,edge=c)
        d.circle(28,yy+53,14,fill=None,edge="white",lw=1)
        d.text(28,yy+53,str(i+1),size=20,color="white",ha="center")
        d.text(54,yy+53,label,size=18,bold=True,max_width=109)
    def block(x,y,w,title,body,phase,icon,*,icon_color=None,icon_accent=None):
        _,card_fill,c=PHASES[phase]
        d.rect(x,y,w,83,fill=card_fill,edge=c,radius=2,lw=.8)
        d.icon(icon,x+9,y+22,size=41,color=icon_color,accent=icon_accent)
        d.text(x+(w+48)/2,y+18,title,size=17,bold=True,ha="center",max_width=w-65)
        d.line([(x+58,y+32),(x+w-9,y+32)],color=c,lw=1.1)
        d.text(x+(w+48)/2,y+57,body,size=14,ha="center",max_width=w-65)
    block(171,17,239,"Run Scheduler","Pause · Resume\nCancel",0,"sliders")
    block(424,17,261,"Benchmark Adapter","Task Selection\nRepetition Count",0,"adapter")
    block(699,17,392,"Execution Backend","",0,"clock")
    d.rect(758,60,170,31,fill="#FDF4E2",edge="#EDC438",lw=.8)
    d.icon("play",765,67,size=17,color="#C8A831",accent="#F6DE70")
    d.text(852,75.5,"Integrated runner",size=13.5,ha="center",max_width=134)
    d.text(1007,75.5,"Native runners",size=14,ha="center",max_width=144)
    d.arrow([(411,58),(423,58)],color=accents[0]); d.arrow([(686,58),(698,58)],color=accents[0])
    block(171,132,405,"Environment Specification","Environment Images | Resource Requirement\nVariables | Lifetime and Quota",1,"chart",icon_color="#203C50",icon_accent="#91A6B7")
    block(788,132,303,"Runtime Interface","Provision | Execute & Stream\nTransfer files | Delete",1,"tools",icon_color="#647C88",icon_accent="#F2D265")
    d.arrow([(920,101),(920,132)],color=accents[1])
    d.arrow([(577,174),(787,174)],color=accents[1])
    d.text(678,160,"Runtime Configuration",size=14,color=accents[1],ha="center")
    d.arrow([(940,216),(940,233),(358,233),(358,247)],color=accents[2])
    block(171,247,374,"Sandbox Provision","Resource Admission | Instance Creation\nReadiness Check | Capacity Backoff",2,"sandbox")
    block(716,247,375,"Task Execution & Evaluation","Agent → Task Execution → Evaluator\nCommands | Observations | Outcomes",2,"terminal",icon_color="#242526",icon_accent="#626B6B")
    d.arrow([(546,289),(715,289)],color=accents[2])
    d.text(627,276,"Ready",size=15,color=accents[2],ha="center")
    block(171,369,454,"Resource Reclamation","Stop Instance → Delete → Release Resource\nRun-scoped Cleanup | Lifetime Expiry",3,"trash")
    block(777,369,314,"Results & Evidence","Task Score | Trajectories and Logs\nArtifacts | Run Metadata",3,"report")
    d.arrow([(942,331),(942,368)],color=accents[2])
    d.text(951,352,"Available Outputs",size=13,color=accents[2])
    d.arrow([(776,412),(626,412)],color=accents[3])
    d.arrow([(358,332),(358,351),(396,351),(396,368)],color=accents[3],dash=(0,(4,3)))
    d.line([(904,331),(904,351),(396,351)],color=accents[3],dash=(0,(4,3)),lw=1.4)
    d.text(627,340,"Failure, Timeout, Error",size=14,color=accents[3],ha="center")
    d.note()
    return d.save(output,"Managed evaluation lifecycle")


def ui_panel(d,x,y,w,h,kind,title):
    """Draw a tiny product view with real text and paths, not screenshots."""
    orange="#B55A26"; border="#E9E7EE"
    d.rect(x,y,w,h,fill="white",edge=border,lw=.7)
    for gx in np.arange(x+5,x+w,12): d.line([(gx,y+19),(gx,y+h)],color="#F4F3F8",lw=.3,z=1)
    for gy in np.arange(y+22,y+h,12): d.line([(x,gy),(x+w,gy)],color="#F4F3F8",lw=.3,z=1)
    d.rect(x,y,w,18,fill="#FFFFFF",edge=border,lw=.6)
    d.icon("network",x+7,y+2,size=13,color=orange)
    d.text(x+23,y+9,"Eval Studio",size=7.4,bold=True,color=orange)
    d.text(x+92,y+9,"Models    Agents    Runs    Reports",size=6.5,color=MUTED)
    d.rect(x+w-90,y+4,78,10,fill="#FFF0E1",edge=None,radius=3)
    d.text(x+w-51,y+9,"Daily recommendations",size=5.1,ha="center",color=orange)
    if kind=="home":
        d.text(x+w/2,y+48,"FROM EVALUATION TO IMPROVEMENT",size=6.3,color=orange,ha="center")
        d.text(x+w/2,y+83,"Advancing reliable agents\nacross the research workflow",size=19,bold=True,ha="center")
        d.text(x+w/2,y+121,"One workspace for tasks, evidence and capability analysis.",size=7.5,color=MUTED,ha="center")
        d.rect(x+w/2-84,y+143,80,22,fill=orange,edge=None,radius=10)
        d.text(x+w/2-44,y+154,"Start evaluating",size=7,color="white",ha="center")
        d.rect(x+w/2+3,y+143,89,22,fill="white",edge=border,radius=10)
        d.text(x+w/2+47,y+154,"Browse benchmarks",size=7,ha="center")
        d.text(x+w/2,y+h-29,"Scientific evaluation & benchmarks",size=12,bold=True,ha="center")
    elif kind=="settings":
        d.text(x+w/2,y+36,"Settings",size=16,bold=True,ha="center")
        for i,(label,detail) in enumerate((("Browser service","Ready"),("Result storage","Connected"),
            ("Evaluation status","All workers available"),("Target model registry","3 configured models"),
            ("Model A","Enabled"),("Model B","Enabled"))):
            yy=y+54+i*27
            d.rect(x+55,yy,w-110,22,fill="#FFFCF3" if i<4 else "white",edge=border,radius=4)
            d.circle(x+65,yy+11,2,fill=TEAL,edge=None)
            d.text(x+73,yy+11,label,size=7.5,bold=i==3)
            d.text(x+w-63,yy+11,detail,size=6.6,color=MUTED,ha="right")
    elif kind=="benchmarks":
        d.text(x+w/2,y+36,"Agent Evaluation",size=16,bold=True,ha="center")
        d.text(x+w/2,y+53,"Choose a benchmark and a compatible execution harness",size=6.8,color=MUTED,ha="center")
        names=("Research Suite","Code Suite","Terminal Suite","Discovery Suite","General Suite","Search Suite")
        for i,name in enumerate(names):
            xx=x+17+(i%3)*(w-24)/3; yy=y+71+(i//3)*81; cw=(w-42)/3
            d.rect(xx,yy,cw,72,fill="white",edge=border,radius=3)
            c=("#423550","#3E7386","#479FBB","#376D70","#556E9D","#35838B")[i]
            d.rect(xx+1,yy+1,cw-2,36,fill=c,edge=None)
            d.icon(("science","code","terminal","network","robot","search")[i],xx+cw/2-10,yy+7,size=22,color="#DAEDF5")
            d.text(xx+6,yy+47,name,size=7.5,bold=True)
            d.text(xx+6,yy+62,"View benchmark →",size=6.4,color=orange)
    elif kind=="records":
        d.text(x+17,y+36,"Evaluation Records",size=13,bold=True)
        d.rect(x+15,y+53,96,h-67,fill="#FAFAFC",edge=border)
        for i in range(6):
            d.rect(x+19,y+59+i*28,88,24,fill="#EDF5F4" if i==1 else "white",edge=border,radius=2)
            d.text(x+24,y+67+i*28,f"Run {i+1:03d} · Model A",size=6.4)
            d.text(x+24,y+76+i*28,"Completed",size=5.7,color=TEAL)
        d.text(x+125,y+65,"Research Suite · Run 002",size=9.5,bold=True)
        for i,(label,v) in enumerate((("Score","0.78"),("Tasks","180"),("Duration","24m"))):
            xx=x+125+i*92
            d.rect(xx,y+78,84,33,fill="#FAFAFC",edge=border,radius=2)
            d.text(xx+6,y+88,label,size=6.4,color=MUTED); d.text(xx+6,y+102,v,size=10,bold=True)
        for i in range(7):
            yy=y+125+i*14
            d.line([(x+123,yy+8),(x+w-15,yy+8)],color=border,lw=.5)
            d.text(x+126,yy,f"task_{i+1:03d}   Verify generated output",size=6.4)
            d.text(x+w-20,yy,"pass" if i%3 else "review",size=6.4,color=TEAL if i%3 else orange,ha="right")
    elif kind=="analysis":
        d.rect(x+12,y+31,87,h-44,fill="#FCFCFD",edge=border)
        for i in range(3):
            d.rect(x+16,y+39+i*46,79,40,fill="#ECF6F2" if i==1 else "white",edge=border,radius=2)
            d.text(x+20,y+52+i*46,f"Model {chr(65+i)}",size=7,bold=True)
            d.text(x+20,y+66+i*46,"Capability report",size=6,color=MUTED)
        d.text(x+114,y+41,"Success rate across demand levels",size=10.2,bold=True)
        d.text(x+114,y+61,"Observed tasks and fitted response profiles",size=7,color=MUTED)
        ax=d.fig.add_axes([(x+117)/d.width,1-(y+172)/d.height,190/d.width,94/d.height])
        from style2 import clean_axes
        xx=np.arange(1,6)
        for c,rates in zip((BLUE,"#ED9672",TEAL),([.91,.79,.65,.52,.36],[.84,.68,.51,.33,.2],[.96,.86,.76,.63,.48])):
            ax.plot(xx,rates,color=c,lw=.7)
        ax.set(ylim=(0,1),xlim=(1,5),xticks=[1,3,5],yticks=[0,.5,1])
        ax.tick_params(labelsize=4,length=1,pad=1); clean_axes(ax)
        for i,label in enumerate(("Instruction adherence","Tool use","Code execution")):
            d.text(x+330,y+102+i*22,label,size=6.4,color=(BLUE,"#C77652",TEAL)[i])
        d.text(x+114,y+191,"Curves summarize task outcomes; they do not measure",size=6.6,color=MUTED)
        d.text(x+114,y+203,"isolated skills or establish causal effects.",size=6.6,color=MUTED)
    else:
        raise ValueError(f"Unknown interface panel: {kind}")
    d.text(x+w/2,y+h+14,title,size=12,ha="center")


def interface_walkthrough(output, *, width_in=11):
    """Request: illustrate five screens of an evaluation product in a paper."""
    d=Diagram(845,width_in=width_in)
    for x,y,kind,title in (
        (28,12,"home","(a) Homepage"),(572,12,"settings","(b) Service configuration"),
        (28,289,"benchmarks","(c) Benchmark selection"),(572,289,"records","(d) Evaluation records"),
        (300,566,"analysis","(e) Capability analysis report")):
        ui_panel(d,x,y,500,243,kind,title)
    d.note("Illustrative product interface · every label and panel is drawn as editable vector content")
    return d.save(output,"Evaluation product · five-screen walkthrough")
