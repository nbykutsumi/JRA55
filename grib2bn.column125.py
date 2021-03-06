from numpy import *
import calendar
import subprocess
import os, sys, socket

iyear    = 1979
eyear    = 1979
#lyear    = range(iyear,eyear+1)
lyear    = range(eyear,iyear-1,-1)
#lmon     = [12]
lmon     = arange(1,12+1)
#lmon     = arange(4,12+1)
tstp     = "6hr"
singleday   = False  # True or False
miss_out    = -9999.0
stype  = "anl_column125"
lvar   = ["PWAT"]
res    = "145x288"
#--- LAT & LON & NX, NY : Original  ------------------------------
dlat_org      = 1.25
dlon_org      = 1.25

lat_first_org = -90.0
lat_last_org  = 90.0
lon_first_org = 0.0
lon_last_org  = 360.0 - 1.25
a1lat_org     = arange(lat_first_org, lat_last_org + dlat_org*0.1, dlat_org)  
#-----------
a1lon_org     = arange(lon_first_org, lon_last_org + dlon_org*0.1, dlon_org)

#-----------
def mk_dir(sdir):
  try:
    os.makedirs(sdir)
  except:
    pass

#---------------------------------------------------------------
ny_org     = len(a1lat_org)
nx_org     = len(a1lon_org)
nz_org     = 1
print ny_org, nx_org


#********************************************
#********************************************
for year in lyear:
  for mon in lmon:
    for var in lvar:
      #-- check host --
      hostname = socket.gethostname()
      if hostname == "well":
        #idir      =  "/mnt/mizu.tank/utsumi/JRA55/Daily/%s/%04d%02d"%(stype,year,mon)
        #idir      =  "/media/disk2/data/JRA55/grib/%s/%04d%02d"%(stype,year,mon)
        odir_root =  "/media/disk2/data/JRA55/%s.%s/%s"%(res, stype, tstp)
      elif hostname in ["mizu","naam"]:
        idir      =  "/data2/JRA55/Hist/Daily/%s/%04d%02d"%(stype,year,mon)
        odir_root =  "/tank/utsumi/data/JRA55/%s.%s/%s"%(res, stype, tstp)
      #----------------
      ctlname   = idir + "/%s.ctl"%(stype)

      odir_temp = odir_root  +  "/%s"%(var)
      odir      = odir_temp  +  "/%04d/%02d"%(year, mon)
      odir_meta = "/".join(odir_root.split("/"))
      #-- make directory ---
      mk_dir(odir_root)
      mk_dir(odir_temp)
      mk_dir(odir)
      print odir    
    
      #-- discription file ----------------
      #< dims >
      sout   = "lev %d\nlat %d\nlon %d"%(nz_org, ny_org, nx_org)
      f      = open( odir_meta + "/dims.txt", "w")
      f.write(sout)
      f.close()
    
      #< lat >
      sout   = "\n".join(map( str, a1lat_org))
      f      = open( odir_meta + "/lat.txt", "w")
      f.write(sout)
      f.close()
    
      #< lon >
      sout   = "\n".join(map( str, a1lon_org))
      f      = open( odir_meta + "/lon.txt", "w")
      f.write(sout)
      f.close()
    
      #< dump >
      tempname = idir + "/%s.%04d%02d0100"%(stype, year, mon)
      dumpname = odir_meta + "/dump.txt"
    
      ptemp  = subprocess.call("wgrib -V %s | grep -A 6 %s > %s"%(tempname, var.upper(), dumpname), shell=True)
      #  
      #---------
      eday  = calendar.monthrange(year, mon)[1]
      if singleday == True:
        eday   = 1
      #-----------------
      for day in range(1, eday+1):
        #---
        if singleday == True:
          print "*****************"
          print "   single day !!"
          print "*****************"
        #---
        print year, mon, day 
        for hour in [0, 6, 12, 18]:
          stime     = "%04d%02d%02d%02d"%(year, mon, day, hour)
          #----- Names ------------
          gribname  = idir + "/%s.%s"%(stype, stime)
          oname     = odir + "/%s.%s.%s.%s"%(stype, var, stime, res)
    
          print gribname
          if not os.access(gribname, os.F_OK): 
            print "no file"
            print gribname
            sys.exit()
          #-- grib --> binary -----
    
          args      = "wgrib %s | grep %s | wgrib %s -i -nh -o %s"%(gribname, var.upper(), gribname, oname)
           
          ptemp     = subprocess.call(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
           
          #-- Flipud --------
          a2org     = flipud(fromfile(oname, float32).reshape(ny_org, nx_org))
          #
          a2org.tofile( oname ) 
          print oname
    

