import os

os.chdir("outputsequences")

outputfile=open("output.txt", "wt")
metricsequences=[]
complexsequences=[]
bois=[]
for inputfilename in os.listdir(os.getcwd()):
    inputfile=open(inputfilename, "rt")
    someleft=True
    while someleft==True:
        s=inputfile.readline()
        if s=="":
            someleft=False
            inputfile.close()
            break
        metricsequences.append(s[:s.find(":")])
        complexsequences.append(s[s.find(":")+1:s.find(";")])
        bois.append(s[s.find(";")+1:s.find("\n")])
outputfile.write("Metric Simples\n\n")
for i in metricsequences:
    outputfile.write(i+"\n")
outputfile.write("\nComplexsequences\n\n")
for i in complexsequences:
    outputfile.write(i+"\n")
outputfile.write("\nBeats of Interest\n")
for i in bois:
    outputfile.write(i+"\n")

outputfile.close()
