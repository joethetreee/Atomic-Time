filename = 'CH2_triggerSerial';
data = isfread(strcat(filename,'.ISF'));
disp(data.header);
data2 = [data.x,data.y];
csvwrite(strcat(filename,'.csv'),data2);