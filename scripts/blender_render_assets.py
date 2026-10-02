"""Rebuild original Interstellar Fleets models and registered render passes.

Run: blender -b --python scripts/blender_render_assets.py -- --asset all
Use --hero-only for a fast art-direction review. Blender 4.5+/5.x, no add-ons.
One tile is one model unit. Sprite projection corrects ground foreshortening;
all passes retain the same origin, framing, animation phase and light direction.
"""
from __future__ import annotations
import argparse
import json
import math
import random
import sys
from pathlib import Path
import bpy
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tmp' / 'blender-renders'
TAU = math.tau
M = {}
PARTS = []
MOVERS = []
EMITTERS = []

ASSETS = {
    'interstellar-lab': dict(kind='lab', tiles=5, color=(.08,.56,.57), code='IL-09'),
    'quantum-replicator': dict(kind='replicator', tiles=4, color=(.43,.18,.70), code='QR-04'),
    'interstellar-dust-collector': dict(kind='collector', tiles=3, color=(.90,.48,.08), code='DC-03'),
    'stellar-fusion-drive': dict(kind='fusion', tiles=4, color=(.06,.44,.81), code='SF-07'),
    'antimatter-drive': dict(kind='antidrive', tiles=4, color=(.53,.16,.70), code='AM-08'),
    'interstellar-foundry': dict(kind='foundry', tiles=5, color=(.78,.22,.045), code='IF-05'),
    'interstellar-electromagnetic-plant': dict(kind='electro', tiles=4, color=(.08,.47,.44), code='EM-06'),
    'interstellar-biochamber': dict(kind='bio', tiles=3, color=(.24,.54,.075), code='BC-02'),
    'interstellar-cryogenic-plant': dict(kind='cryo', tiles=5, color=(.18,.54,.68), code='CP-01'),
    'interstellar-dust': dict(kind='dust', tiles=2, color=(.34,.48,.65), code='ID-11'),
    'antimatter': dict(kind='capsule', tiles=2, color=(.55,.16,.77), code='AC-12'),
    'ship-starter-pack': dict(kind='ship', tiles=4, color=(.14,.49,.57), code='SP-10'),
}


def enum(obj, prop, value):
    if getattr(obj, prop) == value:
        return
    options = [v.identifier for v in obj.bl_rna.properties[prop].enum_items]
    if value not in options:
        raise RuntimeError(f'{prop}: {value} not in {options}')
    setattr(obj, prop, value)


def mat(name, color, metal=0.0, rough=.45, emit=0, wear=True):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes
    p = next(x for x in n if x.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    m.diffuse_color = (*color,1)
    if emit:
        p.inputs['Emission Color'].default_value = (*color,1)
        p.inputs['Emission Strength'].default_value = emit
        EMITTERS.append((m, emit))
        m['emissive'] = True
    elif wear:
        tex = n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=34
        tex.inputs['Detail'].default_value=3.5; tex.inputs['Roughness'].default_value=.72
        ramp=n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.30
        ramp.color_ramp.elements[0].color=(*(c*.57 for c in color),1)
        ramp.color_ramp.elements[1].position=.75
        ramp.color_ramp.elements[1].color=(*(min(1,c*1.18+.025) for c in color),1)
        m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs['Fac'])
        m.node_tree.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
        fine=n.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value=145
        bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.17; bump.inputs['Distance'].default_value=.022
        m.node_tree.links.new(fine.outputs['Fac'],bump.inputs['Height'])
        m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    return m


def palette(color):
    M.clear(); EMITTERS.clear()
    specs={'iron':((.22,.25,.24),.78,.46),'dark':((.043,.053,.055),.7,.55),
           'edge':((.32,.32,.28),.8,.38),'copper':((.46,.20,.07),.78,.32),
           'paint':(tuple(c*.48+.018 for c in color),.5,.5),'ivory':((.40,.43,.38),.35,.54),
           'rust':((.26,.105,.039),.55,.74),'rubber':((.017,.021,.02),.1,.7),
           'yellow':((.77,.49,.09),.25,.55),'glass':((.035,.13,.16),.67,.16)}
    for k,(c,metal,rough) in specs.items(): M[k]=mat(k,c,metal,rough)
    M['glow']=mat('process light',color,.2,.28,2.7,False)
    M['white']=mat('warm instrument light',(.75,.89,.70),.1,.3,1.6,False)
    M['amber']=mat('amber lamp',(.95,.29,.04),.1,.3,2.3,False)


def finish(obj,name,material,bevel=0,smooth=False):
    obj.name=name; obj.data.materials.append(M.get(material,material))
    PARTS.append(obj)
    if bevel:
        mod=obj.modifiers.new('machined edge bevel','BEVEL'); mod.width=bevel; mod.segments=2
    if smooth and obj.type=='MESH':
        for p in obj.data.polygons: p.use_smooth=True
    if bevel:
        mod=obj.modifiers.new('weighted face normals','WEIGHTED_NORMAL'); mod.keep_sharp=True
    return obj


def box(name,loc,size,material='iron',bevel=.04,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot: o.rotation_euler=rot
    return finish(o,name,material,bevel)


def cyl(name,loc,r,depth,material='iron',rot=None,verts=48,r2=None):
    if r2 is None: bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc)
    else: bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r,radius2=r2,depth=depth,location=loc)
    o=bpy.context.object
    if rot: o.rotation_euler=rot
    return finish(o,name,material,.025,True)


def ball(name,loc,scale,material='glass'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=loc)
    o=bpy.context.object; o.scale=scale
    return finish(o,name,material,0,True)


def tor(name,loc,r,t,material='edge',rot=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=10,location=loc,major_radius=r,minor_radius=t)
    o=bpy.context.object
    if rot:o.rotation_euler=rot
    return finish(o,name,material,0,True)


def pipe(name,points,r=.06,material='copper'):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=12
    cu.bevel_depth=r; cu.bevel_resolution=3
    s=cu.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):
        p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o)
    return finish(o,name,material)


def rod(name,a,b,r=.07,material='edge'):
    a,b=Vector(a),Vector(b); d=b-a
    o=cyl(name,(a+b)/2,r,d.length,material,verts=16)
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return o


def bolts(loc,r,n=12,axis='Z'):
    for i in range(n):
        a=i*TAU/n; x,y,z=loc
        if axis=='Z':x+=r*math.cos(a);y+=r*math.sin(a); rot=None
        else:x+=r*math.cos(a);z+=r*math.sin(a);rot=(math.pi/2,0,0)
        cyl('hex bolt',(x,y,z),.041,.055,'edge',rot,6)


def flange(loc,r=.22,axis='Z'):
    rot=(math.pi/2,0,0) if axis=='Y' else None
    cyl('bolted pipe flange',loc,r,.11,'edge',rot)
    bolts(loc,r*.72,8,axis)


def vents(loc,size,rows=9):
    x,y,z=loc; w,h=size
    box('recessed heat exchanger',(x,y,z),(w,.12,h),'rubber',.02)
    for i in range(rows):
        box('cast cooling louver',(x,y-.08,z-h/2+(i+.5)*h/rows),(w*.92,.12,.04),'edge',.009)


def label(text,loc,size=.17,rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new('cast equipment serial','FONT'); cu.body=text; cu.size=size; cu.extrude=.001
    o=bpy.data.objects.new('serial '+text,cu); bpy.context.collection.objects.link(o)
    o.location=loc;o.rotation_euler=rot
    finish(o,o.name,'ivory')


def hazard(loc,w=1.0):
    x,y,z=loc
    box('safety stripe backing',loc,(w,.025,.18),'rubber',.01)
    for i in range(int(w/.18)):
        box('ochre safety stripe',(x-w/2+.12+i*.18,y-.022,z),(.085,.025,.17),'yellow',.003,rot=(0,-.25,0))


def base(w,d=None,code=''):
    d=d or w
    box('structural foundation',(0,0,.20),(w,d,.40),'dark',.13)
    box('cast deck',(0,0,.42),(w-.14,d-.14,.16),'iron',.08)
    for x in (-w/2+.18,w/2-.18):
        box('longitudinal deck rail',(x,0,.54),(.12,d-.15,.10),'edge',.015)
        for y in (-d/2+.22,d/2-.22):
            box('anchor shoe',(x,y,.16),(.35,.42,.30),'rust',.04)
            cyl('foundation bolt',(x,y,.6),.073,.075,'edge',verts=6)
    for y in (-d/2+.17,d/2-.17):
        box('end deck rail',(0,y,.54),(w-.20,.12,.10),'edge',.015)
    for x in (-w*.32,w*.32):hazard((x,-d/2-.01,.24),w*.20)
    if code:label(code,(-.32,-d/2-.026,.19),.13)
    for side in (-1,1):
        for j in range(7):
            y=-d*.34+j*d*.11
            box('deck access plate',(side*(w/2-.35),y,.523),(.31,d*.095,.026),'iron',.01)
            cyl('countersunk deck screw',(side*(w/2-.35),y,.55),.025,.018,'edge',verts=6)
        pipe('deck service conduit',[(side*(w/2-.1),-d*.30,.64),(side*(w/2-.1),0,.64),(side*(w/2-.1),d*.31,.64)],.031,'copper')
    for x in (-w*.33,w*.33):
        box('service module',(x,-d*.30,.73),(.48,.42,.42),'paint',.035)
        box('instrument panel',(x,-d*.30-.22,.76),(.36,.028,.19),'dark',.01)
        for j in range(3):ball('instrument diode',(x-.105+j*.105,-d*.30-.245,.80),(.023,.016,.023),'white' if j<2 else 'amber')


def tank(x,y,z,r,h,material='ivory'):
    cyl('pressure vessel',(x,y,z),r,h,material)
    ball('domed vessel crown',(x,y,z+h/2),(r,r,r*.48),material)
    ball('domed vessel floor',(x,y,z-h/2),(r,r,r*.38),'iron')
    for zz in (z-h*.31,z+h*.31):
        tor('reinforcement hoop',(x,y,zz),r+.015,.05,'edge')
    flange((x,y,z+h/2+r*.48+.04),r*.27)


def animate(obj,mode,amount):MOVERS.append((obj,mode,amount,obj.location.copy(),obj.rotation_euler.copy()))


def lab(spec):
    base(4.65,code=spec['code'])
    cyl('octagonal laboratory pressure hull',(0,.15,.98),1.78,.95,'ivory',verts=12)
    tor('external copper feed',(0,.15,.77),1.78,.075,'copper')
    cyl('observatory turret',(0,.15,1.54),1.48,.24,'dark')
    ball('smoked quartz observatory',(0,.15,1.57),(1.35,1.35,.82),'glass')
    for i in range(12):
        a=i*TAU/12
        points=[]
        for j in range(9):
            t=j*math.pi/2/8
            points.append((1.37*math.cos(t)*math.cos(a),.15+1.37*math.cos(t)*math.sin(a),1.59+.83*math.sin(t)))
        pipe('observatory radial rib',points,.035,'edge')
    for z,r in [(1.61,1.37),(1.97,1.23),(2.20,.94)]:tor('optical scanner ring',(0,.15,z),r,.025,'glow')
    scan=tor('rotating spectral sensor',(0,.15,2.03),1.36,.048,'copper',(.20,0,0));animate(scan,'spin',1)
    cyl('zenith cap',(0,.15,2.44),.23,.13,'edge');ball('research beacon',(0,.15,2.57),(.10,.10,.11),'glow')
    for x in (-1.83,1.83):
        tank(x,.45,1.02,.24,.82,'paint')
        pipe('lab coolant return',[(x,-1.1,.65),(x,-.4,1.2),(x,.45,1.48)],.06)
        vents((x,-.70,1.05),(.47,.48),6)
    for x in (-.75,.75):
        box('sealed research console',(x,-1.55,1.08),(.95,.35,.69),'paint')
        box('observation glass',(x,-1.74,1.19),(.70,.028,.23),'glass',.02)
        box('console readout',(x,-1.76,.93),(.45,.023,.045),'glow',.005)
    for x in (-1.65,1.65):
        rod('communications mast',(x,1.65,.5),(x,1.65,2.6),.035)
        ball('mast navigation lamp',(x,1.65,2.63),(.055,.055,.075),'amber')
        tor('antenna array',(x,1.65,2.14),.18,.018,'edge',(.35,0,0))
    bolts((0,.15,1.65),1.48,16)


def replicator(spec):
    base(3.70,code=spec['code'])
    cyl('matter receiver',(0,0,.68),1.14,.28,'iron')
    for r in (.72,.96,1.15):tor('receiver traces',(0,0,.86),r,.025,'copper')
    for x in (-1.33,1.33):
        box('magnet buttress',(x,.2,1.59),(.44,.75,2.15),'paint',.08)
        vents((x,-.205,1.51),(.31,1.24),13)
    rot=(math.pi/2,0,0)
    for y,r,material in [(0,1.23,'edge'),(.3,1.28,'dark'),(-.17,1.08,'copper'),(-.22,1,'glow')]:
        tor('quantum induction aperture',(0,y,1.9),r,.11 if material!='glow' else .032,material,rot)
    for i in range(12):
        a=i*TAU/12;x=1.25*math.cos(a);z=1.90+1.25*math.sin(a)
        o=box('magnet winding shoe',(x,0,z),(.30,.58,.25),'copper',.035);o.rotation_euler.y=-a
        rod('field shunt',(x,-.35,z),(x,-.44,z),.048,'edge')
    core=box('suspended matter crystal',(0,-.05,1.9),(.52,.52,.52),'glow',.035,rot=(.4,.5,.3));animate(core,'spin',1)
    for i in range(6):
        a=i*TAU/6
        shard=box('orbiting matter fragment',(.67*math.cos(a),-.03,1.9+.67*math.sin(a)),(.16,.22,.16),'edge',.015,rot=(a,a,a));animate(shard,'spin',-1)
    for side in (-1,1):
        pipe('heavy field cable',[(side*.8,1.30,.6),(side*1.6,1.1,.9),(side*1.4,.45,2.0)],.105,'rubber')
        tank(side*.9,1.2,1.0,.23,.8,'ivory')


def collector(spec):
    base(2.72,code=spec['code'])
    cyl('collector azimuth bearing',(0,0,.74),1.03,.38,'iron')
    bolts((0,0,.97),.90,12)
    box('filter housing',(0,.4,1.15),(1.3,.95,.8),'paint',.09)
    # Lathed annular parabolic dish; open center and real thickness.
    verts=[]; faces=[]; segments=64;rings=12
    for j in range(rings):
        r=.20+j*1.02/(rings-1);z=1.45+.56*(r/1.22)**2
        for i in range(segments):a=i*TAU/segments;verts.append((r*math.cos(a),-.22+r*math.sin(a),z))
    for j in range(rings-1):
        for i in range(segments):a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
    me=bpy.data.meshes.new('parabolic intake shell');me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new('golden dust intake reflector',me);bpy.context.collection.objects.link(o);finish(o,o.name,'copper',0,True)
    solid=o.modifiers.new('dish metal thickness','SOLIDIFY');solid.thickness=.04
    tor('intake rim',(0,-.22,2.01),1.23,.055,'edge')
    for r in (.42,.66,.90):tor('collector annular mesh',(0,-.22,1.45+.56*(r/1.22)**2),r,.019,'dark')
    for i in range(8):
        a=i*TAU/8
        rod('intake support spoke',(.21*math.cos(a),-.22+.21*math.sin(a),1.47),(1.2*math.cos(a),-.22+1.2*math.sin(a),1.98),.023,'edge')
    cyl('field feed stalk',(0,-.22,1.86),.1,.80,'dark')
    ball('dust detector',(0,-.22,2.29),(.18,.18,.16),'glow')
    sweep=tor('sweeping dust detector',(0,-.22,2.17),.38,.035,'glow',(.35,0,0));animate(sweep,'spin',1)
    for x in (-1.10,1.10):
        tank(x,.7,1.1,.18,.75,'ivory')
        pipe('filter cyclone feed',[(x,.70,1.60),(x,.95,1.80),(0,.8,1.50)],.075)


def drive(spec,anti=False):
    base(3.7,4.7,spec['code'])
    rot=(math.pi/2,0,0)
    # Chamber runs north-south. Multiple actual manifold parts avoid a plain rocket cone.
    cyl('reaction pressure chamber',(0,.2,1.35),.85,2.8,'dark',rot)
    for y in (-.85,-.42,0,.42,.84,1.25):
        tor('reactor cooling collar',(0,y,1.35),.85,.11,'edge',rot)
        tor('exposed induction winding',(0,y-.12,1.35),.80,.045,'glow' if anti else 'copper',rot)
    for x in (-1.24,1.24):
        box('long armored radiator',(x,.25,1.12),(.63,2.9,.83),'paint',.10)
        for i in range(14):box('drive fin',(x,-1.06+i*.20,1.60),(.69,.095,.30),'edge',.015)
        pipe('reactor fuel manifold',[(x,1.5,1.3),(x,.9,1.94),(x,-.9,1.94),(x,-1.4,1.3)],.065,'copper')
    cyl('ceramic convergent throat',(0,-1.5,1.35),.54,.7,'ivory',rot,r2=.81)
    cyl('nozzle outer bell',(0,-2.02,1.35),1.02,.58,'edge',rot,r2=.56)
    cyl('nozzle dark throat',(0,-2.32,1.35),.84,.015,'rubber',rot)
    tor('nozzle energized rim',(0,-2.345,1.35),.77,.045,'glow',rot)
    cyl('exhaust source',(0,-2.349,1.35),.52,.016,'glow',rot)
    for i in range(12):
        a=i*TAU/12
        rod('nozzle reinforcement rib',(.55*math.cos(a),-1.78,1.35+.55*math.sin(a)),(.99*math.cos(a),-2.29,1.35+.99*math.sin(a)),.044,'dark')
    bolts((0,-2.36,1.35),.95,12,'Y')
    if anti:
        for y in (-.4,.9):
            tor('antimatter containment hoop',(0,y,1.35),1.2,.14,'paint',rot)
            tor('containment luminous seam',(0,y-.12,1.35),1.18,.037,'glow',rot)
        ball('contained antiparticle core',(0,.1,2.19),(.30,.7,.22),'glow')
    else:
        for x in (-.47,.47):pipe('superheated transfer conduit',[(x,1.5,1.75),(x,.8,2.16),(x,-.9,2.12)],.09,'ivory')
    tank(0,1.85,1.08,.50,.72,'paint')


def foundry(spec):
    base(4.65,code=spec['code'])
    cyl('crucible foundation',(0,-.25,.75),1.40,.40,'iron')
    cyl('smelting crucible',(0,-.25,1.47),1.15,1.15,'rust',r2=1.36)
    cyl('molten metal surface',(0,-.25,2.06),1.11,.03,'glow')
    tor('refractory rim',(0,-.25,2.08),1.31,.18,'dark')
    for z in (1.05,1.35,1.65):tor('crucible induction winding',(0,-.25,z),1.25,.08,'copper')
    for i in range(10):
        a=i*TAU/10
        rod('crucible restraining stave',(1.28*math.cos(a),-.25+1.28*math.sin(a),.78),(1.47*math.cos(a),-.25+1.47*math.sin(a),2.14),.095,'edge')
    for x in (-1.74,1.74):
        box('casting pillar',(x,.5,1.26),(.51,1.55,1.4),'paint',.08)
        vents((x,-.32,1.4),(.39,.85),9)
        pipe('molten metal transfer',[(x,-1.8,.60),(x,-1.5,1.1),(x,-.5,1.1),(.9*x,-.25,1.3)],.13)
    for x in (-.85,.85):
        tank(x,1.62,1.68,.37,1.92,'rust')
        cyl('stack crown',(x,1.62,2.83),.43,.15,'dark')
        tor('stack heat indicator',(x,1.62,2.89),.28,.04,'amber')
    for x in (-1.74,1.74):
        for z in (.88,1.12,1.36,1.60):
            box('foundry casing reinforcing rib',(x,.5,z),(.55,1.60,.04),'edge',.009)
        for y in (.15,.45,.75,1.05):
            cyl('foundry cabinet bolt',(x,y,2.00),.045,.06,'edge',verts=6)
    for x in (-1.9,1.9):
        rod('hoist upright',(x,1.5,.6),(x,1.5,2.62),.08)
        rod('hoist diagonal',(x,1.5,1.5),(x,.8,2.56),.05)
    rod('lid bridge',(-1.6,.8,2.54),(1.6,.8,2.54),.15)
    agitator=box('crucible moving scraper',(0,-.25,2.20),(1.8,.16,.12),'edge',.025);animate(agitator,'spin',1)


def electro(spec):
    base(3.72,code=spec['code'])
    box('electrical switchgear',(0,.9,1.09),(2.8,.85,1.0),'paint',.08)
    for x in (-.93,.93):
        cyl('ceramic coil tower',(x,-.25,1.26),.57,1.35,'ivory')
        for j in range(10):tor('copper solenoid winding',(x,-.25,.70+j*.13),.61,.045,'copper')
        cyl('field cap',(x,-.25,1.98),.66,.17,'dark')
        tor('active coil rim',(x,-.25,2.10),.48,.035,'glow')
        bolts((x,-.25,2.09),.57,8)
    cyl('wafer fabrication table',(0,-.30,.94),.59,.19,'dark')
    wafer=cyl('rotating silicon wafer',(0,-.30,1.08),.49,.035,'glass');animate(wafer,'spin',1)
    for i in range(5):box('wafer gold circuit',(-.3+i*.15,-.30,1.108),(.023,.68,.009),'copper',0)
    for x in (-1.5,1.5):pipe('insulated high voltage cable',[(x,-1.15,.62),(x,.6,2.25),(x*.55,.9,2.0)],.085,'rubber')
    vents((0,.44,1.39),(1.50,.46),7)
    rod('field bus',(-.93,-.25,2.26),(.93,-.25,2.26),.075,'copper')
    for x in (-.93,.93):ball('ceramic insulator',(x,-.25,2.26),(.15,.15,.14),'ivory')


def bio(spec):
    base(2.72,code=spec['code'])
    for i,(x,y,r) in enumerate([(-.70,.38,.46),(.70,.38,.46),(0,-.55,.59)]):
        cyl('cultivation vessel base',(x,y,.8),r+.08,.40,'dark')
        ball('ribbed culture vessel',(x,y,1.5),(r,r,.76),'paint')
        for a in range(8):
            t=a*TAU/8
            pipe('organic vessel reinforcement',[(x+r*.65*math.cos(t),y+r*.65*math.sin(t),.93),(x+r*1.015*math.cos(t),y+r*1.015*math.sin(t),1.52),(x+r*.5*math.cos(t),y+r*.5*math.sin(t),2.12)],.038,'copper')
        for z in (1.10,1.85):tor('cultivation gasket',(x,y,z),r*.86,.055,'edge')
        ball('culture inspection window',(x,y-r*.91,1.50),(r*.55,.09,.40),'glass')
        for j in range(3):ball('culture luminescence',(x-.12+j*.12,y-r-.01,1.48+.12*math.sin(j)),(.038,.035,.10),'glow')
        flange((x,y,2.19),.15)
        pipe('nutrient feeder',[(x,y,2.22),(x,y+.22,2.47),(0,1.06,1.45)],.044,'rubber')
    tank(0,1.0,1.13,.24,1.05,'ivory')
    for x in (-1.13,1.13):pipe('nutrient floor manifold',[(x,-.95,.62),(x,-.15,.60),(x,.95,.68)],.068,'copper')


def cryo(spec):
    base(4.65,code=spec['code'])
    for x in (-.95,.95):
        tank(x,.2,1.77,.65,2.04,'ivory')
        for z in (.96,1.25,1.54,1.83,2.12,2.41):tor('cryogenic insulation seam',(x,.2,z),.66,.033,'edge')
        box('thermal observation strip',(x,-.45,1.73),(.15,.06,1.25),'glass',.02)
        box('cold process light',(x,-.49,1.73),(.038,.015,1.08),'glow',.005)
        for y in (-1.20,1.38):
            pipe('vacuum jacket cooling loop',[(x,y,.65),(x,y,2.05),(x,.6,2.87)],.11,'paint')
        flange((x,.2,3.15),.22)
    for x in (-1.89,1.89):
        box('heat pump housing',(x,0,1.15),(.52,2.25,1.25),'paint',.07)
        vents((x,-1.15,1.22),(.41,.95),12)
        for j in range(10):box('heat pump radiator fin',(x,-.9+j*.20,1.83),(.56,.05,.30),'edge',.01)
    for x in (-1.1,0,1.1):
        pipe('front cryogenic manifold',[(x,-2.15,.60),(x,-1.85,.80),(x,-1.30,.83)],.105,'copper')
        flange((x,-2.13,.6),.17,'Y')
    rod('instrument rack',(-1.45,.95,3.1),(1.45,.95,3.1),.065)


def dust(spec):
    rng=random.Random(117)
    for i in range(19):
        a=rng.random()*TAU;r=rng.random()*.70
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(r*math.cos(a),r*math.sin(a),.24+rng.random()*.58))
        o=bpy.context.object;o.scale=(.20+rng.random()*.25,.16+rng.random()*.18,.2+rng.random()*.6);o.rotation_euler=(rng.random(),rng.random(),rng.random())
        finish(o,'fractured interstellar mineral','iron' if i%3 else 'copper')
        if i%2==0:
            cyl('exotic crystal inclusion',(o.location.x+.08,o.location.y-.10,o.location.z+.15),.08,.38,'glow',verts=5,r2=.005)
    for i in range(8):
        a=i*TAU/8
        ball('dust satellite particle',(math.cos(a)*.97,math.sin(a)*.75,.40+.13*(i%3)),(.04,.04,.045),'edge')


def capsule(spec):
    cyl('capsule foot',(0,0,.19),.74,.22,'dark')
    cyl('capsule foot bevel',(0,0,.35),.67,.20,'edge',r2=.53)
    cyl('quartz vacuum tube',(0,0,1.10),.48,1.31,'glass')
    for z in (.55,1.04,1.53):
        tor('superconducting magnetic band',(0,0,z),.55,.071,'copper')
        tor('contained energy seam',(0,0,z+.08),.49,.027,'glow')
    for i in range(6):
        a=i*TAU/6
        box('capsule protective strut',(.62*math.cos(a),.62*math.sin(a),1.07),(.14,.14,1.43),'ivory',.025)
    cyl('locking crown',(0,0,1.86),.68,.24,'paint')
    bolts((0,0,2.00),.53,8)
    tor('lifting eye',(0,0,2.2),.19,.055,'edge',(math.pi/2,0,0))
    box('danger plate',(0,-.69,1.01),(.50,.04,.44),'yellow',.018)
    label('AM',(-.19,-.716,.89),.25)
    box('capsule inspection viewport',(0,-.505,1.46),(.25,.02,.27),'glow',.015)


def ship(spec):
    base(3.2,4.0,spec['code'])
    box('folded platform cargo core',(0,.25,.94),(1.85,2.40,.83),'ivory',.13)
    box('starship dorsal spine',(0,.4,1.48),(.55,2.0,.31),'paint',.06)
    for x in (-1.25,1.25):
        box('folded platform sections',(x,.25,.91),(.44,2.9,.82),'dark',.06)
        for j in range(9):box('nested deck ribs',(x,-.93+j*.30,1.35),(.48,.07,.10),'edge',.01)
        cyl('compact engine',(x,-1.35,.87),.39,.87,'paint',(math.pi/2,0,0))
        tor('engine rim',(x,-1.81,.87),.37,.065,'edge',(math.pi/2,0,0))
        cyl('engine energized outlet',(x,-1.83,.87),.27,.015,'glow',(math.pi/2,0,0))
    for y in (-.58,.70):
        box('transport restraint',(0,y,1.40),(2.90,.13,.14),'copper',.02)
    for x in (-.55,.55):
        box('cargo hatch',(x,.10,1.41),(.57,1.25,.04),'iron',.02)
        bolts((x,.10,1.46),.20,6)
    box('navigation canopy',(0,1.2,1.33),(1.24,.45,.36),'glass',.10)
    box('navigation canopy glow',(0,1.43,1.31),(.85,.023,.11),'glow',.01)
    rod('folded antenna',(0,.9,1.64),(0,.9,2.26),.033)
    tor('docking hardpoint',(0,-.75,1.65),.27,.068,'edge')


def create_scene(name,spec):
    # Background factory startup only; never resets the user's live Blender scene.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    PARTS.clear();MOVERS.clear();palette(spec['color'])
    funcs={'lab':lab,'replicator':replicator,'collector':collector,'fusion':lambda s:drive(s),'antidrive':lambda s:drive(s,True),'foundry':foundry,'electro':electro,'bio':bio,'cryo':cryo,'dust':dust,'capsule':capsule,'ship':ship}
    funcs[spec['kind']](spec)
    panel_names={'magnet buttress','casting pillar','electrical switchgear','heat pump housing','folded platform cargo core','sealed research console','filter housing'}
    for panel in list(PARTS):
        if panel.name.split('.')[0] not in panel_names:continue
        x,y,z=panel.location;w,d,h=panel.dimensions
        for dx in (-w*.34,w*.34):
            for dz in (-h*.34,h*.34):
                cyl('panel retaining screw',(x+dx,y-d/2-.029,z+dz),.035,.035,'edge',(math.pi/2,0,0),6)
        box('panel recessed seam',(x,y-d/2-.012,z-h*.25),(w*.72,.014,.018),'dark',.003)
    root=bpy.data.objects.new('MODEL • '+name,None);bpy.context.collection.objects.link(root)
    for obj in PARTS:obj.parent=root
    scene=bpy.context.scene;scene.name=name
    scene['art_pipeline']='Interstellar Fleets original Blender art v2';scene['ground_units_per_tile']=1
    scene['asset_name']=name
    for frame in range(1,10):
        phase=(frame-1)*TAU/8
        for obj,mode,amount,loc,rot in MOVERS:
            obj.rotation_euler=rot
            obj.rotation_euler.z+=phase*amount
            obj.keyframe_insert(data_path='rotation_euler',frame=frame)
        for m,power in EMITTERS:
            p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            p.inputs['Emission Strength'].default_value=power*(.80+.20*math.cos(phase))
            p.inputs['Emission Strength'].keyframe_insert(data_path='default_value',frame=frame)
    scene.frame_start=1;scene.frame_end=8
    scene.render.film_transparent=True
    try:scene.render.engine='CYCLES'
    except TypeError as ex:raise RuntimeError(f'Cycles required: {ex}')
    scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.cycles.max_bounces=6
    scene.render.resolution_percentage=100
    enum(scene.render.image_settings,'file_format','PNG')
    enum(scene.render.image_settings,'color_mode','RGBA')
    enum(scene.render.image_settings,'color_depth','8')
    enum(scene.view_settings,'view_transform','AgX')
    scene.view_settings.exposure=.05
    world=bpy.data.worlds.new('studio environment');scene.world=world;world.use_nodes=True
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.32,.36,.42,1);bg.inputs[1].default_value=.25
    for nm,pos,power,color,size in [('warm key',(-5,-7,10),1450,(1,.84,.64),5),('cool fill',(6,-1,6),500,(.62,.8,1),4),('rim light',(1,6,8),1300,(.83,.90,1),3)]:
        data=bpy.data.lights.new(nm,'AREA');data.energy=power;data.color=color;data.shape='DISK';data.size=size
        ob=bpy.data.objects.new(nm,data);scene.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
    ca=bpy.data.cameras.new('Orthographic art camera');enum(ca,'type','ORTHO')
    cam=bpy.data.objects.new('Orthographic art camera',ca);scene.collection.objects.link(cam);scene.camera=cam
    scene.frame_set(1)
    return scene,root


def camera(scene,pos,target,ortho,size):
    cam=scene.camera;cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=ortho
    scene.render.resolution_x=size;scene.render.resolution_y=size


def render(scene,path):
    path.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)


def emission_pass(scene,path):
    # Black surfaces retain occlusion; only actual emissive materials contribute.
    originals=[]
    for m in bpy.data.materials:
        if not m.use_nodes:continue
        nodes=m.node_tree.nodes;out=next((n for n in nodes if n.type=='OUTPUT_MATERIAL'),None)
        if not out:continue
        link=next((l for l in m.node_tree.links if l.to_node==out and l.to_socket.name=='Surface'),None)
        if not link:continue
        originals.append((m,link.from_socket,out))
        em=nodes.new('ShaderNodeEmission');em.name='PASS_TEMP'
        p=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
        em.inputs['Color'].default_value=p.inputs['Emission Color'].default_value if m.get('emissive') else (0,0,0,1)
        em.inputs['Strength'].default_value=p.inputs['Emission Strength'].default_value if m.get('emissive') else 0
        m.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
    render(scene,path)
    for m,socket,out in originals:
        m.node_tree.nodes.remove(m.node_tree.nodes['PASS_TEMP']);m.node_tree.links.new(socket,out.inputs['Surface'])


def shadow_pass(scene,path):
    # Geometrically project the evaluated model from a fixed NW sun onto its deck.
    # All moving meshes and curved hoses participate; no alpha blob approximation.
    deps=bpy.context.evaluated_depsgraph_get();vertices=[];faces=[]
    for obj in PARTS:
        if obj.type not in {'MESH','CURVE','FONT'}:continue
        ev=obj.evaluated_get(deps);mesh=ev.to_mesh()
        offset=len(vertices)
        for v in mesh.vertices:
            p=ev.matrix_world@v.co;vertices.append((p.x+.50*p.z,p.y+.70*p.z,.015))
        for p in mesh.polygons:faces.append(tuple(i+offset for i in p.vertices))
        ev.to_mesh_clear()
    me=bpy.data.meshes.new('projected shadow');me.from_pydata(vertices,[],faces);me.update()
    ob=bpy.data.objects.new('projected shadow',me);scene.collection.objects.link(ob)
    m=bpy.data.materials.new('shadow pass');m.use_nodes=True
    nodes=m.node_tree.nodes;out=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');e=nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(0,0,0,1);e.inputs[1].default_value=0;m.node_tree.links.new(e.outputs[0],out.inputs[0]);me.materials.append(m)
    for obj in PARTS:obj.hide_render=True
    render(scene,path)
    for obj in PARTS:obj.hide_render=False
    bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me);bpy.data.materials.remove(m)


def load_scene(name):
    """Render an artist-edited source without rebuilding or overwriting geometry."""
    path=ROOT/'art/models'/f'{name}.blend'
    if not path.is_file():
        raise FileNotFoundError(path)
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    scene=bpy.context.scene
    root=next((o for o in scene.objects if o.name.startswith('MODEL • ')),None)
    if root is None:
        raise RuntimeError(f'{path} must retain its MODEL root object')
    PARTS.clear();MOVERS.clear();EMITTERS.clear()
    PARTS.extend(o for o in root.children_recursive if o.type in {'MESH','CURVE','FONT'})
    for m in bpy.data.materials:
        if m.use_nodes and m.get('emissive'):
            p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            EMITTERS.append((m,p.inputs['Emission Strength'].default_value))
    scene.frame_set(1)
    return scene,root


def main():
    args=argparse.ArgumentParser();args.add_argument('--asset',default='all');args.add_argument('--hero-only',action='store_true');args.add_argument('--samples',type=int,default=32)
    args.add_argument('--from-blend',action='store_true',help='Render saved artist-edited models instead of rebuilding geometry')
    opt=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    names=list(ASSETS) if opt.asset=='all' else opt.asset.split(',')
    (ROOT/'art/models').mkdir(parents=True,exist_ok=True)
    (ROOT/'art/render-manifest.json').write_text(json.dumps({'schema_version':2,'assets':ASSETS},indent=2)+'\n')
    for name in names:
        spec=ASSETS[name];scene,root=load_scene(name) if opt.from_blend else create_scene(name,spec);scene.cycles.samples=opt.samples
        size=spec['tiles'];hero_ortho=size*1.55+1.0
        camera(scene,(8,-11,10),(0,0,1.1),hero_ortho,1024)
        scene['sprite_projection']='camera 45 degrees; model Y multiplied sqrt(2); fixed target/origin'
        if not opt.from_blend:
            bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/models'/f'{name}.blend'),compress=True)
        render(scene,OUT/name/'hero.png')
        is_machine=spec['kind'] not in {'dust','capsule','ship'}
        ortho=size+4.2 if spec['kind'] not in {'fusion','antidrive'} else 9.3
        target_z=1.05
        metadata=dict(width=512,height=512,frame_count=8,line_length=8,directions=4 if spec['kind']=='collector' else 1,
                      scale=ortho*32/512,shift=[0,-target_z/math.sqrt(2)],mesh_count=sum(o.type=='MESH' for o in PARTS),
                      model=f'art/models/{name}.blend',sample=f'art/samples/{name}.png')
        (OUT/name/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
        if opt.hero_only or not is_machine:continue
        projection=bpy.data.objects.new('ground projection correction',None)
        scene.collection.objects.link(projection)
        projection.scale.y=math.sqrt(2)
        root.parent=projection
        camera(scene,(0,-12+0,12+target_z),(0,0,target_z),ortho,512)
        for direction in range(metadata['directions']):
            root.rotation_euler.z=(math.pi if spec['kind']=='collector' else 0)-direction*math.pi/2
            directory=OUT/name/f'direction_{direction}'
            for f in range(8):
                scene.frame_set(f+1)
                powers=[]
                for material,power in EMITTERS:
                    node=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
                    powers.append((node,node.inputs['Emission Strength'].default_value))
                    node.inputs['Emission Strength'].default_value=0
                render(scene,directory/f'frame_{f}.png')
                for node,power in powers:
                    node.inputs['Emission Strength'].default_value=power
                emission_pass(scene,directory/f'glow_{f}.png')
                shadow_pass(scene,directory/f'shadow_{f}.png')
        print(f'ASSET COMPLETE: {name}',flush=True)

if __name__=='__main__':main()
