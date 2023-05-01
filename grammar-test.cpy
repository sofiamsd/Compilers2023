#$ Moisiadou Sofia 4446 #$
#$ Tsiaousi Thomai 4510 #$
def main_expression_test():
#{
    #declare a,b,c,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z
    
    def null(x): #{
        x = int(input());
        print(1);
        return(0);
    #}    
        
    a = 1;
    a = +1;
    b = -1;
    c = a+b;
    d = a*c;
    e = (a*d + b//c)*((((d+1)*((-1)) + (1*2*3*4*(a+b*8)))));
    c = (1+2)+3*4+1-1//2;
    e = a*b*c*(1+(1+2+d));
    f = +null(0);
    f = -null(0);
    f = null(f+null(null(a)*null(b)));
    
    return(f);
#}

def main_boolean_test():
#{
    #declare x,y,z
    
    x=1;
    
    if (x==1):
        if (x==2 or x==3):
            #{
            if (x==4 and x==5): return(1);
            else: print(1);
            
            if (1==0 or x==4 and x==5 or [x==6 and x==7 and x>=8 and not [x!=10]]):
                #{
                    print(1);
                #}
            #}
    
    while ([not [1==1]]):return(x);        
    
    while (not [not [1==1]]):return(x);
        
#}



if __name__ == "__main__":
    main_expression_test();
    main_boolean_test();