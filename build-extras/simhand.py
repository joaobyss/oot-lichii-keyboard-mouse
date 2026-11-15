import random, math
def unwrap(d,p):
    h=p//2
    while d>h: d-=p
    while d<-h: d+=p
    return d
def unwrap_fast(d,p,pred,thr,stopfrac=0.1):
    h=p//2; r=unwrap(d,p)
    if abs(pred)<h*thr or abs(r)<p*stopfrac: return r
    n=0
    while pred-r>h and n<8: r+=p; n+=1
    while r-pred>h and n<16: r-=p; n+=1
    return r
def hand_path(rng, total_ms, peak_cm_s_range, wiggle):
    # returns true position (counts) at each ms
    pos=[0.0]*(total_ms+1); t=0; x=0.0; d=1
    while t<total_ms:
        peak=rng.uniform(*peak_cm_s_range)*630/1000.0      # counts per ms
        tau=rng.uniform(90,350)                             # ms
        D=peak*tau/1.875
        if rng.random()<wiggle: d=-d
        elif rng.random()<0.5: d=d
        D*=d
        n=int(tau)
        for i in range(1,n+1):
            s=i/tau; mj=10*s**3-15*s**4+6*s**5
            if t+i<=total_ms: pos[t+i]=x+D*mj
        x+=D; t+=n
        # rest
        rest=int(rng.uniform(0,120))
        for i in range(1,rest+1):
            if t+i<=total_ms: pos[t+i]=x
        t+=rest
    for i in range(1,total_ms+1):
        if pos[i]==0.0 and i>0 and pos[i-1]!=0.0: pos[i]=pos[i-1]
    return pos
def run(period,step,T,peak,wiggle,thr,seed,total=60000):
    rng=random.Random(seed); pos=hand_path(rng,total,peak,wiggle)
    # pointer (px) with 1 ms helper wrap, picture center 0
    ptr=0.0; hw=period/2; samples=[]; true=[]
    last_ptr=0; last_true=0; pred=0; err_abs=0; tot=0; bad=0; n=0
    prevpos=0.0; ptr_int=0
    for ms in range(1,total+1):
        ptr+= (pos[ms]-pos[ms-1])*step
        if ptr>hw: ptr-=period
        elif ptr<-hw: ptr+=period
        if ms%T==0:
            pi=int(math.floor(ptr));
            d=pi-last_ptr; last_ptr=pi
            tr=(pos[ms]-last_true)*step; last_true=pos[ms]
            r_new=unwrap_fast(d,period,pred,thr); pred=r_new
            r_old=unwrap(d,period)
            yield tr,r_old,r_new
def score(period,step,T,peak,wiggle,thr,seeds=3):
    res={'old':[0,0,0],'new':[0,0,0]}
    for sd in range(seeds):
        for tr,ro,rn in run(period,step,T,peak,wiggle,thr,sd):
            for k,r in (('old',ro),('new',rn)):
                e=abs(r-tr); res[k][0]+=e; res[k][1]+=abs(tr)
                if e>150: res[k][2]+=1
    return {k:(round(v[0]/max(v[1],1)*100,2),v[2]) for k,v in res.items()}
if __name__=='__main__':
    print('X axis period 1024, step 0.5; columns: relative error %, number of samples off by >150 px')
    for T in (16,33):
        for peak in ((15,60),(30,120),(60,250)):
            for wig in (0.3,):
                for thr in (0.5,0.75):
                    print('T',T,'peak cm/s',peak,'thr',thr,score(1024,0.5,T,peak,wig,thr))
