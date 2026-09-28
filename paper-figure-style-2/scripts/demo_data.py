"""Deterministic, fictional inputs. Never substitute these for user experiments."""
import numpy as np

DIMENSIONS = ("INST", "TOOLS", "SEARCH", "PLAN", "REASON", "CODE")
DIMENSION_NAMES = ("Instruction adherence", "Tool use", "Evidence search",
                   "Research planning", "Scientific reasoning", "Code execution")
SUITES = ("Research Suite", "Code Suite", "Terminal Suite", "Discovery Suite", "General Suite", "Search Suite")
MODELS = ("Model A", "Model B", "Model C")


def benchmark_demands():
    """Each benchmark supplies a task-by-dimension array on the 0–5 scale."""
    rng = np.random.default_rng(821)
    coverage = np.array([[.95,.97,.12,.82,.53,.88],[.18,1,.4,.58,.01,.99],
                         [.98,.96,.17,.45,.08,.99],[.68,.93,.68,.95,.82,.87],
                         [.95,.9,.18,.23,0,.4],[.03,.99,1,0,.08,0]])
    positive_means = np.array([[2.5,3.4,2.6,2.,3.4,3.], [1.5,2.3,2.3,1.3,1.,2.4],
                              [2.2,3.1,2.8,1.8,3.5,2.6],[1.9,4.1,4.,3.1,4.2,4.4],
                              [1.9,1.8,2.8,1.5,1.,1.1],[1.,2.6,3.9,1.,1.5,1.]])
    result=[]
    for probability, mean in zip(coverage,positive_means):
        positive=rng.binomial(4,(mean-1)/4,size=(250,6))+1
        present=rng.random((250,6))<probability
        result.append(positive*present)
    return result


def response_observations():
    n=np.array([[150,130,96,48,14],[140,128,90,60,28],[12,40,34,17,5],
                [33,75,61,28,9],[16,32,46,20,7],[140,126,96,71,35]])
    rates=np.array([
        [[.94,.74,.58,.39,.08],[1,.94,.82,.24,.03],[1,.95,.83,.6,.08],
         [1,.9,.47,.12,0],[.68,.37,.23,.1,0],[1,.98,.9,.2,.03]],
        [[.98,.77,.65,.44,.07],[1,.95,.86,.4,.04],[1,.98,.92,.68,.2],
         [1,.98,.7,.21,.11],[.85,.53,.35,.15,0],[1,.99,.93,.33,.06]],
    ])
    return np.arange(1,6),np.rint(rates*n).astype(int),n


def harness_counts():
    """Shape: benchmark, model, capability, harness, demand group."""
    rng=np.random.default_rng(312)
    base=np.array([[.91,.87,.8],[.79,.7,.57],[.55,.46,.31]])
    groups=np.array([[150,74,26],[102,92,45],[17,29,14],[58,44,16],[8,14,9],[114,105,51]])
    totals=np.broadcast_to(groups[None,None,:,None,:],(3,3,6,3,3)).copy()
    # Empty cells are part of the example, and must never be displayed as zero.
    totals[0,:,[0,3,4],:,2]=0
    totals[0,:,0,:,1]=0
    totals[1,:,4,:,0]=0
    scores=np.empty_like(totals)
    for b in range(3):
        for m in range(3):
            for c in range(6):
                for h in range(3):
                    rates=np.clip(base[b]+.025*m+(.045 if h==0 else -.03 if h==1 else .01)
                                  +.035*np.cos(c*1.2+h)+rng.normal(0,.022,3),.04,.99)
                    scores[b,m,c,h]=rng.binomial(totals[b,m,c,h],rates)
    return scores,totals


def repeated_tasks():
    """Task-level data shared by recovery summary and evidence table."""
    rng=np.random.default_rng(718)
    demands=np.column_stack([
        rng.choice(np.arange(6),180,p=p) for p in (
            [.10,0,.25,.5,.13,.02],[.04,0,.18,.48,.27,.03],
            [.75,.03,.06,.10,.04,.02],[.12,.05,.42,.28,.11,.02],
            [.3,.05,.1,.3,.2,.05],[.07,.02,.1,.48,.28,.05])])
    high_counts=rng.choice([0,1,2,3],180,p=[.22,.12,.11,.55])
    scores=rng.uniform(0,.77,(180,3))
    for i, high in enumerate(high_counts):
        runs=rng.choice(3,high,replace=False)
        scores[i,runs]=rng.choice([.81,.9,.95,1.],high)
    ids=[f"{domain}/{task}_{i+1:03d}" for i,(domain,task) in enumerate(
        ([("finance","report_audit"),("software","dependency_fix"),
          ("biology","variant_pipeline"),("materials","energy_fit"),
          ("education","record_reconcile"),("data","forecast_check")]*30))]
    return ids,scores,demands


def recovery_counts():
    _,scores,demands=repeated_tasks()
    high=(scores>=.8).sum(axis=1)
    one=[]; two=[]; total=[]
    hits=np.zeros((6,5),int); ns=np.zeros((6,5),int)
    for c in range(6):
        mask=demands[:,c]>0
        one.append(np.sum(mask&(high==1)))
        two.append(np.sum(mask&(high==2)))
        total.append(mask.sum())
        for level in range(1,6):
            at=demands[:,c]==level
            hits[c,level-1]=np.sum(at&((high==1)|(high==2)))
            ns[c,level-1]=at.sum()
    return np.array(one),np.array(two),np.array(total),hits,ns


FAILURE_LABELS = ("Agent / sandbox\ntimeout", "Agent execution\nfailed", "Access\ndenied",
                  "Sandbox\nunavailable", "Evaluator\nunavailable", "Network\nfailure",
                  "Command\nfailed", "Workspace\npreparation", "Context\noverflow")
FAILURE_COLORS = ("#B9CEE8", "#F5AE83", "#A7D9C5", "#D9CCEA", "#F9E9B7",
                  "#F7CE94", "#C8B9DE", "#D6E7CB", "#D4D4D4")
