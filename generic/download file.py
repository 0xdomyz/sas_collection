import saspy

sas = saspy.SASsession()

# Download from SAS server to local machine
sas.download(
    sasfile="/path/on/sas/server/myfile.xlsx",
    localfile="C:/Users/dominic/Downloads/myfile.xlsx"
)