;Control file for schmitt trigger
.CONTROL
tran 1m 100ms
meas tran ltp find v(in) when v(out)=0.5 rise=1
meas tran utp find v(in) when v(out)=0.5 fall=1
write results.raw v(in) v(out) utp ltp
.ENDC
.PRINT utp ltp
