# ----------------------------------------------
# Carme
# ----------------------------------------------
# carme_backend.py - the Carme Back End Server
#
# see Carme development guide for documentation:
# * Carme/Carme-Doc/DevelDoc/CarmeDevelopmentDocu.md
# * Carme/Carme-Doc/DevelDoc/BackendDocu.md
#
# Copyright 2019 by Fraunhofer ITWM
# License: http://open-carme.org/LICENSE.md
# Contact: info@open-carme.org
# ---------------------------------------------

import rpyc
from rpyc.utils.server import ThreadedServer
from rpyc.utils.authenticators import SSLAuthenticator
import ssl
import os
from ldap3 import *
import MySQLdb
import datetime

import imp
imp.load_source('CarmeConfig', '/opt/development/CarmeConfig')
from CarmeConfig import *


# to be replace by reading Carme Config
CARME_MATTERMOST_BIN = CARME_MATTERMOST_PATH+"/bin/"+CARME_MATTERMOST_COMMAND


"""
Carme Backend Server
See Carme/Carme-Doc/DevelDoc/BackendDocu.md for details.
"""
def setCarmeLog(message, level):
    """adds a message to Carme log files.

    # Arguments
        message: string message to be logged
        level: int log level (20=info, 30=warning, 10=debug, 40=error)

    """
    db = MySQLdb.connect(host=CARME_DB_NODE,  user=CARME_DB_USER,
                         passwd=CARME_DB_PW,  db=CARME_DB_DB)
    cur = db.cursor()
    ts = datetime.datetime.now()
    st = ts.strftime('%Y-%m-%d %H:%M:%S')
    sql = 'insert into `django_db_logger_statuslog` (logger_name, level, msg, trace, create_datetime) values ("db", "'+str(
        level)+'", "'+str(message)+'", "NULL","'+str(st)+'")'
    try:
        cur.execute(sql)
        db.commit()
    except:
        print("log fail")
        db.rollback()
    db.close()

def setMessage(message, user, color): 
    """adds a message to Carme.                                                                                                                                                                          

    # Arguments

        message: string message 
	user: username
	color: color of message                                                                                                                                                                        
    """     

    db = MySQLdb.connect(host=CARME_DB_NODE,  user=CARME_DB_USER,
                         passwd=CARME_DB_PW,  db=CARME_DB_DB)
    cur = db.cursor() 
    sql = 'insert into `carme-base_carmemessages` (user, message, color) values ("'+str(user)+'","'+str(message)+'","'+str(color)+'" )' 

    try:             
        cur.execute(sql) 
        db.commit()

    except:
        print("message fail")   
        db.rollback() 
    db.close()        

def sendMatterMostMessage(user, message):
    """sends Mattermost message to user

    # Arguments 
        user: recipiant
        message: string
    """
    com = '''curl -i -X POST --data-urlencode 'payload={\"channel\": \"@'''+str(
        user)+'''\",\"text\": \" '''+str(message)+'''\"}' ''' + str(CARME_MATTERMOST_WEBHOCK_2)
    setCarmeLog("MATTERMOST: "+str(user)+" "+str(message), 20)
    return os.system(com)


def checkUserJob(user, jobname):
    """ checks if a user owns the given job

    # Arguments
        user: job owner
        jobname: slurm job name
    # Returns
        ok or error message

    """
    db = MySQLdb.connect(host=CARME_DB_NODE,  user=CARME_DB_USER,
            passwd=CARME_DB_PW,  db=CARME_DB_DB)
    cur = db.cursor()
    sql = 'select * from `carme-base_slurmjobs` where (user="'+str(user)+'" and jobName="'+str(jobname)+'");'
    res=0
    try:
        cur.execute(sql)
        selections= cur.fetchall()
        res= len(selections) #is there an entry?
    except:
        print("SQL error")
        db.rollback()
        return "SQL ERROR"

    db.close()
    
    if res !=1:
        return "ERROR: job "+jobname+ "does not belong to user "+user
    else:
        return "ok"

def checkUserJobID(user, jobid):  
    """ checks if a user owns the given job by slurm ID

    # Arguments
        user: job owner  
        jobid: db job id  

    # Returns
        ok or error message  
    """ 

    db = MySQLdb.connect(host=CARME_DB_NODE,  user=CARME_DB_USER,  
            passwd=CARME_DB_PW,  db=CARME_DB_DB)  
    cur = db.cursor()  
    sql = 'select * from `carme-base_slurmjobs` where (user="'+str(user)+'" and id="'+str(jobid)+'");'   
    print (sql)
    res=0

    try:
        cur.execute(sql)  
        selections= cur.fetchall()  
        res= len(selections) #is there an entry? 
    except:
        print("SQL error")  
        db.rollback()  
        return "SQL ERROR" 
    db.close()     

    if res !=1:  
        return "ERROR: job "+jobid+ "does not belong to user "+user  
    else:   
        return "ok"                           

def checkUserSlurmID(user, SLURM_ID):
    """ checks if a user owns the given job by slurm ID  

    # Arguments 
        user: job owner  
        SLURM_ID: job SLURM_ID

    # Returns
        ok or error message    
    """ 

    db = MySQLdb.connect(host=CARME_DB_NODE,  user=CARME_DB_USER,   
            passwd=CARME_DB_PW,  db=CARME_DB_DB) 
    cur = db.cursor() 
    sql = 'select * from `carme-base_slurmjobs` where (user="'+str(user)+'" and SLURM_ID="'+str(SLURM_ID)+'");'
    print (sql)   
    res=0 

    try: 
        cur.execute(sql)  
        selections= cur.fetchall()  
        res= len(selections) #is there an entry?
    except:
        print("SQL error")  
        db.rollback() 
        return "SQL ERROR"
    db.close() 

    if res !=1: 
        return "ERROR: job "+jobid+ "does not belong to user "+user    
    else:   
        return "ok"                                          


class CarmeBackEndService(rpyc.Service):
    """ Carme backend server class

    # Note 
        only methods that are _exposed_ are callable via rpc
    """

    def __init__(self):
        self.myConnection = ''
        self.user = ''

    def on_connect(self, conn):
        """ method is automatically run at new rpc connections
        """
        self.myConnection = conn
        print (conn._config['credentials']['subject'])
        self.user = conn._config['credentials']['subject'][5][0][1]
        if CARME_BACKEND_DEBUG:
            print("new connection: ",
                  conn._config['endpoints'], "from user ", self.user)
            setCarmeLog("BACKEND: new connection from " + str(self.user), 10)
        pass

    def on_disconnect(self, conn):
        """method is automatically run when rpc connection is terminated
        """
        if CARME_BACKEND_DEBUG:
            print ("conn ended", conn._config['connid'])
            setCarmeLog("BACKEND: connection ended", 10)
        pass

    def exposed_ping(self):
        """simple ping for rpc connection testing
        """
        if CARME_BACKEND_DEBUG:
            print ("ping")
            setCarmeLog("BACKEND: ping", 10)
        return 'pong'

    def exposed_whoami(self):
        """simple authentication check

        Note: auth will actually fail at on_connect()
        """
        return self.user

    def exposed_getFreeGpuOnHost(self, IP, numGPUs):
        """ returns the next n free GPUs on targert host

        # Arguments
            IP: ip adress of target host
            numGPUs: number of GPUs to allocate
        """
        possible_GPUs=[]
        for i in range(0,CARME_SYSTEM_GPUS_PER_NODE):
            possible_GPUs.append(str(i))
        db = MySQLdb.connect(host=CARME_DB_NODE,  user=CARME_DB_USER,
            	passwd=CARME_DB_PW,  db=CARME_DB_DB)
                                                                                                                                                                  
        cur = db.cursor()
        sql='select GPUS from `carme-base_slurmjobs` where IP="'+str(IP)+'";' 	

        try:
            cur.execute(sql)
            results = cur.fetchall()
            db.commit() 
        except: 
            print("SQL error")
            db.rollback()   
        db.close() 


        GPUS_used=[]
        for i in results: 
                GPUS_used.append(i[0])
        print(GPUS_used)
        print(possible_GPUs)
        print(numGPUs)
        res_list=list(set(possible_GPUs)-set(GPUS_used))[0:numGPUs]
        #make string   
        res=""  
                
        for i in res_list:
                res+=str(i)+"," 
                    
        if CARME_BACKEND_DEBUG:
            print ("Free GPUS: ", res[:-1]) 
        return res[:-1]

    def exposed_userAlterJobDB(self, IPADDR, HASH, NB_PORT, TB_PORT, SLURM_JOBID, URL, GPUS, DBJOBID ):
        """ updates job status after it has been started by the scheduler

        # Arguments
            IPADDR: master node IP
            HASH: job hash
            NB_PORT: jupyterlab port
            TB_PORT: tensorboard port
            SLURM_JOBID: job id
            URL: full URL
            GPUS: num of GPUs
            DBJOBID: db job key


        """

        #check if user owns job
        check=checkUserJobID(self.user, DBJOBID)
        if check!="ok":
            if CARME_BACKEND_DEBUG:
                print ("User auth failed")
            setCarmeLog("User auth failed on alter_job_db", 40)
            return check

        #alter db entry
        db = MySQLdb.connect(host=CARME_DB_NODE,  user=CARME_DB_USER,
                passwd=CARME_DB_PW,  db=CARME_DB_DB)
        cur = db.cursor()
        sql='update `carme-base_slurmjobs` set IP="'+str(IPADDR)+'", HASH="'+str(HASH)+'", NB_PORT='+str(NB_PORT)+',TB_PORT='+str(TB_PORT)+',status="ready",SLURM_ID='+str(SLURM_JOBID)+',URL="'+str(URL)+'",GPUS="'+str(GPUS)+'",  EntryNode="'+str(IPADDR)+'" where id='+str(DBJOBID)+';'
        
        try:
            cur.execute(sql) 
            db.commit()  
        except: 
            if CARME_BACKEND_DEBUG:
                print("SQL error", sql)
            setCarmeLog("SQL error", 40)
            db.rollback() 
        db.close()

        return "ok"



    def exposed_userTerminateJob(self, jobUser, jobName):
        """ allows users to terminate running jobs

        #Arguments
            jobUser
            JobName
        """
        #check user auth
        if self.user!=jobUser:
            message="Error: User "+jobUser+" tried to terminate job of user "+self.user
            if CARME_BACKEND_DEBUG:
                print ("message")
            setCarmeLog(message, 40)
            return message

        #check if user owns job
        check=checkUserJob(jobUser, jobName)

        #terminate jom
        if check!="ok":
            return check
        com = 'scancel -n '+str(jobName)

        ret = os.system(com)  

        if ret == 0:  
            setCarmeLog("BACKEND: Job " + str(jobName) +
                        " terminated by user API.", 20) 
            setMessage("Terminating job " + str(jobName), str(jobUser), "tomato")
            sendMatterMostMessage(  
                jobUser, "Job " + str(jobName) + " terminated by user API.")
        else:       
            setMessage("FAILED Terminating job " + str(jobName), str(jobUser), "red")   
            sendMatterMostMessage( 
                jobUser, "terminating job " + str(jobName) + " FAILED! - Contact your admin.")
            sendMatterMostMessage("admin", "terminating job " + str(jobName) +
                                  " for user " + str(jobUser) + "FAILED! check Django logs.")            
        #remove job from db
        db = MySQLdb.connect(host=CARME_DB_NODE,  user=CARME_DB_USER,
                passwd=CARME_DB_PW,  db=CARME_DB_DB)

        cur = db.cursor() 
        sql='delete from `carme-base_slurmjobs` where jobName="'+str(jobName)+'";'
        try:
            cur.execute(sql) 
            db.commit()
        except:
            db.rollback()
            db.close()
            return "Error: SQL FAIL!"
        db.close()           
                                                                                                                                                                                           

        return ret                                                          


    def exposed_StartJob(self, jobUser, jobID, jobImage, jobMounts, jobPartition, jobNumGPUs, jobNumNodes, jobName):
        """
        Tells the batch-system to schedule a new job

        # NOTE 
            only requests from the frontend are exepted

        # Arguments
            jobUser: username
            jobID: frontend job id 
            jobImage: image to start
            jobMounts: mount points to be set
            jobPartition: partition to be used
            jobNumGPUs: number of GPUs to be used
            jobNumNodes: number of nodes
            jobName: name string (NOTE: must be unique)
        """
        if self.user != "frontend":
            setCarmeLog("BACKEND: AUTH FAILED", 40)
            return "Auth Failed"

        print("start job ", CARME_SCRIPT_PATH) 
        com = 'runuser -l '+str(jobUser)+' '+str(CARME_BACKEND_PATH)+'/Bash/submitJob.sh '+str(CARME_SCRIPT_PATH)+' '+str(jobID)+' '+str(
            jobImage)+' '+str(jobMounts)+' '+str(jobPartition)+' '+str(jobNumGPUs)+' '+str(jobNumNodes)+' '+str(jobName)+' '+str(CARME_SCRIPT_PATH)
        if CARME_BACKEND_DEBUG:
            print (com)
            setCarmeLog("BACKEND: "+str(com), 10)
        ret = os.system(com)
        if ret == 0:
            sendMatterMostMessage(
                jobUser, "Job " + str(jobName) + " has been schedued for execution")
            setMessage("Job " + str(jobName) + " scheduled", str(jobUser), "yellow") 
        else:
            sendMatterMostMessage(
                jobUser, "scheduling job " + str(jobName) + " FAILED! - Contact your admin.")
            sendMatterMostMessage("admin", "scheduling job " + str(jobName) +
                                  " for user " + str(jobUser) + "FAILED! check Django logs.")
        return ret

    def exposed_StopJob(self, jobName, jobUser):
        """
        Tells the batch system to terminate a job

        # NOTE
            only requests from the frontend are exepted

        # Arguments
            jobName: name string of the job
            jobUser: username of job owner 
        """
        if self.user != "frontend":
            setCarmeLog("BACKEND: AUTH FAILED", 40)
            return "Auth Failed"
        if CARME_BACKEND_DEBUG:
            print("Stop job: ", str(jobName))
        com = 'scancel -n '+str(jobName)

        ret = os.system(com)
        if ret == 0:
            setCarmeLog("BACKEND: Job " + str(jobName) +
                        " terminated by user.", 20)
            setMessage("Terminating job " + str(jobName), str(jobUser), "tomato")
            sendMatterMostMessage(
                jobUser, "Job " + str(jobName) + " terminated by user.")
        else:
            setMessage("FAILED Terminating job " + str(jobName), str(jobUser), "red")
            sendMatterMostMessage(
                jobUser, "terminating job " + str(jobName) + " FAILED! - Contact your admin.")
            sendMatterMostMessage("admin", "terminating job " + str(jobName) +
                                  " for user " + str(jobUser) + "FAILED! check Django logs.")

        return ret

    def exposed_SetTrigger(self, jobSlurmID, jobUser, jobName):                              
        """ 
        sets batch system trigger for running job  
        # NOTE  
            only requests from the frontend are exepted 
        # Arguments   
            jobSlurmID: batch system job id   
            jobUser: username  
            jobName: name string of the job   
        """   
        print("TRIGGER") 
                                                                                                                                                                                         
        if self.user != "frontend":      
            setCarmeLog("BACKEND: AUTH FAILED", 40)  
            print ("AUTH FAILED")
            return "Auth Failed" 

        sendMatterMostMessage(                                                                                                                                                                                 
                jobUser, "Job "+str(jobName)+" (ID: " + str(jobSlurmID) + ") Started!")  
                                                                                                                        
        setMessage("Starting job " + str(jobName), str(jobUser), "green") 
        
        print ("TRIGGER DONE")  
 
        return 0
        
    def exposed_SendNotify(self, message, user, color):
        sendMatterMostMessage(user, message)
        setMessage(message, user, color)

    def exposed_SendMessage(self, user, message):
        """
        sends Mattermoste message

        # Arguments
            user: recipiant user name
            message: string
        """
        return sendMatterMostMessage(user, message)

    def exposed_SetPassword(self, user, user_name, password):
        """
        sets LDAP user password

        # NOTE
            only requests from the frontend are exepted

        # Arguments
            user: LDAP user ID
            user_name: user name string
            password: new password to be set

        """
        if self.user != "frontend":
            setCarmeLog("BACKEND: AUTH FAILED", 40)
            return "Auth Failed"
        ret = 0  # fail by default
        # LDAP
        try:
            # define an unsecure LDAP server, requesting info on DSE and schema
            s = Server(CARME_LDAP_SERVER_IP, get_info=ALL)
            c = Connection(s, user='cn=admin,dc=carme,dc=local',
                           password=CARME_LDAP_SERVER_PW)
            c.bind()
            c.modify(user, {'userPassword': [(MODIFY_REPLACE, password)]})
            c.unbind()
            setCarmeLog("BACKEND: password changed for " + str(user), 10)
            ret = 1
        except:
            setCarmeLog("BACKEND: LDAP ERROR", 40)
            return 0
        # Mattermost
        com = "cd "+str(CARME_MATTERMOST_PATH)+"/bin/; "+"./"+CARME_MATTERMOST_COMMAND+ " user password " + \
            str(user_name) + " '" + str(password) + "'"
        print(com)
        oscall = os.system(com)
        if oscall != 0:
            ret = 0
            setCarmeLog("MATTERMOST: chpwd ERROR", 40)
        else:
            setCarmeLog("MATTERMOST: password changed for " + str(user), 10)
        return ret


if __name__ == "__main__":
    print("Came Backend up, using ", CARME_SCRIPT_PATH)
    setCarmeLog("Came Backend started", 10)
    auth = SSLAuthenticator(str(CARME_BACKEND_PATH)+"SSL/backend.key", str(CARME_BACKEND_PATH) +
                            "SSL/backend.crt", cert_reqs=ssl.CERT_REQUIRED, ca_certs=str(CARME_BACKEND_PATH)+"SSL/backend.crt")
    server = ThreadedServer(CarmeBackEndService, port=CARME_BACKEND_PORT,
                            authenticator=auth, protocol_config={'allow_all_attrs': True})
    server.start()
