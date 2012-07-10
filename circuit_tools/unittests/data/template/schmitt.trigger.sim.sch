v 20110115 2
C 40000 40000 0 0 0 title-B.sym
C 47800 44900 1 0 0 dual-opamp-1.sym
{
T 48000 47200 5 10 0 0 0 0 1
device=DUAL_OPAMP
T 48000 45800 5 10 1 1 0 0 1
refdes=X1
T 48600 45600 5 10 0 1 0 0 1
footprint=SO8
T 48000 47400 5 10 0 0 0 0 1
symversion=0.2
T 48600 46000 5 10 1 1 0 0 1
manufacturer=Microchip
T 48600 45800 5 10 0 1 0 0 1
part-number=MCP6002-I/SN
T 48600 45700 5 10 1 0 0 0 1
model-name=MCP6001
}
C 46200 43900 1 90 0 resistor-2.sym
{
T 45850 44300 5 10 0 0 90 0 1
device=RESISTOR
T 45900 44600 5 10 1 1 180 0 1
refdes=R2
T 45600 44100 5 10 1 1 0 0 1
value=10k
T 46300 44100 5 10 0 1 0 0 1
footprint=0603
T 46300 44500 5 10 0 1 0 0 1
manufacturer=Panasonic
T 46300 44300 5 10 0 1 0 0 1
part-number=ERJ-3GEYJ103V
}
C 48100 45700 1 0 0 vcc-1.sym
C 47000 50200 1 0 0 vcc-1.sym
C 48200 44600 1 0 0 gnd-1.sym
C 47100 48700 1 0 0 gnd-1.sym
C 52300 42100 1 0 0 gnd-1.sym
C 51000 45100 1 0 0 nmos-3.sym
{
T 51600 45600 5 10 0 0 0 0 1
device=NMOS_TRANSISTOR
T 51700 45700 5 10 1 1 0 0 1
refdes=X1
T 51700 45500 5 10 0 1 0 0 1
manufacturer=Vishay Siliconix
T 51700 45100 5 10 0 1 0 0 1
footprint=SOT_23_3
T 51700 45300 5 10 0 1 0 0 1
part-number=SI2302ADS-T1-E3
T 51600 45100 5 10 1 0 0 0 1
model-name=Si2301CDS
}
C 45900 47700 1 0 0 vcc-1.sym
C 46000 43600 1 0 0 gnd-1.sym
C 51600 46400 1 90 0 resistor-2.sym
{
T 51250 46800 5 10 0 0 90 0 1
device=RESISTOR
T 51300 47000 5 10 1 1 180 0 1
refdes=R5
T 51100 46600 5 10 1 1 0 0 1
value=10
T 51700 47000 5 10 0 1 0 0 1
manufacturer=Stackpole Electronics
T 51700 46800 5 10 0 1 0 0 1
part-number=RHC2512FT10R0
T 51700 46600 5 10 0 1 0 0 1
footprint=2512
}
C 51300 47600 1 0 0 vcc-1.sym
N 46100 46800 46100 46300 4
N 46100 45400 46100 44800 4
C 47700 47300 1 270 0 input-2.sym
{
T 47900 47300 5 10 0 0 270 0 1
net=in:1
T 48400 46700 5 10 0 0 270 0 1
device=none
T 47800 46900 5 10 1 1 0 7 1
value=in
}
N 46100 45100 47800 45100 4
N 47900 43800 47300 43800 4
N 47300 43800 47300 45100 4
N 48800 43800 49100 43800 4
N 50000 43800 50000 45300 4
N 48800 45300 51000 45300 4
N 52400 44500 52400 44900 4
N 51500 44900 52400 44900 4
N 51500 45100 51500 44900 4
N 51500 45900 51500 46400 4
N 51500 47600 51500 47300 4
C 46200 46800 1 90 0 resistor-2.sym
{
T 45850 47200 5 10 0 0 90 0 1
device=RESISTOR
T 45900 47500 5 10 1 1 180 0 1
refdes=R6
T 45600 47000 5 10 1 1 0 0 1
value=10k
T 46300 47000 5 10 0 1 0 0 1
footprint=0603
T 46300 47400 5 10 0 1 0 0 1
manufacturer=Panasonic
T 46300 47200 5 10 0 1 0 0 1
part-number=ERJ-3GEYJ103V
}
C 48800 43900 1 180 0 resistor-2.sym
{
T 48400 43550 5 10 0 0 180 0 1
device=RESISTOR
T 47900 44000 5 10 1 1 0 0 1
refdes=R7
T 48800 44100 5 10 1 1 180 0 1
value=10k
T 48500 43200 5 10 0 1 180 0 1
footprint=0603
T 48900 43600 5 10 0 1 180 0 1
manufacturer=Panasonic
T 49500 43400 5 10 0 1 180 0 1
part-number=ERJ-3GEYJ103V
}
N 47800 45900 47800 45500 4
T 40700 42600 9 10 1 0 0 0 1
Connector Types
T 40700 42000 9 10 1 0 0 0 2
2 pin, smd, right angle, shrouded header: JST S2B-PH-SM4-TB
Mates with wire connector: JST PHR-2
T 48400 47900 9 10 1 0 0 0 2
Add additional resistance here 
to reduce diode current
C 46900 49000 1 0 0 vdc-1.sym
{
T 47600 49650 5 10 1 1 0 0 1
refdes=VBATT
T 47600 49850 5 10 0 0 0 0 1
device=VOLTAGE_SOURCE
T 47600 50050 5 10 0 0 0 0 1
footprint=none
T 47600 49450 5 10 1 1 0 0 1
value=DC 3.6V
}
C 41900 45000 1 0 0 vac-1.sym
{
T 42600 45650 5 10 1 1 0 0 1
refdes=Vin
T 42600 45850 5 10 0 0 0 0 1
device=vac
T 42600 46050 5 10 0 0 0 0 1
footprint=none
T 42600 45150 5 10 1 1 0 0 1
value=dc 1.8 ac SIN(1.8 0 40Hz)
}
C 42100 44700 1 0 0 gnd-1.sym
C 42100 47600 1 270 0 input-2.sym
{
T 42300 47600 5 10 0 0 270 0 1
net=in:1
T 42800 47000 5 10 0 0 270 0 1
device=none
T 42200 47200 5 10 1 1 0 7 1
value=in
}
C 46200 45400 1 90 0 resistor-2.sym
{
T 45850 45800 5 10 0 0 90 0 1
device=RESISTOR
T 45900 46100 5 10 1 1 180 0 1
refdes=Rvar1
T 45300 45600 5 10 1 1 0 0 1
value=$Rvar1
T 46300 45600 5 10 0 1 0 0 1
footprint=0603
T 46300 46000 5 10 0 1 0 0 1
manufacturer=Panasonic
T 46300 45800 5 10 0 1 0 0 1
part-number=ERJ-3GEYJ103V
}
C 50000 43900 1 180 0 resistor-2.sym
{
T 49600 43550 5 10 0 0 180 0 1
device=RESISTOR
T 49100 43400 5 10 1 1 0 0 1
refdes=Rvar2
T 50300 43500 5 10 1 1 180 0 1
value=$Rvar2
T 49800 44000 5 10 0 1 90 0 1
footprint=0603
T 49400 44000 5 10 0 1 90 0 1
manufacturer=Panasonic
T 49600 44000 5 10 0 1 90 0 1
part-number=ERJ-3GEYJ103V
}
C 41200 49800 1 0 0 spice-include-1.sym
{
T 41300 50100 5 10 0 1 0 0 1
device=include
T 41300 50200 5 10 1 1 0 0 1
refdes=A1
T 41700 49900 5 10 1 1 0 0 1
file=./models/MCP6001.txt
}
C 41200 49100 1 0 0 spice-include-1.sym
{
T 41300 49400 5 10 0 1 0 0 1
device=include
T 41300 49500 5 10 1 1 0 0 1
refdes=A2
T 41700 49200 5 10 1 1 0 0 1
file=./models/si2302ads.lib
}
C 41200 48300 1 0 0 spice-include-1.sym
{
T 41300 48600 5 10 0 1 0 0 1
device=include
T 41300 48700 5 10 1 1 0 0 1
refdes=A3
T 41700 48400 5 10 1 1 0 0 1
file=./sim.cmd
}
C 41200 47600 1 0 0 spice-include-1.sym
{
T 41300 47900 5 10 0 1 0 0 1
device=include
T 41300 48000 5 10 1 1 0 0 1
refdes=A4
T 41700 47700 5 10 1 1 0 0 1
file=./models/leds.lib
}
C 52600 43600 1 90 0 led-3.sym
{
T 51950 44550 5 10 0 0 90 0 1
device=LED
T 52950 44150 5 10 1 1 180 0 1
refdes=X1
T 52600 43600 5 10 1 0 0 0 1
model-name=LuxStar-1watt
}
C 53800 44600 1 180 0 input-2.sym
{
T 53800 44400 5 10 0 0 180 0 1
net=led_out:1
T 53200 43900 5 10 0 0 180 0 1
device=none
T 53400 44500 5 10 1 1 270 7 1
value=led_out
}
C 50800 43900 1 90 0 input-2.sym
{
T 50600 43900 5 10 0 0 90 0 1
net=trigger_out:1
T 50100 44500 5 10 0 0 90 0 1
device=none
T 50700 44300 5 10 1 1 180 7 1
value=trigger_out
}
C 52100 42400 1 0 0 vdc-1.sym
{
T 52800 43050 5 10 1 1 0 0 1
refdes=VLED
T 52800 43250 5 10 0 0 0 0 1
device=VOLTAGE_SOURCE
T 52800 43450 5 10 0 0 0 0 1
footprint=none
T 52800 42850 5 10 1 1 0 0 1
value=DC 0V
}
