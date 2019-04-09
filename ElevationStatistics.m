% find study elevation range
%
% ElevationStatistics.m
% Created by Mac McMahan
% Last edited 4 Nov 2018
%
% Takes in data tables created by ArcMap Model and locates elevation bands
% which contain streams in all 3 rock types.  It first separates the files
% into matrices grouped by rock type.  From there hypsometric curves for
% each geographic group are calculated showing the overlap of the three
% rock types from each group.  The hypsometries are multiplied by each
% other within groups to locate only the 10 meter elevation band where all
% three hypsometries overlap.  The latitude and longitude of points which
% fall into those elevation bands are then extracted, along with new unique
% object IDs and stream segment IDs.  The points are then exported as .csv
% files to be loaded back into ArcMap for additional processing.
%
%--------------------------------------------------------------------------

clear;
clc;
tic; 

%reads name data files
data=ls('DataTables/*.xls');
%finds number of data files
[m,~]=size(data);
%fix bin edges, all histograms comparable, 4500 to acoomodate Mt. Whitney
edges=0:10:4500;

%---loop over calcareous---
%initialize counter, used for allocation into new, smaller matrices
count=1;
dcount=1;
%preallocates calcareous matrix, made big enough to accept most datasets
dataCalc=zeros(1000,m);
%preallocate hypsometry matrix, large enough to accomodate Mt. Whitney
%bin numbers range from 0 to 450, *10 to get elevation range 0 m to 4500 m
hypCalc=zeros(450,(m/3));
for i=1:3:m-2
    %path and name of data files to read in
    fileIn=sprintf('DataTables/%s',data(i,:));
    %load in data file
    excel=xlsread(fileIn);
    %find dimensions of data file
    [r,~]=size(excel);
    %load elevation column from data file into elevCalc, only fills the
    %necessary cells, others left unaffected
    dataCalc((1:r),(dcount:dcount+4))=excel(:,(1:5));
    %claclulates hypsometric data without plotting
    hypCalc(:,count)=histcounts(excel(:,5),edges);
    %increment counter
    count=count+1;
    dcount=dcount+5;
    
end

%---loop over felsic---
count=1;
dcount=1;
dataFels=zeros(1000,m);
hypFels=zeros(450,(m/3));
for j=2:3:m-1
    fileIn=sprintf('DataTables/%s',data(j,:));
    excel=xlsread(fileIn);
    [r,~]=size(excel);
    dataFels((1:r),(dcount:dcount+4))=excel(:,(1:5));
    hypFels(:,count)=histcounts(excel(:,5),edges);
    count=count+1;
    dcount=dcount+5;  
end

%---loop over mafic---
count=1;
dcount=1;
dataMaf=zeros(1000,m);
hypMaf=zeros(450,(m/3));
for k=3:3:m
    fileIn=sprintf('DataTables/%s',data(k,:));
    excel=xlsread(fileIn);
    [r,~]=size(excel);
    dataMaf((1:r),(dcount:dcount+4))=excel(:,(1:5));
    hypMaf(:,count)=histcounts(excel(:,5),edges);
    count=count+1;
    dcount=dcount+5;  
end

%---plot histograms---
for q=1:m/3
   figure;
   %plots elevation values that are not equal to zero
   histogram(dataCalc(dataCalc(:,q*5)~=0,q*5),'BinWidth',10);
   hold on;
   histogram(dataFels(dataFels(:,q*5)~=0,q*5),'BinWidth',10);
   histogram(dataMaf(dataMaf(:,q*5)~=0,q*5),'BinWidth',10);
   %give each plot a unique title
   txt=sprintf('Group %d hypsometries',q);
   title(txt);
   xlabel('Elevation (m)');
   ylabel('Occurence of elevation (count)');
   %give each figure a unique name
   fgnm=sprintf('Group%02dHypsometries.png',q);
   %path to output folder 
   path='ElevationBands/';
   saveas(gcf,fullfile(path,fgnm),'png');
   hold off;
end

%---locate hypsometric intersections---
%multiply hypsometry against each other, only 3way intersect(int) remains
int=hypCalc.*hypFels.*hypMaf;
%finds where intersection is not 0
elevRaw=(int(:,:)>0);

%find index of non-zero values from elevRaw
Calc=zeros(100,3);
Fels=zeros(100,3);
Maf=zeros(100,3);
for h=1:m/3
    %test to see if suitable conditions exist
    num=sum(int(:,h));
    if num==0
        fprintf('Group %d: No suitable locations found.\n',h);        
    else
        elev=find(elevRaw(:,h));
        %linear index range and convert to meters ASL
        MinE=min(elev)*10;
        MaxE=max(elev)*10;
        fprintf('Group %d: Suitable conditions between %d m and %d m elevation.\n',h,MinE,MaxE);
        
        %clears variables for new iteration
        clear Calc;
        clear Fels;
        clear Maf;
        
        %locates xyz data from dataROCKTYPE in elevation range from above
        Calc(:,(1:5))= dataCalc(dataCalc(:,(h*5))>=MinE & dataCalc(:,(h*5))<=MaxE,(h*5-4:h*5));
        %finds max ObjectID and StreamID from current iteration
        OBM=max(Calc(:,1));
        IDM=max(Calc(:,2));
        Fels(:,(1:5))= dataFels(dataFels(:,(h*5))>=MinE & dataFels(:,(h*5))<=MaxE,(h*5-4:h*5));
        %adds existing max OBJECTID and StreamID to all new values, maintains uniqueness
        Fels(:,1)=Fels(:,1)+OBM;
        Fels(:,2)=Fels(:,2)+IDM;
        %finds new max ObjectID and Stream ID
        OBM=max(Fels(:,1));
        IDM=max(Fels(:,2));
        Maf(:,(1:5))= dataMaf(dataMaf(:,(h*5))>=MinE & dataMaf(:,(h*5))<=MaxE,(h*5-4:h*5));
        %maintaining ID uniqueness by adding previous max to everything
        Maf(:,1)=Maf(:,1)+OBM;
        Maf(:,2)=Maf(:,2)+IDM;
        %loads all xyz points into single matrix for output
        Group=[Calc;Fels;Maf];
    
        %saves unique filename as a string
        fnm=sprintf('Group%02d.csv',h);
        fileOut=fullfile(path,fnm);
        %creates new file
        fid=fopen(fileOut,'w');
        %print header to file
        fprintf(fid,'ObjectID,StreamID,Long,Lat,Elevation\n');
        %append file with data
        dlmwrite(fileOut,Group,'delimiter',',','-append','precision','%16.12f');
        %close file
        fclose(fid);
    end
end

toc;


