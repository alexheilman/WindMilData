clear all 
clc

T = 0.0001;
t = 0:T:0.05;
harmonic = 1;

x1 = sin(2*pi*60*harmonic*t);
x2 = sin(2*pi*60*harmonic*t + (2/3)*pi);
x3 = sin(2*pi*60*harmonic*t + (4/3)*pi);
x_sum = x1+x2+x3;

figure
subplot(211);
hold on;
plot(t,x1);
plot(t,x2);
plot(t,x3);
hold off
subplot(212);
plot(t,x_sum);
ylim([-1 1]);
