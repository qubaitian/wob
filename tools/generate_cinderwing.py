"""Sculpt a faceted dragon from tapered cross sections. Coordinates in game metres."""
from math import sin, cos, pi, sqrt
from collections import defaultdict
from pathlib import Path
import base64, json, struct, uuid, zlib

root = Path(__file__).resolve().parents[1]
colors = dict(hide='332e40', ridge='514654', shadow='272333', belly='ac6342',
              copper='df935f', web='774466', fold='613b5e', lightweb='8b5279',
              horn='867779', bone='cfb6a0', tip='f4dfb9', gold='ffcb53',
              iris='ff891c', black='190f20', mouth='70323f', crest='aa5049')
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,k): return tuple(x*k for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a): return mul(a,1/(sqrt(dot(a,a)) or 1))
def mix(a,b,k): return add(mul(a,1-k),mul(b,k))
parts=[]
group='Body'
pivot={'Body':(0,0,0),'Head':(0,6.5,3.2),'Jaw':(0,8.15,5.76),
       'LeftWing':(1.9,5.75,.3),'RightWing':(-1.9,5.75,.3)}
def record(name,verts,faces):
    assert all(dot(cross(sub(verts[j],verts[i]),sub(verts[k],verts[i])),cross(sub(verts[j],verts[i]),sub(verts[k],verts[i])))>1e-15 for (i,j,k),_ in faces), name
    parts.append((group,name,verts,faces))

def loft(name, rows, mat, sides=9, under=None, band=None):
    # Each row contains a centre and two radii. A transported frame keeps horns
    # and angled legs continuous through their bends.
    pts=[r[0] for r in rows]; verts=[]; faces=[]; prev=None
    def face(indices, color, outside):
        i,j,k=indices
        if dot(cross(sub(verts[j],verts[i]),sub(verts[k],verts[i])),outside)<0: j,k=k,j
        faces.append(((i,j,k),color))
    for i,(p,w,h) in enumerate(rows):
        direction=norm(sub(pts[min(i+1,len(pts)-1)],pts[max(i-1,0)]))
        basis=prev or ((1,0,0) if abs(direction[0])<.86 else (0,0,1))
        u=norm(sub(basis,mul(direction,dot(basis,direction)))); v=norm(cross(direction,u));prev=u
        for j in range(sides):
            theta=2*pi*j/sides
            verts.append(add(p,add(mul(u,w*cos(theta)),mul(v,h*sin(theta)))))
        if i==0:continue
        mid=mix(pts[i-1],p,.5)
        for j in range(sides):
            a=(i-1)*sides+j;b=(i-1)*sides+(j+1)%sides;c=b+sides;d=a+sides
            outside=sub(mix(verts[a],verts[c],.5),mid)
            color=band[i-1] if band else (under if under and norm(outside)[1]<-.36 else mat)
            face((a,b,c),color,outside);face((a,c,d),color,outside)
    for i in [0,len(rows)-1]:
        ix=len(verts);verts.append(pts[i]);outside=sub(pts[i],pts[1 if i==0 else -2])
        for j in range(sides):face((ix,i*sides+j,i*sides+(j+1)%sides),band[0 if i==0 else -1] if band else mat,outside)
    record(name,verts,faces)

def rod(name,stations,material,sides=7,band=None):
    loft(name,[(tuple(pt),r,r) for pt,r in stations],material,sides,band=band)
def fan(name,vertices,triangles):
    record(name,vertices,triangles)

# 躯干和四肢。每个截面记录中心位置、宽度半径和厚度半径，单位为米。
loft('Thorax and hips',[
 ((0,3.4,-5.2),.63,.78),((0,3.92,-4.15),1.54,1.52),
 ((0,4.15,-2.55),2.03,1.94),((0,4.35,-.45),1.98,2.04),
 ((0,4.83,1.0),2.34,2.28),((0,4.98,2.15),1.68,1.83),((0,5.1,2.9),1.16,1.3)],'hide',12,under='belly')
loft('Arched neck',[
 ((0,4.9,1.43),1.57,1.37),((0,5.46,2.55),1.38,1.24),
 ((0,6.5,3.24),1.09,1.05),((0,7.43,3.74),.95,.98),
 ((0,8.1,4.81),.91,.95)],'hide',10,under='belly')
for x,y,z,w in [(0,4.36,3.22,1.13),(0,4.94,3.54,1.02),(0,5.54,3.94,.89),(0,6.1,4.27,.8),(0,6.74,4.57,.73)]:
    loft(f'Gorget {y}',[((x,y,z-.46),w,.48),((x,y+.09,z),w*.91,.29),((x,y+.22,z+.12),w*.53,.20)],'belly',8,under='copper')
tail=[((0,3.55,-4.25),1.02),((.35,3.24,-5.85),.86),((1.25,2.73,-7.25),.67),((2.8,2.17,-8.3),.50),((4.6,1.74,-8.72),.36),((6.25,1.55,-8.36),.24),((7.56,1.84,-7.49),.14),((8.15,2.35,-6.64),.02)]
rod('Swept tail',tail,'hide',9)
for i,(z,y,r) in enumerate([(-7.7,2.9,.29),(-5.55,4.2,.44),(-4.25,5.15,.61),(-3.05,5.87,.72),(-1.65,6.12,.78),(-.18,6.47,.83),(1.01,6.84,.75),(2.1,7.13,.65),(2.89,7.65,.54)]):
    x=1.95 if i==0 else .25 if i==1 else 0
    loft(f'Dorsal blade {i}',[((x,y,z),r*.44,r*.78),((x,y+r*.8,z-.2),r*.32,r*.5),((x,y+r*1.7,z-.7*r),.025,.035)],'ridge',6,band=['ridge','horn'])
for side in [1,-1]:
    label='Left' if side==1 else 'Right'
    def P(x,y,z):return (side*x,y,z)
    # Bring the elbows outside the ribcage and break the rear silhouette at the hock.
    fore=[(1.67,5.02,1.32,1.08,1.25),(2.22,4.26,1.39,1.12,1.23),
          (2.64,3.35,1.04,.94,.99),(2.93,2.72,.74,.80,.88),
          (3.17,2.08,1.20,.80,.87),(3.38,1.38,1.88,.65,.74),
          (3.54,.68,2.55,.53,.57)]
    hind=[(1.42,4.32,-3.57,1.21,1.48),(2.12,3.86,-3.17,1.37,1.46),
          (2.67,3.12,-2.56,1.18,1.23),(2.95,2.40,-2.27,.94,1.01),
          (3.18,1.84,-3.13,.81,.82),(3.26,1.35,-3.86,.62,.67),
          (3.32,.69,-3.55,.53,.57)]
    for leg,stations in [('Fore',fore),('Hind',hind)]:
        offset=0 if side==1 else (-.64 if leg=='Fore' else .48)
        def footpoint(x,y,z): return P(x,y,z+offset)
        loft(label+' '+leg+' limb',[(footpoint(x,y,z),w,h) for x,y,z,w,h in stations],
             'hide',11,under='ridge')
        # An overlapping outer plate follows the muscle, leaving the flexion joint exposed.
        x,y,z,_,_=stations[1]
        loft(label+' '+leg+' shoulder shield',[
            (footpoint(x+.42,y+.42,z-.10),.70,.78),
            (footpoint(x+.78,y+.12,z+.01),.76,.81),
            (footpoint(x+.72,y-.43,z+.12),.57,.58),
            (footpoint(x+.52,y-.88,z+.13),.21,.27)],'ridge',8)
        x,y,z,_,_=stations[-1]
        loft(label+' '+leg+' broad foot',[
            (footpoint(x,.59,z-.37),.50,.47),(footpoint(x,.48,z+.03),.70,.43),
            (footpoint(x+.04,.37,z+.48),.83,.33),(footpoint(x+.05,.29,z+.87),.64,.25)],
            'ridge',10)
        for j in [-1,0,1]:
            toe=f'{label} {leg} digit {j}'
            rod(toe,[(footpoint(x+j*.42,.39,z+.44),.29),
                     (footpoint(x+j*.56,.29,z+.91),.26),
                     (footpoint(x+j*.69,.23,z+1.14-abs(j)*.08),.17)],'hide',8)
            rod(toe+' claw',[(footpoint(x+j*.60,.28,z+.96),.19),
                            (footpoint(x+j*.72,.22,z+1.24-abs(j)*.07),.14),
                            (footpoint(x+j*.86,.065,z+1.59-abs(j)*.13),.018)],
                'bone',7,band=['horn','tip'])
    for i in range(4):
        z=-2.8+i*1.18;x=1.92+.17*(i==3)
        loft(f'{label} flank plate {i}',[(P(x-.3,4.42,z-.65),.20,.40),(P(x,4.8,z),.40,.55),(P(x-.08,4.95,z+.55),.27,.35)],'ridge',7)
# 头骨、棘冠、角和下颌。下颌有独立的转轴，用于张嘴。
group='Head'
loft('Wedge skull',[
 ((0,8.23,4.04),.78,.80),((0,8.53,4.77),1.39,1.12),((0,8.62,5.57),1.42,.95),
 ((0,8.41,6.34),1.03,.64),((0,8.29,7.31),.81,.46),((0,8.29,7.83),.66,.30)],'hide',10,under='ridge')
loft('Nasal keel',[((0,9.37,5.06),.39,.33),((0,9.36,5.76),.35,.24),((0,8.85,6.65),.25,.16),((0,8.59,7.64),.09,.09)],'ridge',6)
for side in [1,-1]:
    name='L' if side==1 else 'R'
    def P(x,y,z):return (side*x,y,z)
    # Broad frill fans frame each cheek behind the recurved horns.
    tips=[(.55,11.13,3.25),(1.42,11.18,3.60),(2.31,10.47,3.50),(3.19,9.63,3.38),(3.25,8.7,3.21),(2.85,7.77,3.42)]
    base=P(.74,8.65,4.45)
    for i,t in enumerate(tips):
        tp=P(*t); rod(f'{name} crown spine {i}',[(base,.22),(mix(base,tp,.66),.13),(tp,.013)],'horn',6,band=['ridge','bone'])
        if i:
            a=mix(base,P(*tips[i-1]),.89);b=mix(base,tp,.86)
            mid=add(mix(a,b,.5),(0,-.13,.11))
            fan(f'{name} frill web {i}',[base,a,mid,b],[((0,1,2),'crest'),((0,2,3),'belly')])
    rod(name+' great sickle horn',[(P(1.03,9.0,4.99),.52),(P(1.56,9.38,4.57),.49),(P(2.11,9.39,4.71),.40),(P(2.42,9.13,5.20),.31),(P(2.36,8.92,5.83),.23),(P(2.16,8.94,6.34),.13),(P(1.96,9.21,6.69),.015)],'horn',9,band=['ridge','horn','horn','bone','bone','tip'])
    rod(name+' cheek barb',[(P(1.0,8.2,5.57),.37),(P(1.62,8.13,4.96),.28),(P(2.08,7.91,4.23),.035)],'ridge')
    # Tilted almond, partly hooded; keep a forward-facing plane for raid distance.
    eye=[P(.55,8.68,6.55),P(.86,8.96,6.44),P(1.32,9.05,5.94),P(1.18,8.73,6.28),P(.87,8.58,6.49)]
    center=P(.97,8.81,6.54)
    fan(name+' amber eye',eye+[center],[((i,(i+1)%5,5),'gold' if i<3 else 'iris') for i in range(5)])
    fan(name+' slit pupil',[P(.96,8.92,6.52),P(1.035,8.80,6.57),P(.97,8.68,6.56),P(.92,8.81,6.58)],[((0,1,2),'black'),((0,2,3),'black')])
    rod(name+' brow ridge',[(P(.51,8.85,6.58),.145),(P(.95,9.15,6.28),.23),(P(1.32,9.28,5.87),.23),(P(1.54,9.46,5.43),.055)],'ridge',7)
    rod(name+' nostril',[(P(.42,8.45,7.78),.14),(P(.47,8.48,7.87),.115)],'black',7)
    for i in range(4):
        z=6.05+i*.40;x=1.05-i*.14;y=8.03-.04*i
        rod(f'{name} fang {i}',[(P(x,y,z),.133 if i<2 else .105),(P(x,y-.16,z+.04),.10),(P(x*.97,y-(.55 if i==1 else .31),z+.13),.016)],'tip',6)
group='Jaw'
loft('Lower jaw and chin',[((0,7.87,5.53),1,.53),((0,7.80,6.11),1.03,.44),((0,7.72,6.93),.8,.28),((0,7.72,7.68),.60,.18)],'ridge',9,under='belly')
loft('Tongue',[((0,8.03,6.0),.75,.15),((0,7.96,6.83),.65,.12),((0,7.89,7.53),.44,.09)],'mouth',8)
for side in [1,-1]:
    group='LeftWing' if side==1 else 'RightWing'
    def P(x,y,z):return (side*x,y,z)
    shoulder=P(1.62,5.6,.55); elbow=P(3.6,7.1,-1.05); knuckle=P(6.15,10.55,.80)
    rod(group+' leading arm',[(shoulder,.73),(elbow,.51),(P(4.75,8.95,.0),.41),(knuckle,.36)],'hide',9)
    rod(group+' thumb hook',[(knuckle,.28),(P(6.10,11.1,1.06),.20),(P(6.30,11.37,1.37),.12),(P(6.60,11.26,1.62),.018)],'bone',7)
    tips=[(14.0,6.88,-2.65),(12.43,4.55,-4.68),(9.65,3.49,-5.58),(6.56,3.15,-6.15),(3.65,3.46,-5.62),(1.50,4.7,-3.26)]
    mids=[(10.4,10.08,-.18),(9.61,8.42,-1.54),(8.11,7.88,-2.16),(6.32,7.20,-2.68),(4.83,6.45,-2.66),(3.18,6.1,-1.75)]
    for i,(tip,half) in enumerate(zip(tips,mids)):
        end=P(*tip);mid=P(*half)
        rod(group+f' finger {i}',[(knuckle,.26 if i==0 else .16),(mid,.23 if i==0 else .118),(mix(mid,end,.86),.105 if i==0 else .064),(end,.016)],'ridge',7,band=['hide','ridge','horn'])
        if not i:continue
        prev=P(*tips[i-1]);pm=P(*mids[i-1])
        # Concave trailing edge between finger tips, with two softly ridged panels.
        valley=add(mix(prev,end,.5),(0,.85,.49));ridge=add(mix(pm,mid,.5),(0,.16,-.45))
        fan(group+f' sail {i}',[knuckle,pm,prev,valley,end,mid,ridge],[
            ((0,1,6),'web'),((0,6,5),'lightweb'),((1,2,6),'web'),((2,3,6),'fold'),
            ((3,4,6),'web'),((4,5,6),'lightweb')])
    fan(group+' inner sail',[shoulder,elbow,knuckle,P(*mids[-1]),P(*tips[-1])],[((0,1,4),'fold'),((1,2,3),'web'),((1,3,4),'web')])

# 站姿。调整前爪位置、胸口朝向和承重侧，同时移动相应的动画转轴。
# Bake the stance into the editable mesh and repose the existing animation pivots.
def smooth(low,high,v):
    k=max(0,min(1,(v-low)/(high-low)))
    return k*k*(3-2*k)

def rotate(p,center,yaw=0,pitch=0,roll=0):
    x,y,z=sub(p,center)
    a,b,c=(angle*pi/180 for angle in (yaw,pitch,roll))
    y,z=y*cos(b)-z*sin(b),y*sin(b)+z*cos(b)
    x,z=x*cos(a)+z*sin(a),-x*sin(a)+z*cos(a)
    x,y=x*cos(c)-y*sin(c),x*sin(c)+y*cos(c)
    return add(center,(x,y,z))

def chest(p):
    return add(rotate(p,(0,4.8,.4),yaw=-22,roll=5),(-.54,-.18,.14))

def posed(grp,name,p):
    x,y,z=p
    if grp in ('Head','Jaw'):
        neck=chest(pivot['Head'])
        return rotate(chest(p),neck,yaw=29,pitch=8)
    if grp in ('LeftWing','RightWing'):
        # The loaded shoulder sits lower, while the opposite wing is relaxed.
        side=1 if grp=='LeftWing' else -1
        return rotate(chest(p),chest(pivot[grp]),roll=2 if side==1 else 4)
    if 'Fore' in name:
        side=1 if name.startswith('Left') else -1
        # Keep the soles level and translate the whole paw below the ankle.
        reach=(.17,0,.86) if side==1 else (.53,0,-.36)
        return mix(add(p,reach),chest(p),smooth(.92,4.95,y))
    if 'Hind' in name or 'tail' in name.lower():
        return p
    if name=='Arched neck' or name.startswith('Gorget'):
        base=chest(p)
        counter=smooth(5.6,8.1,y)
        return rotate(base,chest(pivot['Head']),yaw=29*counter,pitch=8*counter)
    return mix(p,chest(p),smooth(-3.1,1.1,z))

mouth_world=posed('Head','',(0,7.92,7.44))
posed_pivots={g:(p if g=='Body' else posed(g,'',p)) for g,p in pivot.items()}
parts=[(g,name,[posed(g,name,p) for p in vertices],faces) for g,name,vertices,faces in parts]
pivot=posed_pivots
print('Muzzle offset:',tuple(round(v,4) for v in sub(mouth_world,pivot['Head'])))
# 输出。Blockbench 工程和游戏模型共用上面生成的形状和站姿。
def id_for(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,'wob/cinderwing/'+name))
def vec16(p):return [round(x*16,4) for x in p]
def chunk(name,b):return struct.pack('>I',len(b))+name+b+struct.pack('>I',zlib.crc32(name+b)&0xffffffff)
palette=list(colors)
rows=[b'\0'+b''.join(bytes.fromhex(colors[m]) for m in palette) for _ in range(2)]
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',len(palette),2,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b'')
def data_url(mime,payload):return 'data:'+mime+';base64,'+base64.b64encode(payload).decode()
parents={'Body':None,'Head':'Body','Jaw':'Head','LeftWing':'Body','RightWing':'Body'}
groups={n:dict(name=n,uuid=id_for(n),origin=vec16(p),children=[],export=True,isOpen=False) for n,p in pivot.items()}
elements=[]
batches=defaultdict(lambda:defaultdict(lambda:([],[])))
for grp,name,vs,fs in parts:
    # The edit model keeps separate named pieces while the renderer batches by surface.
    el=dict(name=name,type='mesh',uuid=id_for(grp+'/'+name),origin=vec16(pivot[grp]),vertices={},faces={})
    local=[sub(v,pivot[grp]) for v in vs]
    el['vertices']={f'v{i}':vec16(p) for i,p in enumerate(local)}
    for i,(tri,m) in enumerate(fs):
        keys=[f'v{k}' for k in tri];k=palette.index(m)
        uv=dict(zip(keys,[[k+.2,.2],[k+.8,.2],[k+.5,1.8]]))
        el['faces'][f'f{i}']=dict(vertices=keys,uv=uv,texture=0)
        points,normals=batches[grp][m];a,b,c=[local[t] for t in tri]
        n=norm(cross(sub(b,a),sub(c,a)));points.extend((a,b,c));normals.extend([n]*3)
    groups[grp]['children'].append(el['uuid']);elements.append(el)
for n,parent in parents.items():
    if parent:groups[parent]['children'].append(groups[n])
bb=dict(meta=dict(format_version='4.10',model_format='free',box_uv=False),name='Cinderwing',
        resolution=dict(width=len(palette),height=2),elements=elements,outliner=[groups['Body']],
        textures=[dict(id='0',uuid=id_for('Obsidian palette'),name='Obsidian and amethyst',width=len(palette),height=2,uv_width=len(palette),uv_height=2,source=data_url('image/png',png))])
(root/'assets/cinderwing.bbmodel').write_text(json.dumps(bb,separators=(',',':'))+'\n')
g=dict(asset=dict(version='2.0',generator='World of Block'),scene=0,scenes=[dict(nodes=[0])],nodes=[],meshes=[],accessors=[],bufferViews=[],materials=[])
buf=bytearray()
def accessor(rows,pos=False):
    index=len(g['bufferViews'])
    g['bufferViews'].append(dict(buffer=0,byteOffset=len(buf),byteLength=len(rows)*12,target=34962))
    buf.extend(b''.join(struct.pack('<fff',*r) for r in rows))
    acc=dict(bufferView=index,componentType=5126,count=len(rows),type='VEC3')
    if pos:acc.update(min=list(map(min,zip(*rows))),max=list(map(max,zip(*rows))))
    g['accessors'].append(acc);return index
for m,col in colors.items():
    rgb=[(int(col[i:i+2],16)/255)**2.2 for i in [0,2,4]]
    mat=dict(name=m,doubleSided=True,pbrMetallicRoughness=dict(baseColorFactor=rgb+[1],roughnessFactor=.75,metallicFactor=.05))
    if m in ('gold','iris'):mat['emissiveFactor']=mul(rgb,.80)
    g['materials'].append(mat)
for name,p in pivot.items():
    parent=parents[name];node=dict(name=name,translation=sub(p,pivot[parent]) if parent else p,mesh=len(g['meshes']))
    children=[list(pivot).index(n) for n,v in parents.items() if v==name]
    if children:node['children']=children
    g['nodes'].append(node)
    prims=[dict(attributes=dict(POSITION=accessor(v,True),NORMAL=accessor(n)),material=palette.index(m)) for m,(v,n) in batches[name].items()]
    g['meshes'].append(dict(name=name,primitives=prims))
g['buffers']=[dict(byteLength=len(buf),uri=data_url('application/octet-stream',buf))]
(root/'client/public/models/cinderwing.gltf').write_text(json.dumps(g,separators=(',',':'))+'\n')
print(len(parts),'editable pieces,',sum(len(f) for _,_,_,f in parts),'triangles',len(buf),'bytes')
