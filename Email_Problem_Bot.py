#!/usr/bin/env python
#sends either txt or png in email to listed users

import smtplib
import os
import yaml
import random
from email.mime.image     import MIMEImage
from email.mime.text      import MIMEText
from email.mime.multipart import MIMEMultipart

CONFIGFILE   = './config.yml';
PROBLEM_DAT  = './prob_tracking.yml';

#loaded config file
CONFIG_SPEC     = None
prob_tracking   = None

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

#emails a random problem, then updates our metadata lib
def sendRandomProblems(n):
    global CONFIG_SPEC
    problem_list = set()
    #get existing config
    # params
    f = open(CONFIGFILE)
    CONFIG_SPEC = yaml.load(f.read())
    f.close()
    # problems to ignore
    f = open(PROBLEM_DAT)
    prob_tracking = yaml.load(f.read())
    f.close()

    #get list of problems in your directories
    for dir in get_immediate_subdirectories(CONFIG_SPEC['problem_directory']):
        for file in os.listdir(dir):
            problem_list.add(dir+'/'+file)
    
    completed_list = set(prob_tracking['sent_problems'])
    problem_list = problem_list - completed_list
    #pick n random problems
    to_send = random.sample(problem_list, n)
    for i in to_send:
        sendProblem(i)
        prob_tracking['sent_problems'].append(i)
    
    prob_tracking['sent_problems']
    f = open(PROBLEM_DAT,'w')
    f.write(yaml.dump(prob_tracking))
    f.close()

#formats given problem and sends it to the user
def sendProblem( prob ):
    global CONFIG_SPEC
    #get extension
    ext = prob.split('.')[-1]
    message=None
    f = open(prob,'rb')
    if ext == 'txt':
        message = MIMEText(f.read())
    elif ext == 'png':
        message = MIMEImage(f.read())
        message.add_header('Content-ID', '<image1>')
    f.close()
    
    prob_name = prob.split('/')[-1].split('.')[0]
    sendemail(CONFIG_SPEC['email'], CONFIG_SPEC['recipients'],# [],
        CONFIG_SPEC['subject'] + ' ' + prob_name, message,
	CONFIG_SPEC['email'], CONFIG_SPEC['pass'])
 
def sendemail(from_addr, to_addr_list,# cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    global CONFIG_SPEC
    msg = MIMEMultipart()
    msg['From']      = from_addr
    msg['To']        = ','.join(to_addr_list)
    msg['Subject']   = '%s' % subject
    msg.preamble = 'This is a multi-part message in MIME format.'

    msg.attach(MIMEText('%s <br> <img src="cid:image1"> <br> Enyoy!' % CONFIG_SPEC['msg_header'], 'html'))
    msg.attach(message)

    server = smtplib.SMTP(smtpserver)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, msg.as_string())
    server.quit()

sendRandomProblems(1)
