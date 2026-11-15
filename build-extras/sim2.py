import math, random
from simhand import hand_path, unwrap
def dec(d,p,pred,prev2,thr,stopfrac,lin):
    h=p//2; r=unwrap(d,p)
    # prediction
    q=pred+ (pred-prev2)*lin
    if abs(pred)<h*thr or abs(r)<p*stopfrac: return r
    n=0
    while q-r>h and n<8: r+=p; n+=1
    while r-q>h and n<16: r-=p; n+=1
    return r
def run(period,step,T,peak,wig,thr,stopfrac,lin,seeds=3,total=60000):
    tot=[0,0,0,0]
    for sd in range(seeds):
        rng=random.Random(sd); pos=hand_path(rng,total,peak,wig)
        ptr=0.0; hw=period/2; last_ptr=0; last_true=0; pred=0; prev2=0
        for ms in range(1,total+1):
            ptr+=(pos[ms]-pos[ms-1])*step
            if ptr>hw: ptr-=period
            elif ptr<-hw: ptr+=period
            if ms%T==0:
                pi=int(math.floor(ptr)); d=pi-last_ptr; last_ptr=pi
                tr=(pos[ms]-last_true)*step; last_true=pos[ms]
                r=dec(d,period,pred,prev2,thr,stopfrac,lin); prev2=pred; pred=r
                e=abs(r-tr); tot[0]+=e; tot[1]+=abs(tr)
                if e>150: tot[2]+=1
                if e>400: tot[3]+=1
    return round(tot[0]/max(tot[1],1)*100,2), tot[2], tot[3]
if __name__=='__main__':
    print('rel.error%, n(>150px), n(>400px)   [X axis, period 1024]')
    for step in (0.5,0.25):
        for T in (16,33):
            for peak in ((30,120),(60,250)):
                row=[]
                for (thr,sf,lin) in ((9,0.1,0),(0.5,0.1,0),(0.4,0.1,0),(0.5,0.1,0.5),(0.5,0.1,1.0),(0.4,0.1,0.5)):
                    row.append(((thr,sf,lin),run(1024,step,T,peak,0.3,thr,sf,lin)))
                print('step',step,'T',T,'peak',peak)
                for k,v in row: print('   ',('classic' if k[0]==9 else k),v)
