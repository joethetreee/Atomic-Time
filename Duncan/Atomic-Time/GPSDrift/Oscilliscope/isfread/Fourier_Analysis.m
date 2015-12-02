filename = 'combined_triggerSerial.csv';
data = csvread(filename);

t=data(1:end,1);
serialAvg_t=data(1:end,3);
pulseAvg_t=data(1:end,2);
square_t=t;

% make square wave
disp(length(t));
for i = 1:length(t)
    if (t(i)<0.05)
        square_t(i)=1;
    else
        square_t(i)=0;
    end
end
plot(t,square_t);

t_tot=1.0;                      % time span of data
freq_s=t_tot/length(t);         % sampling frequency

t=t*t_tot/t(end);

pulseAvg_f=fft(pulseAvg_t);
square_f=fft(square_t);
f=(0:length(t)-1)/(t(2)-t(1));

pulse_f=pulseAvg_f;
for i = 1:length(t)
    pulse_f(i)=pulseAvg_f(i)/square_f(i);
end

pulse_t=fft(pulse_f);

plot(t,abs(pulse_t));