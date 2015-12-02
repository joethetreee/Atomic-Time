filename = 'T0001CH2';
data = isfread(strcat(filename,'.ISF'));
disp(data);
data2 = [data(1).x,data(1).y]
csvwrite(strcat(filename,'.csv'),data2);